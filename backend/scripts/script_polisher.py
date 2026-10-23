import os
import re
import requests
from dotenv import load_dotenv
from scripts.llm_client import query_llm, clean_json_string

# Load environment variables from .env
load_dotenv()

SYSTEM_PROMPT = """You are an expert YouTube Shorts director and scriptwriter. Your job is to polish raw user scripts into high-impact, high-retention viral YouTube Shorts, select contextually appropriate emojis for subtitles, and generate highly descriptive scene-by-scene visual prompts for the AI image generator.

Rules:
- Keep the total length SHORT: exactly 5-7 scenes, total 60-80 words (fits in ~30 seconds of speech).
- Open with a powerful HOOK in the very first scene to grab attention instantly.
- Write in punchy, short, easy-to-read narration sentences. One sentence per scene.
- Inject 1-2 highly contextually relevant Emojis directly into each scene's narration sentence to maximize subtitle visual appeal (e.g. "Egyptian tombs 🏛️" or "ancient pharaohs 👑").
- For each scene, create a corresponding highly descriptive, cinematic camera/image prompt for the AI image generator. 
  - ALWAYS include camera shot size & angle (e.g., "Macro extreme close up", "Low-angle dramatic wide shot", "Anamorphic cinematic medium shot").
  - ALWAYS specify lighting quality (e.g., "warm golden hour light rays", "moody volumetric rim lighting", "dramatic cinematic backlighting").
  - Describe details with hyper-realistic granularity (e.g. sharp skin pores, natural hair textures, volumetric atmospheric depth, ultra-sharp 4K/8K lens resolution) to leverage our high-fidelity vertical canvas.
  - Do NOT include text, watermarks, signatures, abstract concepts, or generic adjectives like "cool" or "gorgeous". Make them concrete and photorealistic.
  - Maintain stylistic consistency across scenes.

Format the output as a strict, clean JSON array of scene objects. Do not wrap the JSON in markdown code blocks or add any other text outside the JSON.

Expected JSON Structure:
[
  {
    "scene_number": 1,
    "narration": "Narration sentence with embedded emojis...",
    "visual": "Cinematic visual camera prompt..."
  },
  ...
]"""




DIALOGUE_SYSTEM_PROMPT = """You are an expert viral YouTube Shorts director specializing in fast-paced 2-character conversational dialogue Shorts.
Your job is to transform a raw topic, story, or conversation into an alternating dialogue between two characters (Character A and Character B).

Rules:
- Keep the total length snappy: 5 to 7 turns, total 60-80 words (fits in ~30 seconds of speech).
- Open with a powerful HOOK question, exclamation, or shocking statement in Scene 1.
- Characters alternate speaking: Character A, Character B, Character A, Character B, etc.
- Each scene must be tagged with:
  - "speaker": The name of the speaking character (e.g. "Mia", "Ben", "Host", "Guest").
  - "voice_gender": "female" for Character A, "male" for Character B (or vice versa).
- Spoken narration must be punchy, natural, conversational banter (8-14 words per turn).
- Inject 1-2 contextually relevant Emojis directly into each scene's narration sentence.
- For each scene, create a corresponding descriptive, cinematic 9:16 vertical camera visual prompt focusing on the speaking character's expressions, actions, and consistent environment.

Format the output as a strict, clean JSON array of scene objects. Do not wrap in markdown code blocks.

Expected JSON Structure:
[
  {
    "scene_number": 1,
    "speaker": "Mia",
    "voice_gender": "female",
    "narration": "Ben, tell me you did NOT just give my secret sandwich to the dog! 🥪😱",
    "visual": "Cinematic close-up of an expressive teenage girl with hands on her hips, questioning look, cozy warm kitchen, 9:16 vertical portrait, dramatic rim lighting..."
  },
  {
    "scene_number": 2,
    "speaker": "Ben",
    "voice_gender": "male",
    "narration": "Max was starving! Look at those puppy eyes, how could I resist? 🐶🥺",
    "visual": "Cinematic medium shot of a boy pointing towards a happy puppy on the kitchen floor, warm sunlight, 9:16 vertical..."
  }
]"""


