import json
import os
import base64
import sys
from google import genai
from google.genai import types
from typing import Dict, Any, Optional, List
from config import Config

class GeminiAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.slideshow_context = {}  # Store context between batch calls
    
    def analyze_video(self, video_path: str, metadata: Dict[str, Any], transcript: str) -> Dict[str, Any]:
        """Analyze video using Gemini 2.0 Flash and return structured analysis"""
        try:
            print(f"Analyzing video: {video_path}")
            
            # Read video file as bytes
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
            
            # Check file size (20MB limit for inline data)
            file_size_mb = len(video_bytes) / (1024 * 1024)
            print(f"Video file size: {file_size_mb:.2f} MB")
            
            if file_size_mb > 20:
                raise Exception(f"Video file too large ({file_size_mb:.2f} MB). Must be under 20MB for inline processing.")
            
            # Get the analysis prompt
            prompt = Config.get_analysis_prompt()
            
            print("Sending request to Gemini with inline video data...")
            # Generate analysis using inline data method with the correct API format
            # Use new API format
            contents = [types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(
                        mime_type="video/mp4",
                        data=video_bytes
                    ),
                    types.Part.from_text(text=prompt)
                ]
            )]
            
            response_stream = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents
            )
            
            # Collect response text
            response_text = ""
            for chunk in response_stream:
                if chunk.text:
                    response_text += chunk.text
            
            print("Received response from Gemini")
            
            # Parse JSON response with robust error handling
            try:
                response_text = response_text.strip()
                print(f"Raw response length: {len(response_text)} characters")
                
                # Multiple attempts to clean and parse the JSON
                analysis_data = None
                
                # Attempt 1: Clean markdown code blocks
                clean_text = response_text
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.startswith('```'):
                    clean_text = clean_text[3:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                try:
                    analysis_data = json.loads(clean_text)
                    print("✅ Successfully parsed JSON (attempt 1)")
                except json.JSONDecodeError:
                    pass
                
                # Attempt 2: Find JSON block with regex
                if analysis_data is None:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            analysis_data = json.loads(json_match.group())
                            print("✅ Successfully parsed JSON (attempt 2 - regex)")
                        except json.JSONDecodeError:
                            pass
                
                # Attempt 3: Try to find and extract just the JSON content
                if analysis_data is None:
                    lines = response_text.split('\n')
                    json_lines = []
                    in_json = False
                    brace_count = 0
                    
                    for line in lines:
                        if '{' in line and not in_json:
                            in_json = True
                            brace_count += line.count('{') - line.count('}')
                            json_lines.append(line)
                        elif in_json:
                            brace_count += line.count('{') - line.count('}')
                            json_lines.append(line)
                            if brace_count <= 0:
                                break
                    
                    if json_lines:
                        try:
                            json_text = '\n'.join(json_lines)
                            analysis_data = json.loads(json_text)
                            print("✅ Successfully parsed JSON (attempt 3 - line parsing)")
                        except json.JSONDecodeError:
                            pass
                
                if analysis_data is None:
                    raise json.JSONDecodeError("Could not parse JSON after multiple attempts", response_text, 0)
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error after all attempts: {e}")
                print(f"Response text (first 1000 chars): {response.text[:1000]}...")
                
                # Enhanced fallback: create structured data from any available info
                analysis_data = {
                    "video_metadata": {
                        "video_id": metadata.get('video_id', 'unknown'),
                        "platform": metadata.get('platform', 'unknown'),
                        "url": metadata.get('url', ''),
                        "upload_date": metadata.get('upload_date'),
                        "ingestion_date": metadata.get('ingestion_date'),
                        "duration_seconds": metadata.get('duration_seconds', 0),
                        "resolution": "unknown",
                        "aspect_ratio": "unknown"
                    },
                    "creator_profile": {
                        "creator_id": metadata.get('creator_username', 'unknown'),
                        "username": metadata.get('creator_username', 'unknown'),
                        "demographics": {
                            "apparent_age_range": "unknown",
                            "apparent_gender": "unknown",
                            "apparent_ethnicity": "unknown",
                            "attractiveness_score": 0.0
                        },
                        "apparel": {
                            "clothing_style": "unknown",
                            "visible_brands": [],
                            "formality_level": "unknown",
                            "color_palette": []
                        },
                        "on_screen_presence": {
                            "confidence_level": "unknown",
                            "energy_level": "unknown",
                            "authenticity_score": 0.0
                        }
                    },
                    "hook_analysis": {
                        "duration_seconds": 0.0,
                        "hook_type": "unknown",
                        "promise_statement": "unknown",
                        "emotional_triggers": [],
                        "target_audience": {
                            "primary_demographic": "unknown",
                            "psychographic_profile": "unknown",
                            "pain_points_addressed": []
                        },
                        "visual_elements": {
                            "face_visible": False,
                            "facial_expression": "unknown",
                            "text_overlays": [],
                            "motion_intensity": "unknown",
                            "visual_complexity": "unknown",
                            "attention_anchors": []
                        },
                        "audio_elements": {
                            "opening_words": "unknown",
                            "vocal_delivery": "unknown",
                            "audio_hook_pattern": "unknown"
                        }
                    },
                    "content_classification": {
                        "primary_vertical": "unknown",
                        "secondary_verticals": [],
                        "content_purpose": "unknown",
                        "tone": [],
                        "content_tags": [],
                        "educational_entertainment_ratio": 0.0
                    },
                    "raw_response": response.text,
                    "error": f"JSON parsing failed: {str(e)}"
                }
            
            return analysis_data
            
        except Exception as e:
            print(f"Error in analyze_video: {str(e)}")
            raise Exception(f"Failed to analyze video with Gemini: {str(e)}")
    
    def generate_embeddings(self, text: str) -> list:
        """Generate embeddings for text using Gemini"""
        try:
            if not text or not text.strip():
                print("Warning: Empty text provided for embeddings")
                return [0.0] * 512  # Return 512-dimensional zero vector for database compatibility
            
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text.strip()
            )
            
            # text-embedding-004 returns 768-dimensional vectors, but our DB expects 512
            # We'll truncate to 512 dimensions for now
            embedding = result['embedding']
            return embedding[:512] if len(embedding) > 512 else embedding + [0.0] * (512 - len(embedding))
            
        except Exception as e:
            print(f"Warning: Failed to generate embeddings: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 512
    
    def create_combined_text(self, metadata: Dict[str, Any], transcript: str, analysis: Dict[str, Any]) -> str:
        """Create combined text for embedding generation"""
        parts = []
        
        # Add title and description
        if metadata.get('title'):
            parts.append(f"Title: {metadata['title']}")
        if metadata.get('description'):
            parts.append(f"Description: {metadata['description'][:500]}")
        
        # Add transcript
        if transcript:
            parts.append(f"Transcript: {transcript[:1000]}")
        
        # Add key analysis points
        content_class = analysis.get('content_classification', {})
        if content_class.get('primary_vertical'):
            parts.append(f"Category: {content_class['primary_vertical']}")
        
        hook_analysis = analysis.get('hook_analysis', {})
        if hook_analysis.get('hook_type'):
            parts.append(f"Hook type: {hook_analysis['hook_type']}")
        
        return " ".join(parts)
    
    def extract_visual_text(self, analysis: Dict[str, Any]) -> str:
        """Extract visual elements text for embedding"""
        visual_parts = []
        
        # Extract from hook analysis visual elements
        hook_visual = analysis.get('hook_analysis', {}).get('visual_elements', {})
        if hook_visual.get('attention_anchors'):
            visual_parts.append(f"Visual anchors: {', '.join(hook_visual['attention_anchors'])}")
        if hook_visual.get('text_overlays'):
            visual_parts.append(f"Text overlays: {', '.join(hook_visual['text_overlays'])}")
        
        # Extract from visual analysis
        visual_analysis = analysis.get('visual_analysis', {})
        if visual_analysis.get('color_psychology', {}).get('dominant_colors'):
            visual_parts.append(f"Colors: {', '.join(visual_analysis['color_psychology']['dominant_colors'])}")
        
        return " ".join(visual_parts)
    
    def analyze_slideshow(self, image_paths: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complete slideshow using multi-batch approach with context preservation"""
        try:
            print(f"🖼️  Analyzing slideshow with {len(image_paths)} images")
            
            # Initialize slideshow context
            video_id = metadata.get('video_id', 'unknown')
            self.slideshow_context[video_id] = {
                'total_slides': len(image_paths),
                'batches_completed': 0,
                'all_slides_data': [],
                'narrative_context': {}
            }
            
            # Process images in batches of 3
            batch_size = 3
            all_batch_results = []
            
            for i in range(0, len(image_paths), batch_size):
                batch_images = image_paths[i:i+batch_size]
                batch_number = (i // batch_size) + 1
                start_slide = i + 1
                end_slide = min(i + batch_size, len(image_paths))
                
                print(f"   📸 Processing batch {batch_number}: slides {start_slide}-{end_slide}")
                
                batch_result = self._analyze_slide_batch(
                    batch_images, 
                    batch_number, 
                    start_slide, 
                    end_slide,
                    len(image_paths),
                    video_id
                )
                
                if batch_result:
                    all_batch_results.append(batch_result)
                    # Update context for next batch
                    self._update_slideshow_context(video_id, batch_result)
                else:
                    print(f"   ⚠️  Batch {batch_number} analysis failed")
            
            # Final comprehensive analysis
            print("   🎯 Performing final comprehensive slideshow analysis...")
            final_analysis = self._final_slideshow_analysis(video_id, metadata, all_batch_results)
            
            # Cleanup context
            if video_id in self.slideshow_context:
                del self.slideshow_context[video_id]
            
            return final_analysis
            
        except Exception as e:
            print(f"❌ Error in analyze_slideshow: {str(e)}")
            raise Exception(f"Failed to analyze slideshow with Gemini: {str(e)}")
    
    def _analyze_slide_batch(self, image_paths: List[str], batch_number: int, 
                            start_slide: int, end_slide: int, total_slides: int, 
                            video_id: str) -> Optional[Dict[str, Any]]:
        """Analyze a batch of slideshow images (up to 3 images)"""
        try:
            # Load slide analysis prompt
            slide_prompt = self._load_slide_analysis_prompt()
            
            # Get previous context for this slideshow
            context = self.slideshow_context.get(video_id, {})
            previous_context = context.get('narrative_context', {})
            
            # Format prompt with context
            try:
                formatted_prompt = slide_prompt.format(
                    previous_slides_context=json.dumps(previous_context, indent=2) if previous_context else "No previous context - this is the first batch",
                    start_slide_number=start_slide,
                    end_slide_number=end_slide,
                    total_slides=total_slides
                )
                print(f"      📝 Prompt formatted successfully for batch {batch_number}")
            except Exception as format_error:
                print(f"      ❌ Prompt formatting failed for batch {batch_number}: {format_error}")
                raise Exception(f"Prompt formatting error: {format_error}")
            
            # Prepare content parts for new API
            content_parts = []
            
            # Add all images in the batch
            for image_path in image_paths:
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    
                    content_parts.append(
                        types.Part.from_bytes(
                            mime_type="image/jpeg",
                            data=image_data
                        )
                    )
                else:
                    print(f"   ⚠️  Image not found: {image_path}")
            
            # Add prompt text
            content_parts.append(types.Part.from_text(text=formatted_prompt))
            
            # Create content structure
            contents = [types.Content(role="user", parts=content_parts)]
            
            # Generate analysis
            print(f"      🧠 Analyzing batch {batch_number} with Gemini...")
            response_stream = self.client.models.generate_content_stream(
                model="gemini-2.5-pro",
                contents=contents
            )
            
            # Collect response text
            response_text = ""
            for chunk in response_stream:
                if chunk.text:
                    response_text += chunk.text
            
            print(f"      ✅ Received response for batch {batch_number}")
            
            # Parse JSON response
            batch_analysis = self._parse_json_response(response_text, f"batch {batch_number}")
            
            return batch_analysis
            
        except Exception as e:
            print(f"      ❌ Error analyzing batch {batch_number}: {str(e)}")
            return None
    
    def _final_slideshow_analysis(self, video_id: str, metadata: Dict[str, Any], 
                                 batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform final comprehensive slideshow analysis using all batch data"""
        try:
            # Load final slideshow prompt
            final_prompt = self._load_final_slideshow_prompt()
            
            # Extract and preserve hook-specific pain points before they get aggregated
            hook_pain_points = self._extract_hook_pain_points_from_batches(batch_results)
            print(f"      📌 Extracted {len(hook_pain_points)} hook-specific pain points to preserve")
            
            # Compile all slides data
            all_slides_data = []
            for batch_result in batch_results:
                if batch_result and 'individual_slides' in batch_result:
                    all_slides_data.extend(batch_result['individual_slides'])
            
            # Prepare slideshow metadata
            slideshow_metadata = {
                'video_id': metadata.get('video_id', ''),
                'platform': metadata.get('platform', ''),
                'url': metadata.get('url', ''),
                'upload_date': metadata.get('upload_date', ''),
                'ingestion_date': metadata.get('ingestion_date', ''),
                'total_slides': len(all_slides_data),
                'estimated_display_duration': len(all_slides_data) * 3.0,  # 3 seconds per slide estimate
                'aspect_ratio': 'vertical',  # TikTok/Instagram default
                'slide_format': 'portrait'
            }
            
            # Format final prompt
            try:
                formatted_prompt = final_prompt.format(
                    all_slides_data=json.dumps(batch_results, indent=2),
                    slideshow_metadata=json.dumps(slideshow_metadata, indent=2)
                )
                print(f"      📝 Final prompt formatted successfully")
            except Exception as format_error:
                print(f"      ❌ Final prompt formatting failed: {format_error}")
                raise Exception(f"Final prompt formatting error: {format_error}")
            
            # Use text-only analysis for final comprehensive analysis
            print("      🎯 Generating final comprehensive analysis...")
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=formatted_prompt)]
            )]
            
            response_stream = self.client.models.generate_content_stream(
                model="gemini-2.5-pro",
                contents=contents
            )
            
            # Collect response text
            response_text = ""
            for chunk in response_stream:
                if chunk.text:
                    response_text += chunk.text
            
            final_analysis = self._parse_json_response(response_text, "final analysis")
            
            # Add preserved hook pain points to the final analysis
            if hook_pain_points:
                final_analysis['hook_specific_pain_points'] = hook_pain_points
                print(f"      💾 Added {len(hook_pain_points)} hook-specific pain points to final analysis")
            
            print("      ✅ Final slideshow analysis complete")
            return final_analysis
            
        except Exception as e:
            print(f"      ❌ Error in final slideshow analysis: {str(e)}")
            # Return basic structure with error
            return self._create_fallback_slideshow_analysis(metadata, str(e))
    
    def _extract_hook_pain_points_from_batches(self, batch_results: List[Dict[str, Any]]) -> List[str]:
        """Extract hook-specific pain points from batch results before they get aggregated"""
        hook_pain_points = []
        
        try:
            for batch_result in batch_results:
                if not batch_result:
                    continue
                
                # Check slideshow_hook_analysis.pain_point_analysis
                if 'slideshow_hook_analysis' in batch_result:
                    hook_analysis = batch_result['slideshow_hook_analysis']
                    if 'pain_point_analysis' in hook_analysis:
                        pain_analysis = hook_analysis['pain_point_analysis']
                        
                        # Extract pain_points_addressed
                        if 'pain_points_addressed' in pain_analysis:
                            pain_points = pain_analysis['pain_points_addressed']
                            if isinstance(pain_points, list):
                                hook_pain_points.extend(pain_points)
                            elif isinstance(pain_points, str) and pain_points.strip():
                                hook_pain_points.append(pain_points.strip())
                        
                        # Extract primary_pain_point
                        if 'primary_pain_point' in pain_analysis:
                            primary_pain = pain_analysis['primary_pain_point']
                            if primary_pain and primary_pain.strip():
                                hook_pain_points.append(primary_pain.strip())
                
                # Also check any hook-related analysis in individual slides from first slide
                if 'individual_slides' in batch_result:
                    slides = batch_result['individual_slides']
                    if slides and len(slides) > 0:
                        first_slide = slides[0]
                        if 'slide_number' in first_slide and first_slide['slide_number'] == 1:
                            # Check if first slide has hook-specific pain point analysis
                            if 'pain_point_indicators' in first_slide:
                                pain_indicators = first_slide['pain_point_indicators']
                                if 'pain_points_present' in pain_indicators:
                                    pain_points = pain_indicators['pain_points_present']
                                    if isinstance(pain_points, list):
                                        hook_pain_points.extend(pain_points)
                                    elif isinstance(pain_points, str) and pain_points.strip():
                                        hook_pain_points.append(pain_points.strip())
            
            # Remove duplicates and empty strings
            hook_pain_points = list(set([pp.strip() for pp in hook_pain_points if pp and pp.strip()]))
            
        except Exception as e:
            print(f"      ⚠️  Error extracting hook pain points: {str(e)}")
        
        return hook_pain_points
    
    def _update_slideshow_context(self, video_id: str, batch_result: Dict[str, Any]):
        """Update slideshow context with latest batch results"""
        if video_id not in self.slideshow_context:
            return
        
        context = self.slideshow_context[video_id]
        context['batches_completed'] += 1
        
        # Extract context for next batch from current batch
        if 'context_for_next_batch' in batch_result:
            context['narrative_context'] = batch_result['context_for_next_batch']
        
        # Store individual slides data
        if 'individual_slides' in batch_result:
            context['all_slides_data'].extend(batch_result['individual_slides'])
    
    def _load_slide_analysis_prompt(self) -> str:
        """Load the slide analysis prompt template"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'config_files/slide_analysis_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Could not load slide analysis prompt: {e}")
            return self._get_default_slide_prompt()
    
    def _load_final_slideshow_prompt(self) -> str:
        """Load the final slideshow analysis prompt template"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'config_files/final_slideshow_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Could not load final slideshow prompt: {e}")
            return self._get_default_final_prompt()
    
    def _parse_json_response(self, response_text: str, context: str = "") -> Dict[str, Any]:
        """Parse JSON response with robust error handling"""
        try:
            print(f"      📄 Parsing response for {context} ({len(response_text)} chars)")
            
            # Clean response text
            clean_text = response_text.strip()
            
            # Remove markdown code blocks
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            elif clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Attempt 1: Direct JSON parsing
            try:
                parsed_json = json.loads(clean_text)
                print(f"      ✅ JSON parsed successfully for {context}")
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"      ⚠️  Direct JSON parsing failed for {context}: {str(e)[:100]}")
            
            # Attempt 2: Find JSON block with regex
            import re
            json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
            json_matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            for i, json_match in enumerate(json_matches):
                try:
                    parsed_json = json.loads(json_match)
                    print(f"      ✅ JSON parsed with regex (match {i+1}) for {context}")
                    return parsed_json
                except json.JSONDecodeError:
                    continue
            
            # Attempt 3: Extract JSON manually by finding balanced braces
            brace_count = 0
            start_idx = response_text.find('{')
            if start_idx == -1:
                raise json.JSONDecodeError("No opening brace found", response_text, 0)
            
            for i in range(start_idx, len(response_text)):
                if response_text[i] == '{':
                    brace_count += 1
                elif response_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_text = response_text[start_idx:i+1]
                        try:
                            parsed_json = json.loads(json_text)
                            print(f"      ✅ JSON parsed with manual extraction for {context}")
                            return parsed_json
                        except json.JSONDecodeError:
                            break
            
            raise json.JSONDecodeError("All JSON parsing attempts failed", response_text, 0)
                
        except Exception as e:
            print(f"      ❌ All JSON parsing failed for {context}: {str(e)}")
            print(f"      📝 Raw response preview (first 200 chars):")
            print(f"         {repr(response_text[:200])}")
            print(f"      📝 Response type: {type(response_text)}")
            
            # Return minimal valid structure based on context
            if "batch" in context:
                return {
                    "error": f"JSON parsing failed for {context}: {str(e)}",
                    "raw_response": response_text[:2000],
                    "batch_analysis": {
                        "batch_number": 1,
                        "slides_analyzed": 0,
                        "slide_range": "unknown"
                    },
                    "individual_slides": [],
                    "batch_insights": {
                        "narrative_development": "unknown",
                        "emotional_arc": "unknown",
                        "visual_consistency": "unknown"
                    },
                    "context_for_next_batch": {
                        "narrative_state": "unknown",
                        "emotional_state": "unknown"
                    }
                }
            else:
                return {
                    "error": f"JSON parsing failed for {context}: {str(e)}",
                    "raw_response": response_text[:2000],
                    "slideshow_metadata": {
                        "total_slides": 0,
                        "platform": "unknown"
                    },
                    "overall_assessment": {
                        "slideshow_effectiveness": 0.0
                    }
                }
    
    def _create_fallback_slideshow_analysis(self, metadata: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create fallback slideshow analysis structure when main analysis fails"""
        return {
            "slideshow_metadata": {
                "video_id": metadata.get('video_id', ''),
                "platform": metadata.get('platform', ''),
                "url": metadata.get('url', ''),
                "upload_date": metadata.get('upload_date', ''),
                "ingestion_date": metadata.get('ingestion_date', ''),
                "total_slides": 0,
                "estimated_display_duration": 0.0,
                "aspect_ratio": "unknown",
                "slide_format": "unknown"
            },
            "creator_profile": {
                "creator_id": metadata.get('creator_username', ''),
                "username": metadata.get('creator_username', ''),
                "demographics": {
                    "apparent_age_range": "unknown",
                    "apparent_gender": "unknown",
                    "apparent_ethnicity": "unknown",
                    "attractiveness_score": 0.0
                }
            },
            "narrative_architecture": {
                "story_framework": "unknown",
                "narrative_structure": "unknown",
                "story_arc_quality": 0.0,
                "story_cohesion": 0.0
            },
            "engagement_strategy": {
                "attention_curve": [],
                "curiosity_management": {
                    "curiosity_gaps_created": [],
                    "curiosity_arc": "unknown",
                    "payoff_delivery": 0.0
                }
            },
            "performance_prediction": {
                "viral_potential": {
                    "shareability_score": 0.0,
                    "memorable_moments": [],
                    "emotional_peak_slide": 0
                },
                "engagement_prediction": {
                    "completion_rate": 0.0,
                    "replay_likelihood": 0.0,
                    "save_probability": 0.0
                }
            },
            "overall_assessment": {
                "slideshow_effectiveness": 0.0,
                "narrative_strength": 0.0,
                "persuasion_power": 0.0,
                "engagement_quality": 0.0
            },
            "error": f"Slideshow analysis failed: {error_msg}",
            "fallback_used": True
        }
    
    def _get_default_slide_prompt(self) -> str:
        """Default slide analysis prompt if file not found"""
        return """Analyze these slideshow images individually. Focus on:
1. Each slide's purpose and message
2. Visual composition and design
3. Emotional tone and engagement tactics
4. How slides connect to each other
5. Narrative progression

Respond with JSON containing individual slide analysis and batch insights.

Previous context: {previous_slides_context}
Analyzing slides {start_slide_number} to {end_slide_number} of {total_slides} total."""
    
    def _get_default_final_prompt(self) -> str:
        """Default final slideshow prompt if file not found"""
        return """Analyze the complete slideshow using all slide data. Focus on:
1. Overall narrative structure and story arc
2. Slide relationships and flow
3. Engagement strategy and attention management
4. Persuasion architecture and conversion optimization
5. Performance predictions

All slides data: {all_slides_data}
Slideshow metadata: {slideshow_metadata}

Respond with comprehensive JSON analysis."""
    
    def generate_response(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """Generic method to get a text response from Gemini for any prompt"""
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]
            
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=contents
            )
            
            # Collect response text
            response_text = ""
            for chunk in response_stream:
                if chunk.text:
                    response_text += chunk.text
            
            return response_text.strip()
            
        except Exception as e:
            print(f"Error with Gemini API: {str(e)}", file=sys.stderr)
            return None