"""
YTShorts Storyboard Validator
Validates scenes, narrations, and visual prompts BEFORE image generation
to prevent token wastage, TTS crashes, caption overflows, and video composition errors.
Guarantees a zero-error, single-attempt render pipeline.
"""

import re
import json
import sys
from typing import Dict, Any, List, Union

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Banned tokens in visual prompts that cause Imagen to generate distorted text/artifacts
BANNED_VISUAL_TERMS = [
    r"\btext\b", r"\bwords\b", r"\bletters\b", r"\bwatermark\b",
    r"\btypography\b", r"\bfont\b", r"\bsubtitles?\b", r"\blogo\b",
    r"\btitle card\b", r"\bcaptions?\b"
]

# Essential camera/composition signals for high-fidelity 9:16 rendering
CAMERA_SIGNALS = [
    "macro", "close-up", "close up", "wide shot", "portrait", "low-angle",
    "low angle", "high-angle", "high angle", "eye-level", "cinematic",
    "anamorphic", "depth of field", "bokeh", "overhead", "establishing shot"
]

# Essential lighting/atmosphere signals
LIGHTING_SIGNALS = [
    "lighting", "light", "illumination", "volumetric", "god rays",
    "golden hour", "chiaroscuro", "shadows", "neon", "glow", "glows",
    "ambient", "dark", "moody", "torchlight", "rim light"
]

# Markdown syntax that damages TTS reading (reading 'asterisk', 'hash', etc.)
TTS_FORBIDDEN_PATTERNS = [
    (r"\*{1,3}[^*]+\*{1,3}", "Markdown bold/italic asterisks (TTS reads 'asterisk')"),
    (r"#{1,6}\s", "Markdown headers (TTS reads 'hash')"),
    (r"\[.*?\]", "Bracketed notes (e.g. [Sound Effect], [Laughter])"),
    (r"https?://\S+", "URLs (TTS reads literal link)"),
]