# Language directives appended to the system prompt when a non-English voice is selected.
# Visual prompts ALWAYS stay in English so the image generator works correctly.
LANGUAGE_DIRECTIVES = {
    "Hindi":    "LANGUAGE DIRECTIVE: Write ALL narration text in Hindi (Devanagari script: हिन्दी). Visual image prompts must remain in English.",
    "Bengali":  "LANGUAGE DIRECTIVE: Write ALL narration text in Bengali (বাংলা script). Visual image prompts must remain in English.",
    "Punjabi":  "LANGUAGE DIRECTIVE: Write ALL narration text in Punjabi (ਪੰਜਾਬੀ / Gurmukhi script). Visual image prompts must remain in English.",
    "Bhojpuri": "LANGUAGE DIRECTIVE: Write ALL narration text in Bhojpuri (using Devanagari script, similar to Hindi but in Bhojpuri dialect/vocabulary). Visual image prompts must remain in English.",
}


def parse_storyboard(storyboard_text) -> list[dict]:
    """
    Parses a structured JSON storyboard string into a list of scenes.
    Each scene is a dict with 'narration', 'visual', and optional 'speaker'/'narration_hi'.
    Extremely robust against markdown formatting, mixed-case, delimiter-style fallbacks,
    and plain text splits.
    """
    import json
    if isinstance(storyboard_text, list):
        return storyboard_text
        
    scenes = []
    if not storyboard_text:
        return scenes

    if not isinstance(storyboard_text, str):
        storyboard_text = str(storyboard_text)

    text = storyboard_text.strip()
    
    # 1. Try decoding as highly fault-tolerant JSON list first
    try:
        clean_text = text
        
        # Strip markdown json code block markers if present
        clean_text = re.sub(r'^```(?:json)?\s*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\s*```$', '', clean_text, flags=re.IGNORECASE).strip()
        
        # Clean up any trailing commas before closing brackets or braces (common LLM generation anomaly)
        clean_text = re.sub(r',\s*([\]}])', r'\1', clean_text)
        
        # Dynamically extract first '[' to last ']' or first '{' to last '}' to ignore any leading/trailing AI remarks
        start_idx = clean_text.find('[')
        end_idx = clean_text.rfind(']')
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            # Fallback check for single object wrapped in braces
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean_text = clean_text[start_idx:end_idx+1]
            
        # Parse using strict=False to natively allow literal control characters (newlines, tabs) inside string fields!
        parsed = json.loads(clean_text, strict=False)
        
        # Auto-extract list wrapper from standard dictionary envelopes (e.g. {"scenes": [...]})
        if isinstance(parsed, dict):
            extracted_list = False
            for val in parsed.values():
                if isinstance(val, list):
                    parsed = val
                    extracted_list = True
                    break
            # If not a list envelope but represents a single scene dictionary, wrap it in a list!
            if not extracted_list and "narration" in parsed:
                parsed = [parsed]
                    
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    narration = item.get("narration", "").strip()
                    narration_hi = item.get("narration_hi", "").strip()
                    visual = item.get("visual", "").strip()
                    speaker = item.get("speaker", "").strip()
                    
                    if narration or narration_hi:
                        scene = {
                            "narration": narration if narration else narration_hi,
                            "visual": visual if visual else (narration if narration else narration_hi)
                        }
                        if narration_hi:
                            scene["narration_hi"] = narration_hi
                        if speaker:
                            scene["speaker"] = speaker
                        voice_gender = item.get("voice_gender", "").strip().lower()
                        if voice_gender:
                            scene["voice_gender"] = voice_gender
                        scenes.append(scene)
            if scenes:
                return scenes
    except Exception as exc:
        print(f"[script_polisher] Fault-tolerant JSON parser exception: {exc}. Retrying block-based fallback...", flush=True)

    # 2. Fallback to parsing legacy ---SCENE--- block structures
    # Normalize bold/italic markers to standard uppercase tag format (e.g., NARRATION:)
    text = re.sub(r'\*+(NARRATION|VOICEOVER|AUDIO|VISUAL|IMAGE|PROMPT):\*+', r'\1:', text, flags=re.IGNORECASE)
    
    blocks = []
    if re.search(r'---SCENE---', text, re.IGNORECASE):
        blocks = re.split(r'---SCENE---', text, flags=re.IGNORECASE)
    elif re.search(r'(?:^|\n)\s*(?:###?\s*)?Scene\s*\d+\b', text, re.IGNORECASE):
        blocks = re.split(r'(?:^|\n)\s*(?:###?\s*)?Scene\s*\d+\b', text, flags=re.IGNORECASE)
    elif re.search(r'---', text):
        blocks = re.split(r'---', text)
    else:
        blocks = [text]

    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        narration_match = re.search(r'(?:NARRATION|VOICEOVER|AUDIO):\s*(.*?)(?=(?:VISUAL|IMAGE|PROMPT|NARRATION|VOICEOVER|AUDIO):|$)', block, re.DOTALL | re.IGNORECASE)
        visual_match = re.search(r'(?:VISUAL|IMAGE|PROMPT):\s*(.*?)(?=(?:NARRATION|VOICEOVER|AUDIO|VISUAL|IMAGE|PROMPT):|$)', block, re.DOTALL | re.IGNORECASE)
        
        narration = narration_match.group(1).strip() if narration_match else ""
        visual = visual_match.group(1).strip() if visual_match else ""
        
        if visual:
            visual = visual.strip('[]"\'')
            
        if narration:
            if not visual:
                visual = narration
            scenes.append({
                "narration": narration,
                "visual": visual
            })
            
    if len(scenes) <= 1:
        fallback_scenes = []
        pattern = r'(?:NARRATION|VOICEOVER|AUDIO):\s*(.*?)\s*(?:VISUAL|IMAGE|PROMPT):\s*(.*?)(?=(?:NARRATION|VOICEOVER|AUDIO|VISUAL|IMAGE|PROMPT):|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        for narr, vis in matches:
            narr_clean = narr.strip()
            vis_clean = vis.strip().strip('[]"\'')
            if narr_clean:
                fallback_scenes.append({
                    "narration": narr_clean,
                    "visual": vis_clean if vis_clean else narr_clean
                })
        if len(fallback_scenes) > len(scenes):
            scenes = fallback_scenes

    if not scenes:
        print("[script_polisher] Structured parsing found no scenes, running sentence splitter fallback...", flush=True)
        # If the input contains raw JSON markup but parsing failed, scrub all JSON syntax tags to prevent raw code fragments from leaking to client UI
        clean_fallback_text = text
        if '[' in clean_fallback_text or '{' in clean_fallback_text:
            clean_fallback_text = re.sub(r'[\{\}\[\]"\'\:\,]', ' ', clean_fallback_text)
            clean_fallback_text = re.sub(r'\b(?:scene_number|narration|visual|scene)\b', ' ', clean_fallback_text, flags=re.IGNORECASE)
            clean_fallback_text = re.sub(r'\s+', ' ', clean_fallback_text).strip()
            
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_fallback_text) if len(s.strip()) > 10]
        for s in sentences:
            scenes.append({
                "narration": s,
                "visual": s
            })
            
    return scenes


