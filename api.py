#!/usr/bin/env python3
"""
Script-to-Clip API
==================
FastAPI backend for breaking scripts into segments with clip descriptions.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

from config import Config

app = FastAPI(title="Script-to-Clip API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/generated", StaticFiles(directory="generated_images"), name="generated")


# ============================================================================
# Models
# ============================================================================

class Character(BaseModel):
    id: str
    name: str
    description: str
    visual_archetype: str  # The Authority, The Hero, The Victim, etc.
    ai_prompt_keywords: str
    image_url: Optional[str] = None


class Segment(BaseModel):
    segment_number: int
    script_text: str
    tags_primary: str  # PRODUCT, HERO, UGC, CGI, B-ROLL, TEXT, TESTIMONIAL
    tags_secondary: str  # PROBLEM, SOLUTION, AUTHORITY, EMOTIONAL, URGENCY
    bucket: str  # The Agitation, The UMP, The Hero, The Authority, The Paradise, The Product
    fracture_reason: str
    start_frame_description: Optional[str] = None  # Static image for first frame (for image gen)
    clip_description: str  # Motion/action description (for video gen)
    show_product: bool = False  # Whether product should appear in this segment
    character_id: Optional[str] = None
    generated_image_url: Optional[str] = None


class ScriptBreakdownRequest(BaseModel):
    script: str
    playbook_context: Optional[str] = None  # Additional context/playbook to include


class ScriptBreakdownResponse(BaseModel):
    characters: List[Character]
    segments: List[Segment]
    full_script: str


class GenerateImageRequest(BaseModel):
    segment_number: int
    clip_description: str
    character_id: Optional[str] = None


class GenerateCharacterImageRequest(BaseModel):
    character_id: str
    ai_prompt_keywords: str


class GenerateAllImagesRequest(BaseModel):
    segments: List[Dict[str, Any]]
    characters: List[Dict[str, Any]]
    product_image_base64: Optional[str] = None  # Reference image for product shots as base64


# ============================================================================
# Load Playbooks
# ============================================================================

def load_playbooks() -> str:
    """Load all playbook files."""
    playbook_dir = "prompts/video_editing_prompts"
    playbooks = []

    files_to_load = ["script_to_clip.md", "nutra_ecom.md"]

    for filename in files_to_load:
        filepath = os.path.join(playbook_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                playbooks.append(f"=== {filename} ===\n{f.read()}")

    return "\n\n".join(playbooks)


PLAYBOOKS = load_playbooks()


# ============================================================================
# Script Breakdown Logic
# ============================================================================

def break_script_with_llm(script: str, additional_context: str = None) -> dict:
    """Use Gemini to break script into segments with clip descriptions."""

    if not Config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    model = "gemini-3-pro-preview"

    context = PLAYBOOKS
    if additional_context:
        context += f"\n\n=== ADDITIONAL CONTEXT ===\n{additional_context}"

    prompt = f'''You are an expert direct response video producer. Using the playbooks provided, break the following script into segments.

=== PLAYBOOKS ===
{context}

=== SCRIPT TO BREAK DOWN ===
{script}

=== INSTRUCTIONS ===
1. First, identify all CHARACTERS in the script (narrator, named people, archetypes)
2. Then break the script into segments following the fracture rules from the playbooks
3. For each segment, provide:
   - The exact script text
   - Primary tag (PRODUCT, HERO, UGC, CGI, B-ROLL, TEXT, TESTIMONIAL)
   - Secondary tag (PROBLEM, SOLUTION, AUTHORITY, EMOTIONAL, URGENCY)
   - Bucket (The Agitation, The UMP, The Hero, The Authority, The Paradise, The Product)
   - Fracture reason (why this is its own segment)
   - start_frame_description: What the FIRST FRAME of this video clip looks like (for AI image generation)
   - clip_description: What HAPPENS in this clip - motion and action (for AI video generation with Veo3)
   - Character ID if a specific character appears in this segment
   - show_product: true/false - whether the product should appear in this segment

=== CRITICAL RULES FOR START FRAME & CLIP DESCRIPTIONS ===

1. CONTEXT AWARENESS: Consider what came before and after each segment. The visuals must make logical sense:
   - If someone is "cleaning their fridge", show them AT the fridge, not at a dresser
   - If someone is "putting the product in their fridge", the start frame shows them HOLDING the product near the open fridge
   - Think about physical continuity between segments

2. START FRAME vs CLIP DESCRIPTION:
   - start_frame_description: A STATIC image description - what does frame 1 look like? No motion verbs.
   - clip_description: The ACTION/MOTION - what happens during this 2-4 second clip? Use motion verbs.

   Example for "She puts the device in her fridge":
   - start_frame_description: "Woman holding small white cylindrical device, standing in front of open refrigerator, kitchen setting, soft natural lighting"
   - clip_description: "Woman gently places the device on the top shelf of the refrigerator, closes the door with a satisfied smile"

3. PRODUCT VISIBILITY (show_product = true when):
   - Primary tag is PRODUCT
   - Bucket is "The Product"
   - Any tag mentions the product being shown, demonstrated, or featured
   - The script text explicitly mentions the product/device
   - CGI segments showing the product

4. UGC TAG - DO NOT interpret literally:
   - UGC does NOT mean "person filming with phone camera"
   - UGC means: authentic, relatable, testimonial-style footage
   - Show the PERSON and their EXPERIENCE, not them holding a phone
   - Example: "UGC testimonial about loving the product" = show a real person in their home, talking naturally, maybe holding/showing the product

5. CGI + PRODUCT: When CGI and Product tags appear together, this is a premium product visualization:
   - Floating product, particle effects, sleek 3D render style
   - The start frame MUST prominently feature the product

=== OUTPUT FORMAT (JSON) ===
{{
  "characters": [
    {{
      "id": "char_001",
      "name": "Character Name or Role",
      "description": "Age, role, relationship to product/story",
      "visual_archetype": "The Authority / The Hero / The Victim / etc.",
      "ai_prompt_keywords": "Detailed prompt keywords for generating this character - be specific about age, ethnicity, style, clothing"
    }}
  ],
  "segments": [
    {{
      "segment_number": 1,
      "script_text": "Exact script text for this segment",
      "tags_primary": "B-ROLL",
      "tags_secondary": "PROBLEM",
      "bucket": "The Agitation",
      "fracture_reason": "New noun introduced: device",
      "show_product": false,
      "start_frame_description": "Close-up of open refrigerator interior, various food items visible, slight fog/mist, cool blue lighting",
      "clip_description": "Camera slowly pushes into refrigerator, revealing spoiled food with visible mold spores floating in the air",
      "character_id": null
    }}
  ]
}}

IMPORTANT:
- Every word of the script must appear in exactly one segment
- Follow the fracture rules strictly (noun triggers, list items, action-reaction, pivot words)
- start_frame_description is for IMAGE generation (static, no motion)
- clip_description is for VIDEO generation (includes motion and action)
- show_product must be true whenever the product should be visible in the frame
- Be CONTEXT AWARE - what location/setting makes sense given the script?

OUTPUT ONLY VALID JSON.'''

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            'temperature': 0.3,
            'max_output_tokens': 32768,
        }
    )

    # Parse JSON response
    text = response.text.strip()

    # Remove markdown code fences
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    def try_fix_truncated_json(s):
        """Try to fix JSON that was truncated mid-generation."""
        s = s.strip()

        # Count open brackets/braces to see if truncated
        in_string = False
        escape = False
        brace_depth = 0
        bracket_depth = 0

        for c in s:
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == '{':
                brace_depth += 1
            elif c == '}':
                brace_depth -= 1
            elif c == '[':
                bracket_depth += 1
            elif c == ']':
                bracket_depth -= 1

        # If unbalanced, try to close it
        if brace_depth > 0 or bracket_depth > 0:
            # Find the last complete segment in the segments array
            # Look for the last complete object before truncation
            last_complete = s.rfind('},')
            if last_complete == -1:
                last_complete = s.rfind('}]')

            if last_complete != -1:
                # Truncate to last complete object and close arrays/objects
                s = s[:last_complete+1]
                s += ']}'  # Close segments array and main object

        return s

    def try_parse_json(s):
        """Try to parse JSON, fixing common issues."""
        s = s.strip()
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass

        # Try fixing truncated JSON
        fixed = try_fix_truncated_json(s)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Try to find the outermost JSON object
        start = s.find('{')
        if start == -1:
            return None

        # Find matching closing brace
        depth = 0
        in_string = False
        escape = False
        for i, c in enumerate(s[start:], start):
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i+1])
                    except json.JSONDecodeError:
                        break

        return None

    result = try_parse_json(text)
    if result:
        return result

    # Fallback: try original text
    result = try_parse_json(response.text)
    if result:
        return result

    raise ValueError(f"Failed to parse JSON response from LLM")


# ============================================================================
# Image Generation (Gemini Nana Banana)
# ============================================================================

def generate_image_with_gemini(prompt: str, prefix: str = "image", reference_images_base64: list = None) -> str:
    """
    Generate an image using Gemini 3 Pro Image Preview (Nana Banana).
    Returns the URL path to the generated image.

    Args:
        prompt: The text prompt for image generation
        prefix: Filename prefix
        reference_images_base64: Optional list of base64 encoded images (for product/character shots)
    """
    import base64
    import mimetypes as mt

    client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    model = "gemini-3-pro-image-preview"

    image_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # Build content parts
        parts = []

        # Add reference images first (as base64)
        if reference_images_base64:
            for ref_base64 in reference_images_base64:
                if not ref_base64:
                    continue

                # Decode base64 to bytes
                ref_image_bytes = base64.b64decode(ref_base64)

                # Add image part (assume PNG, works for most images)
                parts.append(types.Part.from_bytes(
                    mime_type='image/png',
                    data=ref_image_bytes,
                ))
                print(f"Using reference image (base64, {len(ref_image_bytes)} bytes)")

        # Add text prompt
        parts.append(types.Part.from_text(text=prompt))

        contents = [
            types.Content(
                role="user",
                parts=parts,
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        )

        generated_file = None

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            part = chunk.candidates[0].content.parts[0]
            if part.inline_data and part.inline_data.data:
                inline_data = part.inline_data
                data_buffer = inline_data.data

                # Decode if base64 encoded
                if isinstance(data_buffer, str):
                    data_buffer = base64.b64decode(data_buffer)
                elif isinstance(data_buffer, bytes):
                    # Check if it's base64 encoded bytes (starts with base64 chars, not PNG header)
                    if not data_buffer[:4] == b'\x89PNG' and not data_buffer[:2] == b'\xff\xd8':
                        try:
                            data_buffer = base64.b64decode(data_buffer)
                        except:
                            pass

                file_extension = mt.guess_extension(inline_data.mime_type) or '.png'
                filename = f"{prefix}_{image_id}_{timestamp}{file_extension}"
                filepath = os.path.join("generated_images", filename)

                with open(filepath, 'wb') as f:
                    f.write(data_buffer)

                # Return both URL and base64 for instant display
                image_base64 = base64.b64encode(data_buffer).decode('utf-8')
                mime_type = inline_data.mime_type or 'image/png'

                print(f"Image generated: {filepath}")
                return {
                    'url': f"/generated/{filename}",
                    'data_url': f"data:{mime_type};base64,{image_base64}"
                }

        return None

    except Exception as e:
        print(f"Image generation error: {e}")
        import traceback
        traceback.print_exc()

    return None


def generate_segment_image(clip_description: str, character_info: dict = None, product_image_base64: str = None, is_product_segment: bool = False) -> str:
    """
    Generate an image for a segment using Gemini.

    Args:
        clip_description: The visual description for the clip
        character_info: Optional dict with 'name', 'ai_prompt_keywords', and 'image_base64' for the character
        product_image_base64: Optional base64 encoded product reference image
        is_product_segment: Whether this segment is tagged as PRODUCT
    """
    # Collect reference images (as base64)
    reference_images_base64 = []

    # Build the prompt
    prompt = f"""Generate a cinematic video frame for a direct response advertisement.