def sanitize_narration(text: str) -> str:
    """Cleans narration text to be safe for TTS synthesis and ASS caption subtitles."""
    # Strip markdown asterisks and underscores
    text = re.sub(r'[*_~`]', '', text)
    # Strip bracketed sound cues like [SFX: Whoosh]
    text = re.sub(r'\[.*?\]', '', text)
    # Strip parenthetical speaker cues like (Whispering) if short
    def clean_parentheses(m):
        content = m.group(1).strip()
        return "" if len(content.split()) <= 4 else f"({content})"
    text = re.sub(r'\((.*?)\)', clean_parentheses, text)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def validate_storyboard(storyboard_input: Union[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Validates storyboard scenes, narrations, and image prompts.
    Returns:
        {
            "valid": bool,
            "errors": list of blocking error messages,
            "warnings": list of quality/retention warnings,
            "stats": dict of calculated metrics,
            "sanitized_scenes": list of cleaned scene dicts ready for pipeline
        }
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # 1. Parse JSON if string
    raw_scenes = []
    if isinstance(storyboard_input, str):
        cleaned_str = storyboard_input.strip()
        cleaned_str = re.sub(r'^```(?:json)?\s*', '', cleaned_str, flags=re.IGNORECASE)
        cleaned_str = re.sub(r'\s*```$', '', cleaned_str, flags=re.IGNORECASE).strip()
        cleaned_str = re.sub(r',\s*([\]}])', r'\1', cleaned_str)
        try:
            parsed = json.loads(cleaned_str, strict=False)
            if isinstance(parsed, dict) and "scenes" in parsed:
                raw_scenes = parsed["scenes"]
            elif isinstance(parsed, list):
                raw_scenes = parsed
            else:
                errors.append("Storyboard must be a JSON array of scene objects or a dict with a 'scenes' list.")
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Malformed JSON in storyboard: {str(e)}"],
                "warnings": [],
                "stats": {},
                "sanitized_scenes": []
            }
    elif isinstance(storyboard_input, list):
        raw_scenes = storyboard_input
    elif isinstance(storyboard_input, dict):
        if "scenes" in storyboard_input and isinstance(storyboard_input["scenes"], list):
            raw_scenes = storyboard_input["scenes"]
        else:
            raw_scenes = [storyboard_input]
    else:
        return {
            "valid": False,
            "errors": ["Input must be a JSON string, a list of scene dictionaries, or a dictionary containing 'scenes'."],
            "warnings": [],
            "stats": {},
            "sanitized_scenes": []
        }

    # 2. Scene Count Validation
    scene_count = len(raw_scenes)
    if scene_count == 0:
        errors.append("Storyboard is empty (0 scenes). Minimum 4 scenes required.")
        return {"valid": False, "errors": errors, "warnings": warnings, "stats": {}, "sanitized_scenes": []}
    
    if scene_count < 4:
        errors.append(f"Scene count ({scene_count}) is too low. YouTube Shorts need at least 4-5 scenes to maintain engagement.")
    elif scene_count > 10:
        errors.append(f"Scene count ({scene_count}) is too high for a 60s YouTube Short. Limit to 5-8 scenes.")
    elif scene_count not in range(5, 9):
        warnings.append(f"Optimal Shorts scene count is 5-8 scenes; currently {scene_count}.")

    # 3. Analyze each scene
    sanitized_scenes: List[Dict[str, Any]] = []
    total_words = 0
    emoji_regex = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
    total_emojis = 0

    for idx, item in enumerate(raw_scenes):
        scene_num = idx + 1
        if not isinstance(item, dict):
            errors.append(f"Scene {scene_num} is not a valid dictionary object.")
            continue

        raw_narr = str(item.get("narration", "")).strip()
        raw_vis = str(item.get("visual", "")).strip()

        # Check narration presence
        if not raw_narr:
            errors.append(f"Scene {scene_num}: Missing 'narration' field.")
            continue

        # Check TTS formatting hazards
        for pattern, desc in TTS_FORBIDDEN_PATTERNS:
            if re.search(pattern, raw_narr):
                warnings.append(f"Scene {scene_num}: Contains {desc} in narration ('{raw_narr[:30]}...'). This will be automatically cleaned.")

        clean_narr = sanitize_narration(raw_narr)
        word_list = clean_narr.split()
        word_count = len(word_list)
        total_words += word_count

        # Narration length checks
        if word_count < 4:
            warnings.append(f"Scene {scene_num}: Narration is very short ({word_count} words). May sound clipped.")
        elif word_count > 20:
            warnings.append(f"Scene {scene_num}: Narration has {word_count} words (exceeds recommended 8-15 words). Risk of subtitle wrapping/overflow.")

        # Emoji check
        emojis_found = emoji_regex.findall(raw_narr)
        total_emojis += len(emojis_found)
        if not emojis_found and idx < 4:
            warnings.append(f"Scene {scene_num}: No emoji found in narration. Adding 1 emoji enhances TikTok-style subtitle engagement.")

        # Check visual prompt presence & detail
        if not raw_vis:
            errors.append(f"Scene {scene_num}: Missing 'visual' image prompt.")
        else:
            vis_lower = raw_vis.lower()
            vis_words = len(raw_vis.split())

            # Check prompt richness
            if vis_words < 10:
                warnings.append(f"Scene {scene_num}: Visual prompt is too brief ({vis_words} words). Detailed descriptions yield superior 8K Imagen results.")

            # Banned keywords check
            for banned in BANNED_VISUAL_TERMS:
                if re.search(banned, vis_lower):
                    errors.append(f"Scene {scene_num}: Visual prompt contains forbidden token '{banned}'. Image models will render garbled text artifacts. Remove it.")

            # Ambiguous character check (drift hazard)
            vague_character_match = re.search(r'\b(he|she|they|a man|a woman|the man|the woman|the boy|the girl|a person|the person)\b', vis_lower)
            if vague_character_match and not item.get("character_anchor") and not (isinstance(storyboard_input, dict) and storyboard_input.get("character_anchor")):
                warnings.append(
                    f"Scene {scene_num}: Visual prompt uses generic reference '{vague_character_match.group(0)}' without a Character Anchor. "
                    "Specify exact character traits (hair, age, clothing, facial features) to prevent face/outfit drift across scenes."
                )

            # Camera signal check
            has_camera = any(cam in vis_lower for cam in CAMERA_SIGNALS)
            if not has_camera:
                warnings.append(f"Scene {scene_num}: Visual prompt lacks camera angle/shot type (e.g. 'macro close-up', 'wide shot', 'cinematic portrait').")

            # Lighting signal check
            has_lighting = any(light in vis_lower for light in LIGHTING_SIGNALS)
            if not has_lighting:
                warnings.append(f"Scene {scene_num}: Visual prompt lacks lighting cues (e.g. 'warm rim lighting', 'volumetric god rays', 'moody chiaroscuro').")

        # Package sanitized scene
        clean_item = dict(item)
        clean_item["scene_number"] = scene_num
        clean_item["narration"] = clean_narr
        clean_item["visual"] = raw_vis
        sanitized_scenes.append(clean_item)

    # 4. Duplicate & Near-Duplicate Prompt Detection (Prevent Redundant Image Generation)
    stop_words = {"a", "an", "the", "in", "on", "at", "of", "with", "and", "or", "by", "for", "to", "from", "is", "are", "shot", "portrait", "vertical", "9:16", "8k"}
    for i in range(len(sanitized_scenes)):
        prompt_a = sanitized_scenes[i]["visual"].lower().strip()
        words_a = set(re.findall(r'\b[a-z]{3,}\b', prompt_a)) - stop_words
        for j in range(i + 1, len(sanitized_scenes)):
            prompt_b = sanitized_scenes[j]["visual"].lower().strip()
            if prompt_a == prompt_b:
                errors.append(f"Scene {i+1} and Scene {j+1}: EXACT DUPLICATE visual prompts. This causes duplicate image generation and wasted tokens!")
                continue
            words_b = set(re.findall(r'\b[a-z]{3,}\b', prompt_b)) - stop_words
            if words_a and words_b:
                overlap = len(words_a & words_b) / len(words_a | words_b)
                if overlap >= 0.75:
                    warnings.append(
                        f"Scene {i+1} and Scene {j+1}: High visual similarity ({int(overlap*100)}% word overlap). "
                        "Risk of generating visually redundant images. Vary the camera angle (e.g. macro vs wide) or focal action."
                    )

    # 5. Total Duration & Word Count Estimates
    # Normal TTS speaking rate: ~2.3 words per second (138 wpm)
    est_duration_sec = round(total_words / 2.3, 1) + (len(sanitized_scenes) * 0.4)  # Add minor pauses between scenes

    if total_words > 130:
        errors.append(f"Total word count is {total_words} words (approx. {est_duration_sec}s). Exceeds YouTube Shorts strict 60-second limit! Trim to under 100-110 words.")
    elif total_words < 40:
        warnings.append(f"Total word count is only {total_words} words (approx. {est_duration_sec}s). Consider expanding for optimal 30-45s retention.")

    # 5. Scene 1 Hook Validation
    if sanitized_scenes:
        hook_narr = sanitized_scenes[0]["narration"]
        has_hook_punctuation = any(p in hook_narr for p in ["?", "!", ":", "—"])
        has_hook_keyword = any(k in hook_narr.lower() for k in ["did you know", "what if", "stop", "never", "why", "secret", "top", "this is", "how"])
        if not (has_hook_punctuation or has_hook_keyword):
            warnings.append("Scene 1 Hook: First scene does not contain strong hook triggers or punctuation (? / !). Ensure the opening 3 seconds create a curiosity gap.")

    stats = {
        "scene_count": scene_count,
        "total_words": total_words,
        "estimated_duration_sec": est_duration_sec,
        "avg_words_per_scene": round(total_words / max(1, scene_count), 1),
        "total_emojis": total_emojis,
        "fits_shorts_60s_limit": est_duration_sec < 58.0
    }

    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
        "sanitized_scenes": sanitized_scenes
    }