def polish_with_pollinations(raw_script: str, system_prompt: str = None) -> str:
    """
    Polishes script using the centralized LLM client.
    """
    active_prompt = system_prompt or SYSTEM_PROMPT
    user_content = f"Polish this script into a structured storyboard for YouTube Shorts:\n\n{raw_script}"
    return query_llm(
        user_content,
        system_prompt=active_prompt,
        response_format_json=True,
        temperature=0.65,
        max_tokens=1000
    )



def analyze_script_style(raw_script: str) -> str:
    """
    Scans the raw script topic and tone to dynamically generate exactly 2-3 specific
    visual styling modifiers optimized for the image generators using the central LLM client.
    """
    if not raw_script or len(raw_script.strip()) < 10:
        return ""
    
    # Conserve keyless Pollinations calls for the main storyboard to respect cooling period
    if not os.getenv("GEMINI_API_KEY", "").strip():
        return ""
        
    analysis_prompt = (
        "You are an expert art director. Analyze the following video script topic/tone and output exactly 2-3 specific "
        "visual style and texture modifiers (e.g. 'sharp rustic wooden textures, soft warm flour dustings, natural studio highlights' "
        "or 'sleek high-contrast neon glows, sharp mechanical keyboard close-ups, modern high-tech workspace screen code displays') "
        "that will make the AI image generator match this topic perfectly. "
        "Output ONLY the 2-3 styling modifiers as a single line, nothing else. No explanation, no intro, no punctuation at the end.\n\n"
        f"Script to analyze:\n{raw_script}"
    )
    
    result = query_llm(analysis_prompt, temperature=0.5, max_tokens=60)
    if result:
        result = result.strip('"`\' ')
        print(f"[script_polisher] [STYLE CLASSIFIED]: \"{result}\"", flush=True)
        return result
    return ""