VISUAL DESCRIPTION:
{clip_description}

STRICT REQUIREMENTS:
- Photorealistic, cinematic quality
- 16:9 aspect ratio framing
- Professional lighting
- High production value
- DO NOT include any text, titles, captions, watermarks, or overlays in the image
- DO NOT add any logos, labels, or written words
- Pure visual scene only - no typography of any kind"""

    # Add character reference if provided
    if character_info:
        char_name = character_info.get('name', 'the character')
        char_keywords = character_info.get('ai_prompt_keywords', '')
        char_image_base64 = character_info.get('image_base64')

        prompt += f"\n\nCHARACTER IN THIS SCENE:\nThe person in this scene is {char_name}."
        if char_keywords:
            prompt += f"\n{char_name} appearance: {char_keywords}"

        if char_image_base64:
            prompt += f"\nIMPORTANT: The character {char_name} should look exactly like the reference image provided. Maintain their face, features, and likeness."
            reference_images_base64.append(char_image_base64)

    # Add product reference if this is a product segment
    if is_product_segment and product_image_base64:
        prompt += "\n\nPRODUCT IN THIS SCENE:\nThe product in this image MUST match the reference product image provided. This is the FIRST image attached. Keep the product's exact design, shape, color, and appearance consistent with that reference."
        reference_images_base64.insert(0, product_image_base64)  # Insert at beginning so it's the first image
        print(f"[DEBUG] Adding product image to reference_images_base64 (length: {len(product_image_base64)} chars)")

    print(f"[DEBUG] generate_segment_image: is_product={is_product_segment}, has_product_b64={bool(product_image_base64)}, num_refs={len(reference_images_base64)}")

    result = generate_image_with_gemini(prompt, prefix="segment", reference_images_base64=reference_images_base64 if reference_images_base64 else None)

    if result:
        return result

    # Fallback placeholder if generation fails
    image_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    placeholder_path = f"generated_images/segment_{image_id}_{timestamp}_error.txt"
    with open(placeholder_path, 'w') as f:
        f.write(f"IMAGE GENERATION FAILED\n")
        f.write(f"Prompt: {clip_description}\n")
    return f"/generated/segment_{image_id}_{timestamp}_error.txt"


def generate_character_image(ai_prompt_keywords: str) -> str:
    """
    Generate an image for a character using Gemini.
    """
    prompt = f"""Generate a character portrait for a video advertisement.