def print_validation_report(res: Dict[str, Any]) -> None:
    """Formats and prints the validation results in a clean visual CLI report."""
    print("\n" + "=" * 65)
    print("🎬 YTSHORTS STORYBOARD PRE-FLIGHT VALIDATION REPORT")
    print("=" * 65)
    
    stats = res.get("stats", {})
    if stats:
        print(f"  Scenes            : {stats.get('scene_count')}")
        print(f"  Total Words       : {stats.get('total_words')}")
        print(f"  Est. Video Length : ~{stats.get('estimated_duration_sec')}s (Limit: <60s)")
        print(f"  Pacing            : {stats.get('avg_words_per_scene')} words/scene")
        print(f"  Subtitle Emojis   : {stats.get('total_emojis')} detected")
    print("-" * 65)

    if res["valid"]:
        print("  STATUS: ✅ PASSED VALIDATION (Ready for single-attempt render)")
    else:
        print("  STATUS: ❌ FAILED VALIDATION (Must resolve errors before generating images)")

    if res["errors"]:
        print("\n🚨 BLOCKING ERRORS (Will cause failure or token wastage):")
        for err in res["errors"]:
            print(f"   ✖ {err}")

    if res["warnings"]:
        print("\n⚠️ QUALITY & RETENTION WARNINGS (Suggestions):")
        for warn in res["warnings"]:
            print(f"   ! {warn}")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate YTShorts storyboard JSON.")
    parser.add_argument("--json", type=str, help="Path to JSON file or raw JSON string.")
    args = parser.parse_args()

    if args.json:
        if args.json.endswith(".json") and sys.platform.startswith("win") or "/" in args.json or "\\" in args.json:
            import os
            if os.path.isfile(args.json):
                with open(args.json, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = args.json
        else:
            content = args.json

        result = validate_storyboard(content)
        print_validation_report(result)
        sys.exit(0 if result["valid"] else 1)
    else:
        # Self-test with sample
        sample = [
            {"scene_number": 1, "narration": "Did you know honey never expires? 🍯 Scientists found 3000-year-old honey!", "visual": "Ancient Egyptian tomb with golden jars, warm amber torchlight, cinematic macro lens, 9:16 vertical"},
            {"scene_number": 2, "narration": "Bacteria cannot survive in it ⚗️ due to near-zero moisture and natural peroxide.", "visual": "Microscopic glowing honey crystal molecules, deep blue scientific laboratory, volumetric lighting"},
            {"scene_number": 3, "narration": "Ancient pharaohs even preserved royal mummies using this golden liquid! 👑", "visual": "Golden Egyptian pharaoh sarcophagus, candlelit temple interior, dramatic cinematic rim lighting, 8k"},
            {"scene_number": 4, "narration": "Subscribe for more incredible historical facts! 🔔", "visual": "Ancient leather-bound book illuminated by floating golden stardust particles, dark moody atmospheric lighting"}
        ]
        result = validate_storyboard(sample)
        print_validation_report(result)