def evaluate_script(script: str, mode: str = "shorts") -> float:
    """
    Heuristically grades a script for YouTube Shorts engagement.
    If structured, grades only the spoken narration text.
    Returns a score out of 100.
    """
    if not script:
        return 0.0

    # Parse and extract only narration text for evaluation
    scenes = parse_storyboard(script)
    spoken_text = " ".join([scene["narration"] for scene in scenes])
    
    if not spoken_text.strip():
        spoken_text = script

    score = 0.0
    words = spoken_text.split()
    word_count = len(words)


    # --- SHORTS MODE SCORING ---
    # 1. Word Count Score (45-75 words is ideal for Shorts - max 40 points)
    if 45 <= word_count <= 75:
        score += 40.0
    elif 30 <= word_count < 45:
        score += 25.0
    elif 75 < word_count <= 90:
        score += 20.0
    else:
        score += 5.0  # too short or too long

    # Split into sentences using simple regex
    sentences = [s.strip() for s in re.split(r'[.!?]+', spoken_text) if s.strip()]
    sentence_count = len(sentences)

    if sentence_count > 0:
        avg_sentence_len = word_count / sentence_count
        
        # 2. Punchiness / Sentence Length (Ideal is short, punchy sentences under 15 words - max 30 points)
        if avg_sentence_len <= 12:
            score += 30.0
        elif avg_sentence_len <= 16:
            score += 20.0
        else:
            score += 10.0

        # 3. Hook strength in first sentence (max 30 points)
        first_sentence = sentences[0].lower()
        
        is_question = spoken_text.strip().split('.')[0].strip().endswith('?') or first_sentence.endswith('?')
        
        hook_words = [
            "ever wonder", "did you know", "what if", "imagine", "the shocking truth",
            "this is why", "most people don't know", "secrets of", "stop doing", "never",
            "you won't believe", "the truth about", "nobody talks about", "here's why",
            "turns out", "the real reason", "scientists discovered", "this changes everything",
            "warning", "actually", "this is illegal", "they don't want you to know"
        ]
        has_hook_word = any(hw in first_sentence for hw in hook_words)

        if is_question and has_hook_word:
            score += 30.0
        elif is_question or has_hook_word:
            score += 20.0
        else:
            if len(first_sentence.split()) < 8:
                score += 15.0
            else:
                score += 5.0

    return score



