"""
Script-to-Clip Brain (Playbook)
================================
A comprehensive guide for matching clips to script segments.

This is NOT a statistics engine. It's a PLAYBOOK that teaches:
1. How to break script lines into conceptual boundaries
2. What type of clip belongs with each boundary
3. Rules and examples for clip selection

The brain learns by absorbing real examples from analyzed videos,
building a library of "when the script says X, show Y" patterns.
"""

import os
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime


@dataclass
class ClipExample:
    """A single example of script-to-clip mapping."""
    script_text: str
    clip_type: str  # talking_head, product_shot, screen_demo, broll, text_graphic, lifestyle, demonstration
    visual_description: str  # What we actually see
    setting: str
    subject: str
    text_on_screen: List[str]
    function: str  # hook, problem, agitation, solution, demo, benefit, proof, cta, transition


@dataclass
class ScriptClipBrain:
    """
    The master playbook for script-to-clip selection.

    Organized by CLIP TYPE - for each type, we store:
    - When to use it (what kind of script content)
    - Examples from real videos
    - What variations exist
    """
    version: str = "4.0"
    created_at: str = ""
    updated_at: str = ""
    videos_learned_from: int = 0

    # THE PLAYBOOK: Organized by clip type
    # clip_type -> list of examples
    playbook: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    # Examples organized by function (hook, problem, solution, etc.)
    # function -> list of examples
    by_function: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    # Transition patterns: what clip types follow what
    # "clip_type -> clip_type" -> list of script context examples
    transitions: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

        # Initialize clip type categories
        clip_types = [
            'talking_head',
            'product_shot',
            'screen_demo',
            'broll',
            'text_graphic',
            'lifestyle',
            'demonstration',
            'testimonial',
            'other'
        ]
        for ct in clip_types:
            if ct not in self.playbook:
                self.playbook[ct] = []

    def learn_from_clip(self, clip_data: Dict[str, Any]):
        """Learn from a single analyzed clip."""
        visual = clip_data.get('visual', {})
        functional = clip_data.get('functional', {})

        script = clip_data.get('script_segment', '').strip()
        clip_type = self._determine_clip_type(visual, functional)
        function = functional.get('clip_function', 'unknown')

        example = {
            'script': script,
            'clip_type': clip_type,
            'visual_description': visual.get('subject_description', ''),
            'setting': visual.get('setting_description', ''),
            'setting_type': visual.get('setting_type', ''),
            'subject_type': visual.get('subject_type', ''),
            'subject_action': visual.get('subject_action', ''),
            'text_on_screen': visual.get('text_on_screen', []),
            'shot_type': visual.get('shot_type', ''),
            'function': function,
        }

        # Add to playbook by clip type
        if clip_type not in self.playbook:
            self.playbook[clip_type] = []

        # Avoid duplicates, keep diverse examples (max 50 per type)
        if len(self.playbook[clip_type]) < 50:
            if not self._is_duplicate(example, self.playbook[clip_type]):
                self.playbook[clip_type].append(example)

        # Add to by_function
        if function not in self.by_function:
            self.by_function[function] = []
        if len(self.by_function[function]) < 50:
            if not self._is_duplicate(example, self.by_function[function]):
                self.by_function[function].append(example)

        self.updated_at = datetime.now().isoformat()

    def learn_transition(self, clip1_data: Dict, clip2_data: Dict):
        """Learn what clip types follow each other and in what context."""
        visual1 = clip1_data.get('visual', {})
        visual2 = clip2_data.get('visual', {})
        functional1 = clip1_data.get('functional', {})
        functional2 = clip2_data.get('functional', {})

        type1 = self._determine_clip_type(visual1, functional1)
        type2 = self._determine_clip_type(visual2, functional2)

        transition_key = f"{type1} -> {type2}"

        if transition_key not in self.transitions:
            self.transitions[transition_key] = []

        if len(self.transitions[transition_key]) < 20:
            self.transitions[transition_key].append({
                'from_script': clip1_data.get('script_segment', ''),
                'from_function': functional1.get('clip_function', ''),
                'to_script': clip2_data.get('script_segment', ''),
                'to_function': functional2.get('clip_function', ''),
            })

    def learn_sequence(self, clips: List[Dict[str, Any]]):
        """Learn transitions from a sequence of clips."""
        for i in range(len(clips) - 1):
            self.learn_transition(clips[i], clips[i + 1])

    def _determine_clip_type(self, visual: Dict, functional: Dict) -> str:
        """Categorize the clip type."""
        subject = visual.get('subject_type', '').lower()
        setting = visual.get('setting_type', '').lower()
        subject_desc = visual.get('subject_description', '').lower()
        subject_action = visual.get('subject_action', '').lower()

        if subject == 'product' or 'product' in subject_desc:
            return 'product_shot'
        elif subject in ['text_screen', 'graphic']:
            return 'text_graphic'
        elif 'screen_recording' in setting or setting == 'screen_recording':
            return 'screen_demo'
        elif subject == 'person':
            if subject_action == 'speaking':
                return 'talking_head'
            elif subject_action == 'demonstrating':
                return 'demonstration'
            elif 'testimonial' in subject_desc or 'customer' in subject_desc:
                return 'testimonial'
            else:
                return 'lifestyle'
        elif subject == 'b_roll':
            return 'broll'
        else:
            return 'other'

    def _is_duplicate(self, example: Dict, examples: List[Dict]) -> bool:
        """Check if example is too similar to existing ones."""
        script = example.get('script', '').lower()
        if not script:
            return False
        for ex in examples:
            if ex.get('script', '').lower() == script:
                return True
        return False

    def save(self, path: str):
        """Save brain to pickle."""
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> 'ScriptClipBrain':
        """Load brain from pickle."""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
        return cls()

    def to_text(self) -> str:
        """Generate the complete playbook as text."""
        lines = []

        lines.append("=" * 80)
        lines.append("SCRIPT-TO-CLIP PLAYBOOK")
        lines.append("=" * 80)
        lines.append(f"Videos Analyzed: {self.videos_learned_from}")
        lines.append(f"Last Updated: {self.updated_at}")
        lines.append("")
        lines.append("This playbook shows what clips to use for different script content.")
        lines.append("Use it as a reference when breaking down a new script.")
        lines.append("")

        # ===========================================
        # SECTION 1: CLIP TYPES AND WHEN TO USE THEM
        # ===========================================
        lines.append("=" * 80)
        lines.append("PART 1: CLIP TYPES - WHEN TO USE EACH")
        lines.append("=" * 80)
        lines.append("")

        clip_type_descriptions = {
            'talking_head': 'Person speaking directly to camera. Use for direct address, personal connection, credibility.',
            'product_shot': 'Close-up or beauty shot of the product. Use when mentioning the product, features, or results.',
            'screen_demo': 'Screen recording or software demonstration. Use when showing how something works.',
            'broll': 'Supplementary footage. Use to illustrate concepts, add visual interest, or cover cuts.',
            'text_graphic': 'Text, titles, or graphics on screen. Use for emphasis, stats, quotes, or CTAs.',
            'lifestyle': 'People using product or in relevant situations. Use for aspirational or relatable moments.',
            'demonstration': 'Person actively showing/doing something. Use for tutorials, how-tos, proof.',
            'testimonial': 'Customer or user speaking. Use for social proof and credibility.',
        }

        for clip_type, description in clip_type_descriptions.items():
            examples = self.playbook.get(clip_type, [])

            lines.append("-" * 80)
            lines.append(f"## {clip_type.upper().replace('_', ' ')}")
            lines.append("-" * 80)
            lines.append(f"Definition: {description}")
            lines.append(f"Examples in library: {len(examples)}")
            lines.append("")

            if examples:
                lines.append("WHEN TO USE (learned from real ads):")
                lines.append("")

                # Group by function
                by_func = {}
                for ex in examples:
                    func = ex.get('function', 'unknown')
                    if func not in by_func:
                        by_func[func] = []
                    by_func[func].append(ex)

                for func, func_examples in sorted(by_func.items()):
                    lines.append(f"  For {func.upper()} segments:")
                    for ex in func_examples[:3]:  # Show up to 3 per function
                        script = ex.get('script', '[no dialogue]')
                        if len(script) > 80:
                            script = script[:80] + "..."
                        lines.append(f"    Script: \"{script}\"")
                        if ex.get('visual_description'):
                            lines.append(f"    Visual: {ex['visual_description'][:60]}")
                        if ex.get('text_on_screen'):
                            lines.append(f"    Text on screen: {ex['text_on_screen']}")
                        lines.append("")
            else:
                lines.append("  No examples yet - analyze more videos to build library.")
                lines.append("")

        # ===========================================
        # SECTION 2: BY SCRIPT FUNCTION
        # ===========================================
        lines.append("")
        lines.append("=" * 80)
        lines.append("PART 2: CLIP SELECTION BY SCRIPT FUNCTION")
        lines.append("=" * 80)
        lines.append("")
        lines.append("What clips work best for each part of the ad structure:")
        lines.append("")

        function_descriptions = {
            'hook': 'Opening that grabs attention. First 3-5 seconds.',
            'problem': 'Identifying the pain point or challenge.',
            'agitation': 'Making the problem feel urgent or painful.',
            'solution': 'Introducing the product/service as the answer.',
            'demo': 'Showing how it works.',
            'benefit': 'Explaining what the viewer gains.',
            'proof': 'Evidence it works (testimonials, stats, results).',
            'cta': 'Call to action - what to do next.',
            'transition': 'Connecting segments, pacing changes.',
        }

        for function, description in function_descriptions.items():
            examples = self.by_function.get(function, [])

            lines.append("-" * 80)
            lines.append(f"## {function.upper()}")
            lines.append("-" * 80)
            lines.append(f"Purpose: {description}")
            lines.append("")

            if examples:
                # Count clip types used
                type_counts = {}
                for ex in examples:
                    ct = ex.get('clip_type', 'unknown')
                    type_counts[ct] = type_counts.get(ct, 0) + 1

                lines.append("Clip types that work for this:")
                for ct, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                    lines.append(f"  - {ct}")
                lines.append("")

                lines.append("Examples:")
                for ex in examples[:5]:
                    script = ex.get('script', '[no dialogue]')
                    if len(script) > 70:
                        script = script[:70] + "..."
                    lines.append(f"  Script: \"{script}\"")
                    lines.append(f"  -> Use: {ex.get('clip_type', '?')}")
                    if ex.get('visual_description'):
                        lines.append(f"     Show: {ex['visual_description'][:50]}")
                    lines.append("")
            else:
                lines.append("  No examples yet.")
                lines.append("")

        # ===========================================
        # SECTION 3: TRANSITIONS
        # ===========================================
        if self.transitions:
            lines.append("")
            lines.append("=" * 80)
            lines.append("PART 3: CLIP TRANSITIONS")
            lines.append("=" * 80)
            lines.append("")
            lines.append("What clip types naturally follow each other:")
            lines.append("")

            for transition, examples in sorted(self.transitions.items()):
                lines.append(f"  {transition}")
                if examples:
                    ex = examples[0]
                    from_script = ex.get('from_script', '')[:40]
                    to_script = ex.get('to_script', '')[:40]
                    if from_script or to_script:
                        lines.append(f"    e.g., \"{from_script}...\" -> \"{to_script}...\"")
                lines.append("")

        # ===========================================
        # SECTION 4: QUICK REFERENCE RULES
        # ===========================================
        lines.append("")
        lines.append("=" * 80)
        lines.append("PART 4: QUICK REFERENCE RULES")
        lines.append("=" * 80)
        lines.append("")
        lines.append("CONCEPTUAL BOUNDARIES:")
        lines.append("  - Break script at natural thought boundaries")
        lines.append("  - If a line takes >3 seconds to say, it likely needs multiple clips")
        lines.append("  - Each clip should have ONE visual focus")
        lines.append("  - Change clip when: topic shifts, emotion shifts, or emphasis needed")
        lines.append("")
        lines.append("MATCHING RULES:")
        lines.append("  - Mention product by name -> PRODUCT SHOT")
        lines.append("  - Show how it works -> SCREEN DEMO or DEMONSTRATION")
        lines.append("  - Direct address ('you', 'your') -> TALKING HEAD")
        lines.append("  - Stats or key points -> TEXT GRAPHIC")
        lines.append("  - Emotional/aspirational language -> LIFESTYLE or BROLL")
        lines.append("  - Customer quote or result -> TESTIMONIAL")
        lines.append("  - Action words (click, sign up, get) -> CTA with TEXT GRAPHIC")
        lines.append("")
        lines.append("PACING:")
        lines.append("  - Don't stay on talking head too long - cut to broll/product")
        lines.append("  - After product shot, often return to talking head")
        lines.append("  - Text graphics are punchy - use for emphasis, not narration")
        lines.append("  - Broll covers transitions and adds visual variety")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


def main():
    """CLI to view brain/playbook."""
    import argparse

    parser = argparse.ArgumentParser(description="Script-to-Clip Playbook")
    parser.add_argument('--brain', default='script_clip_brain.pkl', help='Path to brain file')
    parser.add_argument('--output', '-o', help='Output text file')

    args = parser.parse_args()

    brain = ScriptClipBrain.load(args.brain)
    output = brain.to_text()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Playbook saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