CHARACTER DESCRIPTION:
{ai_prompt_keywords}

REQUIREMENTS:
- Photorealistic portrait
- Professional headshot style
- Neutral background
- Good lighting on face
- 16:9 aspect ratio
- Suitable as a character reference for video production"""

    result = generate_image_with_gemini(prompt, prefix="character")

    if result:
        return result

    # Fallback placeholder if generation fails
    image_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    placeholder_path = f"generated_images/character_{image_id}_{timestamp}_error.txt"
    with open(placeholder_path, 'w') as f:
        f.write(f"CHARACTER IMAGE GENERATION FAILED\n")
        f.write(f"Prompt: {ai_prompt_keywords}\n")
    return f"/generated/character_{image_id}_{timestamp}_error.txt"


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {"message": "Script-to-Clip API", "version": "1.0.0"}


@app.post("/api/breakdown", response_model=ScriptBreakdownResponse)
async def breakdown_script(request: ScriptBreakdownRequest):
    """Break a script into segments with clip descriptions."""
    try:
        result = break_script_with_llm(request.script, request.playbook_context)

        characters = [
            Character(
                id=c.get('id', f"char_{i}"),
                name=c.get('name', 'Unknown'),
                description=c.get('description', ''),
                visual_archetype=c.get('visual_archetype', ''),
                ai_prompt_keywords=c.get('ai_prompt_keywords', ''),
                image_url=c.get('image_url')
            )
            for i, c in enumerate(result.get('characters', []))
        ]

        segments = [
            Segment(
                segment_number=s.get('segment_number', i + 1),
                script_text=s.get('script_text', ''),
                tags_primary=s.get('tags_primary', ''),
                tags_secondary=s.get('tags_secondary', ''),
                bucket=s.get('bucket', ''),
                fracture_reason=s.get('fracture_reason', ''),
                start_frame_description=s.get('start_frame_description', s.get('clip_description', '')),
                clip_description=s.get('clip_description', ''),
                show_product=s.get('show_product', False),
                character_id=s.get('character_id'),
                generated_image_url=s.get('generated_image_url')
            )
            for i, s in enumerate(result.get('segments', []))
        ]

        return ScriptBreakdownResponse(
            characters=characters,
            segments=segments,
            full_script=request.script
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-segment-image")
async def generate_image_for_segment(request: GenerateImageRequest):
    """Generate an image for a specific segment."""
    try:
        # character_id here is actually character_info for backwards compat
        # If it's a string, treat as legacy behavior (no character info)
        character_info = None
        if request.character_id and isinstance(request.character_id, dict):
            character_info = request.character_id
        image_url = generate_segment_image(
            request.clip_description,
            character_info
        )
        return {"image_url": image_url, "segment_number": request.segment_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-character-image")
async def generate_image_for_character(request: GenerateCharacterImageRequest):
    """Generate an image for a character."""
    try:
        result = generate_character_image(request.ai_prompt_keywords)
        if result and isinstance(result, dict):
            return {
                "image_url": result['url'],
                "image_data_url": result['data_url'],  # For instant display
                "character_id": request.character_id
            }
        return {"image_url": result, "character_id": request.character_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-all-images")
async def generate_all_segment_images(request: GenerateAllImagesRequest):
    """Generate images for all segments in parallel."""
    try:
        # Build character lookup by ID
        character_lookup = {c['id']: c for c in request.characters}
        product_image_base64 = request.product_image_base64
        print(f"[DEBUG] Product image base64 received: {bool(product_image_base64)} ({len(product_image_base64) if product_image_base64 else 0} chars)")

        def generate_for_segment(segment: dict) -> dict:
            """Generate image for a single segment."""
            segment_num = segment.get('segment_number', 0)
            # Use start_frame_description for image gen, fall back to clip_description
            start_frame_desc = segment.get('start_frame_description') or segment.get('clip_description', '')
            char_id = segment.get('character_id')

            # Use show_product field directly, or fall back to checking tags
            show_product = segment.get('show_product', False)
            if not show_product:
                # Legacy fallback: check all tags for "product"
                tags_primary = segment.get('tags_primary', '').upper()
                tags_secondary = segment.get('tags_secondary', '').upper()
                bucket = segment.get('bucket', '').upper()
                all_tags = f"{tags_primary} {tags_secondary} {bucket}"
                show_product = 'PRODUCT' in all_tags

            # Get character info if segment has a character
            character_info = None
            if char_id and char_id in character_lookup:
                char = character_lookup[char_id]
                character_info = {
                    'name': char.get('name', 'the character'),
                    'ai_prompt_keywords': char.get('ai_prompt_keywords', ''),
                    'image_base64': char.get('image_base64')  # Include character reference image as base64
                }

            print(f"[DEBUG] Segment {segment_num}: show_product={show_product}, has_product_base64={bool(product_image_base64)}")

            try:
                result = generate_segment_image(
                    start_frame_desc,
                    character_info,
                    product_image_base64=product_image_base64 if show_product else None,
                    is_product_segment=show_product
                )
                if result and isinstance(result, dict):
                    return {
                        'segment_number': segment_num,
                        'image_url': result['url'],
                        'image_data_url': result['data_url'],  # For instant display
                        'success': True
                    }
                return {
                    'segment_number': segment_num,
                    'image_url': result,
                    'success': True
                }
            except Exception as e:
                return {
                    'segment_number': segment_num,
                    'image_url': None,
                    'success': False,
                    'error': str(e)
                }

        # Process all segments in parallel
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(generate_for_segment, seg): seg
                for seg in request.segments
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # Sort by segment number for consistent ordering
        results.sort(key=lambda x: x['segment_number'])

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateSingleSegmentImageRequest(BaseModel):
    segment_number: int
    start_frame_description: str
    show_product: bool = False
    character: Optional[Dict[str, Any]] = None
    product_image_base64: Optional[str] = None


@app.post("/api/generate-single-segment-image")
async def generate_single_segment_image(request: GenerateSingleSegmentImageRequest):
    """Generate an image for a single segment with editable description."""
    try:
        character_info = None
        if request.character:
            character_info = {
                'name': request.character.get('name', 'the character'),
                'ai_prompt_keywords': request.character.get('ai_prompt_keywords', ''),
                'image_base64': request.character.get('image_base64')
            }

        result = generate_segment_image(
            request.start_frame_description,
            character_info,
            product_image_base64=request.product_image_base64 if request.show_product else None,
            is_product_segment=request.show_product
        )

        if result and isinstance(result, dict):
            return {
                'segment_number': request.segment_number,
                'image_url': result['url'],
                'image_data_url': result['data_url'],
                'success': True
            }
        return {
            'segment_number': request.segment_number,
            'image_url': result,
            'success': True
        }
    except Exception as e:
        return {
            'segment_number': request.segment_number,
            'image_url': None,
            'success': False,
            'error': str(e)
        }


@app.post("/api/upload-character-image/{character_id}")
async def upload_character_image(character_id: str, file: UploadFile = File(...)):
    """Upload an image for a character."""
    try:
        # Save uploaded file
        file_ext = os.path.splitext(file.filename)[1] or '.png'
        filename = f"character_{character_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        filepath = os.path.join("uploads", filename)

        with open(filepath, 'wb') as f:
            content = await file.read()
            f.write(content)

        return {"image_url": f"/uploads/{filename}", "character_id": character_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-product-image")
async def upload_product_image(file: UploadFile = File(...)):
    """Upload a product reference image."""
    try:
        # Save uploaded file
        file_ext = os.path.splitext(file.filename)[1] or '.png'
        filename = f"product_{uuid.uuid4().hex[:8]}{file_ext}"
        filepath = os.path.join("uploads", filename)

        with open(filepath, 'wb') as f:
            content = await file.read()
            f.write(content)

        return {"image_url": f"/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RerollDescriptionRequest(BaseModel):
    segment_number: int
    type: str  # 'start_frame' or 'clip'
    script_text: str
    tags_primary: str
    tags_secondary: str
    bucket: str
    current_start_frame: Optional[str] = None
    current_clip: Optional[str] = None
    full_script: str


@app.post("/api/reroll-description")
async def reroll_description(request: RerollDescriptionRequest):
    """Regenerate a start_frame or clip description using Gemini."""
    try:
        client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        model = "gemini-3-pro-preview"

        if request.type == 'start_frame':
            prompt = f'''You are an expert visual director for direct response video ads.

Generate a NEW start frame description for this segment. The start frame is a STATIC image - the very first frame of a video clip.

=== CONTEXT ===
Full Script: {request.full_script[:500]}...

Segment Script: "{request.script_text}"
Tags: {request.tags_primary} / {request.tags_secondary}
Bucket: {request.bucket}

Current clip description (for reference): {request.current_clip or 'None'}

=== PREVIOUS START FRAME (generate something DIFFERENT) ===
{request.current_start_frame or 'None'}

=== REQUIREMENTS ===
- Describe a STATIC image (no motion verbs)
- Include: subject, setting, lighting, camera angle, mood
- Be specific and visual
- Make it different from the previous version
- Keep it to 1-2 sentences

Output ONLY the new start frame description, nothing else.'''
        else:
            prompt = f'''You are an expert visual director for direct response video ads.

Generate a NEW clip description for this segment. The clip description describes the MOTION and ACTION that happens during a 4-6 second video clip.

=== CONTEXT ===
Full Script: {request.full_script[:500]}...

Segment Script: "{request.script_text}"
Tags: {request.tags_primary} / {request.tags_secondary}
Bucket: {request.bucket}

Current start frame (for reference): {request.current_start_frame or 'None'}

=== PREVIOUS CLIP DESCRIPTION (generate something DIFFERENT) ===
{request.current_clip or 'None'}

=== REQUIREMENTS ===
- Describe MOTION and ACTION (use motion verbs)
- Include: what moves, how it moves, camera movement if any
- Be specific about the temporal flow (what happens from start to end)
- Make it different from the previous version
- Keep it to 1-2 sentences

Output ONLY the new clip description, nothing else.'''

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                'temperature': 0.9,  # Higher temperature for more variety
                'max_output_tokens': 300,
            }
        )

        result = response.text.strip()
        # Remove quotes if present
        if result.startswith('"') and result.endswith('"'):
            result = result[1:-1]

        if request.type == 'start_frame':
            return {"start_frame_description": result, "segment_number": request.segment_number}
        else:
            return {"clip_description": result, "segment_number": request.segment_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EnhanceVideoPromptRequest(BaseModel):
    segment_number: int
    clip_description: str
    start_frame_description: Optional[str] = None
    script_text: str
    tags_primary: str
    tags_secondary: str
    bucket: str
    full_script: str


class GenerateVideoRequest(BaseModel):
    segment_number: int
    prompt: str
    start_image_base64: Optional[str] = None
    project_name: str = "Project"


# Store for tracking video generation operations
video_operations = {}


@app.post("/api/enhance-video-prompt")
async def enhance_video_prompt(request: EnhanceVideoPromptRequest):
    """Use Gemini to enhance a video prompt for Veo 3.1."""
    try:
        client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        model = "gemini-3-pro-preview"

        prompt = f'''You are an expert video prompt engineer for Veo 3.1, Google's AI video generation model.

Your task is to enhance a video clip description into an optimal prompt for Veo 3.1 video generation.

=== CONTEXT ===
Full Script: {request.full_script[:500]}...

Current Segment Script: "{request.script_text}"
Segment Tags: {request.tags_primary} / {request.tags_secondary}
Bucket: {request.bucket}

=== ORIGINAL DESCRIPTIONS ===
Start Frame: {request.start_frame_description or 'Not provided'}
Clip Description: {request.clip_description}

=== VEO 3.1 PROMPT GUIDELINES ===
1. Be specific about camera movement (pan, tilt, dolly, zoom, static, handheld)
2. Describe lighting conditions (natural, studio, golden hour, dramatic shadows)
3. Include the action/motion that happens during the clip
4. Specify the mood/tone (cinematic, documentary, commercial, intimate)
5. Keep it to 2-3 sentences max - Veo works best with concise prompts
6. Focus on MOTION - what moves, how it moves, camera movement
7. Include temporal flow - what happens from start to end of the clip

=== IMPORTANT ===
- This is for a direct response advertisement
- The clip should be 4-6 seconds long
- Make it visually engaging and professional
- Do NOT include any text overlays or captions in the video
- If this is a PRODUCT segment, ensure the product is prominently featured

Output ONLY the enhanced prompt, nothing else. No explanations, no quotes, just the prompt text.'''

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                'temperature': 0.7,
                'max_output_tokens': 500,
            }
        )

        enhanced = response.text.strip()
        # Remove any quotes if present
        if enhanced.startswith('"') and enhanced.endswith('"'):
            enhanced = enhanced[1:-1]

        return {"enhanced_prompt": enhanced, "segment_number": request.segment_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-video")
async def generate_video(request: GenerateVideoRequest):
    """Start video generation with Veo 3.1 Fast."""
    import base64
    import time as time_module

    try:
        # Debug: Log the prompt being sent
        print(f"[VIDEO GEN] Segment {request.segment_number}")
        print(f"[VIDEO GEN] Prompt: {request.prompt}")
        print(f"[VIDEO GEN] Has start image: {bool(request.start_image_base64)}")

        # Use Vertex AI client for video generation
        client = genai.Client(
            vertexai=True,
            project=Config.VERTEX_PROJECT_ID,
            location=Config.VERTEX_LOCATION
        )
        video_model = "veo-3.1-fast-generate-001"

        # Build the generation config
        # Note: enhance_prompt=False to use the exact prompt provided
        config = types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=6,
            resolution="720p",
            person_generation="allow_adult",
            enhance_prompt=False,  # Use exact prompt, don't let Veo rewrite it
            generate_audio=True,
        )

        # Generate with or without starting image
        if request.start_image_base64:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(request.start_image_base64)

            # Save temp image file
            temp_image_path = f"generated_images/temp_start_{request.segment_number}_{uuid.uuid4().hex[:8]}.png"
            with open(temp_image_path, 'wb') as f:
                f.write(image_bytes)

            operation = client.models.generate_videos(
                model=video_model,
                prompt=request.prompt,
                image=types.Image.from_file(location=temp_image_path),
                config=config,
            )
        else:
            operation = client.models.generate_videos(
                model=video_model,
                prompt=request.prompt,
                config=config,
            )

        # Store operation for polling
        operation_id = str(uuid.uuid4())
        video_operations[operation_id] = {
            'operation': operation,
            'segment_number': request.segment_number,
            'project_name': request.project_name,
            'started_at': datetime.now().isoformat(),
        }

        return {"operation_id": operation_id, "segment_number": request.segment_number}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "segment_number": request.segment_number}


@app.get("/api/video-status/{operation_id}")
async def get_video_status(operation_id: str):
    """Check the status of a video generation operation."""
    import base64

    if operation_id not in video_operations:
        return {"error": "Operation not found", "done": True}

    op_data = video_operations[operation_id]
    operation = op_data['operation']
    segment_number = op_data['segment_number']
    project_name = op_data['project_name']

    try:
        # Use Vertex AI client for video operations
        client = genai.Client(
            vertexai=True,
            project=Config.VERTEX_PROJECT_ID,
            location=Config.VERTEX_LOCATION
        )

        # Check if operation is done (done can be None, so check explicitly)
        if not operation.done:
            # Refresh operation status by passing the operation object directly
            operation = client.operations.get(operation)
            op_data['operation'] = operation

        if operation.done:
            if operation.result and operation.result.generated_videos:
                video_bytes = operation.result.generated_videos[0].video.video_bytes

                # Save video file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_project_name = project_name.replace(' ', '_').replace('/', '_')
                filename = f"{safe_project_name}_segment{segment_number}_{timestamp}.mp4"
                filepath = os.path.join("generated_images", filename)

                with open(filepath, 'wb') as f:
                    f.write(video_bytes)

                # Clean up operation from memory
                del video_operations[operation_id]

                return {
                    "done": True,
                    "video_url": f"/generated/{filename}",
                    "filename": filename,
                    "segment_number": segment_number
                }
            else:
                # Operation done but no video
                error_msg = str(operation.error) if operation.error else "Video generation completed but no video was returned"
                del video_operations[operation_id]
                return {
                    "done": True,
                    "error": error_msg,
                    "segment_number": segment_number
                }
        else:
            return {
                "done": False,
                "segment_number": segment_number
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"done": True, "error": str(e), "segment_number": segment_number}


@app.get("/api/playbooks")
async def get_playbooks():
    """Get available playbooks."""
    return {"playbooks": PLAYBOOKS}


# Serve frontend
@app.get("/app")
async def serve_frontend():
    return FileResponse("frontend/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