def polish_script(raw_script: str, mode: str = "shorts", language: str = "English") -> str:
    """
    Orchestrates script polishing. Supports modes:
      - 'shorts' (default): viral YouTube Shorts — 5-7 scenes, 60-80 words, hook-first.
      - 'dialogue': multi-character conversational banter — alternating 2 characters with speaker tags.
    language: target narration language (e.g. 'Hindi', 'Bengali'). Defaults to 'English'.
    """
    import json
    mode_label = "Dialogue" if mode == "dialogue" else "Shorts"

    import concurrent.futures

    # Phase 1 & 2: Dynamic Style Meta-Prompting Layer
    style_modifiers = analyze_script_style(raw_script)
    base_prompt = DIALOGUE_SYSTEM_PROMPT if mode == "dialogue" else SYSTEM_PROMPT

    # Inject language directive when a non-English voice is selected
    lang_directive = LANGUAGE_DIRECTIVES.get(language, "")
    if lang_directive:
        base_prompt = base_prompt + f"\n\n{lang_directive}"
        print(f"[script_polisher] Language directive injected: {language}", flush=True)

    if style_modifiers:
        active_system_prompt = base_prompt + f"\n- TOPIC-SPECIFIC AESTHETIC DIRECTIVES: Generate scene visual prompts following this custom vibe: {style_modifiers}"
    else:
        active_system_prompt = base_prompt

    print(f"\n[script_polisher] --- {mode_label.upper()} STORYBOARD POLISHING PIPELINE START ---", flush=True)
    print(f"[script_polisher] Original Script ({len(raw_script.split())} words): \"{raw_script[:100]}...\"", flush=True)

    print(f"[script_polisher] Using Pollinations.ai only ({mode_label} mode).", flush=True)
    pol_script = polish_with_pollinations(raw_script, system_prompt=active_system_prompt)
    pol_score = evaluate_script(pol_script, mode=mode)
    print(f"[script_polisher] Pollinations Score: {pol_score:.1f}/100", flush=True)
    winner_script = pol_script if pol_script else raw_script
    winner_name = "Pollinations.ai" if pol_script else "Original (Fallback)"

    # Validate scenes and standardize to clean JSON string
    import json
    scenes = parse_storyboard(winner_script)
    
    # Auto-recovery: If we ended up with only 1 scene, but the original raw script contains multiple sentences or dialogue turns,
    # it means the free text model collapsed the story or hit a cooling limit. We fall back gracefully to structured turns!
    if len(scenes) <= 1:
        if mode == "dialogue":
            # 1. Attempt to extract structured speaker turns like "Mia: ..." and "Ben: ..."
            dialogue_turns = re.findall(r'([A-Za-z0-9_\s]{2,15})\s*:\s*([^:\n]+)', raw_script)
            if len(dialogue_turns) >= 2:
                print(f"[script_polisher] Dialogue recovery: extracted {len(dialogue_turns)} speaker dialogue turns.", flush=True)
                scenes = []
                for idx, (spk, text) in enumerate(dialogue_turns):
                    scenes.append({
                        "scene_number": idx + 1,
                        "speaker": spk.strip(),
                        "voice_gender": "female" if idx % 2 == 0 else "male",
                        "narration": text.strip(),
                        "visual": f"Cinematic close-up of {spk.strip()}, vertical 9:16 portrait, expressive lighting"
                    })
            else:
                # 2. Split on sentence or conversational clause conjunctions (but, while, however)
                dialogue_splits = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=[,;])\s+(?:but|while|whereas|however|and then|yet)\s+', raw_script) if len(s.strip()) > 8]
                if len(dialogue_splits) >= 2:
                    print(f"[script_polisher] Dialogue recovery: clause-split into {len(dialogue_splits)} conversational scenes.", flush=True)
                    scenes = []
                    for idx, s in enumerate(dialogue_splits):
                        scenes.append({
                            "scene_number": idx + 1,
                            "speaker": "Character A" if idx % 2 == 0 else "Character B",
                            "voice_gender": "female" if idx % 2 == 0 else "male",
                            "narration": s,
                            "visual": f"Cinematic shot of Character {'A' if idx % 2 == 0 else 'B'}, 9:16 vertical, vibrant lighting"
                        })
        else:
            # Check if original script has multiple sentences
            raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_script) if len(s.strip()) > 10]
            if len(raw_sentences) > 1:
                print(f"[script_polisher] Auto-recovery: collapsed storyboard ({len(scenes)} scenes) recovered to sentence-split storyboard ({len(raw_sentences)} scenes).", flush=True)
                scenes = []
                for s in raw_sentences:
                    scenes.append({
                        "narration": s,
                        "visual": s
                    })

    if not scenes:
        print("[script_polisher] Winner has no scenes. Structuring fallback...", flush=True)
        scenes = [{"scene_number": 1, "narration": raw_script, "visual": raw_script}]

    # Post-process all scenes in dialogue mode to guarantee speaker and voice_gender fields
    if mode == "dialogue":
        for idx, sc in enumerate(scenes):
            if not sc.get("speaker"):
                m = re.match(r'^([A-Za-z0-9_\s]{2,15})\s*:\s*(.*)', sc.get("narration", ""))
                if m:
                    sc["speaker"] = m.group(1).strip()
                    sc["narration"] = m.group(2).strip()
                else:
                    sc["speaker"] = "Character A" if idx % 2 == 0 else "Character B"
            if not sc.get("voice_gender"):
                sc["voice_gender"] = "female" if idx % 2 == 0 else "male"

    winner_script = json.dumps(scenes, ensure_ascii=False, indent=2)
    print(f"[script_polisher] === WINNER: {winner_name} ({len(scenes)} scenes, {mode_label} mode) ===\n", flush=True)
    return winner_script
