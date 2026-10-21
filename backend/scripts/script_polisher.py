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


TUTORIAL_SYSTEM_PROMPT = """You are an expert educational content creator specializing in slide-based tutorial and how-to YouTube Shorts.
Your job is to transform a raw tutorial topic into a clear, structured step-by-step presentation slide script.

Rules:
- Structure: Introduction (1 scene) + 4-7 numbered steps + optional Summary (1 scene). Total: 6-9 scenes.
- Total word count: 100-150 words (fits in 60-90 seconds of speech at a calm tutorial pace).
- Each scene = ONE educational slide. Spoken narration must be direct, simple, and calm (15-25 words per slide).
- For each scene, you MUST generate structured slide slide_title, bullets, and optional code_snippet:
  - slide_title: A bold, clear, descriptive title for the slide (e.g. "Step 1: Setup Workspace" or "List Comprehension syntax"). Max 6 words.
  - bullets: A strict JSON array containing exactly 2 to 3 short, punchy bullet points. Bullet points must be concise (max 8 words each) so they fit nicely on a vertical mobile screen.
  - code_snippet: Optional single line of code, CLI command, or key takeaway quote (e.g. "pip install edge-tts" or "fruits.append('kiwi')"). Leave empty string ("") if not applicable.
  - visual: A clean background/illustration prompt for the graphic card (e.g., "Flat-lay clean 3D icon of a database, vibrant cyan glow, modern studio background").
- Each scene must include a step_title: "Introduction", "Step 1" through "Step N", or "Summary".

Format the output as a strict, clean JSON array. No markdown, no extra text.

Expected JSON Structure:
[
  {
    "scene_number": 1,
    "step_title": "Introduction",
    "slide_title": "Learn Python Lists",
    "bullets": [
      "Ordered sequence of elements",
      "Defined using square brackets []",
      "Dynamic and mutable lists"
    ],
    "code_snippet": "my_list = [1, 2, 3]",
    "narration": "Today we'll learn about Python lists. Lists are highly flexible collections of ordered items that you can modify.",
    "visual": "A clean 3D cartoon styled graphic of a numbered list, soft blue lighting, white studio background..."
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
    Each scene is a dict with 'narration', 'visual', 'step_title', 'slide_title',
    'bullets', and 'code_snippet' keys.
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
                    step_title = item.get("step_title", "").strip()  # Tutorial Mode field
                    slide_title = item.get("slide_title", "").strip()
                    summary = item.get("summary", "").strip()
                    section_title = item.get("section_title", "").strip()
                    bullets = item.get("bullets", [])
                    code_snippet = item.get("code_snippet", "").strip()
                    layout_type = item.get("layout_type", "").strip()
                    
                    if narration or narration_hi:
                        scene = {
                            "narration": narration if narration else narration_hi,
                            "visual": visual if visual else (narration if narration else narration_hi)
                        }
                        if narration_hi:
                            scene["narration_hi"] = narration_hi
                        if step_title:
                            scene["step_title"] = step_title
                        if slide_title:
                            scene["slide_title"] = slide_title
                        if summary:
                            scene["summary"] = summary
                        if section_title:
                            scene["section_title"] = section_title
                        if bullets:
                            if isinstance(bullets, list):
                                # Keep dictionary bullet structures intact; otherwise convert to string
                                scene["bullets"] = [
                                    b if isinstance(b, dict) else str(b).strip()
                                    for b in bullets if b
                                ]
                            elif isinstance(bullets, str):
                                scene["bullets"] = [b.strip() for b in bullets.split("\n") if b.strip()]
                        if code_snippet:
                            scene["code_snippet"] = code_snippet
                        if layout_type:
                            scene["layout_type"] = layout_type
                        speaker = item.get("speaker", "").strip()
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
            clean_fallback_text = re.sub(r'\b(?:scene_number|narration|visual|step_title|scene)\b', ' ', clean_fallback_text, flags=re.IGNORECASE)
            clean_fallback_text = re.sub(r'\s+', ' ', clean_fallback_text).strip()
            
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_fallback_text) if len(s.strip()) > 10]
        for s in sentences:
            scenes.append({
                "narration": s,
                "visual": s
            })
            
    # Auto-recovery layer: Make sure all scenes have slide titles and bullets for tutorial mode
    for idx, scene in enumerate(scenes):
        if "step_title" in scene and "slide_title" not in scene:
            scene["slide_title"] = scene["step_title"]
        if "slide_title" not in scene:
            scene["slide_title"] = f"Step {idx + 1}" if idx > 0 else "Introduction"
            
        if "bullets" not in scene:
            # Generate 2 nice bullet points by splitting narration at punctuation clauses
            narr = scene.get("narration", "")
            clauses = [c.strip() for c in re.split(r'[,.!?]', narr) if len(c.strip()) > 6]
            if len(clauses) >= 2:
                scene["bullets"] = [clauses[0], clauses[1]]
            else:
                scene["bullets"] = [narr[:40] + "..." if len(narr) > 40 else narr, "Ready for the next step"]
                
        if "code_snippet" not in scene:
            scene["code_snippet"] = ""

    return scenes



def polish_with_pollinations(raw_script: str, system_prompt: str = None) -> str:
    """
    Polishes script using the centralized LLM client.
    """
    active_prompt = system_prompt or SYSTEM_PROMPT
    user_content = (
        f"Structure this into a tutorial storyboard for YouTube Shorts:\n\n{raw_script}"
        if system_prompt
        else f"Polish this script into a structured storyboard for YouTube Shorts:\n\n{raw_script}"
    )
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

    if mode == "tutorial":
        # --- TUTORIAL MODE SCORING ---
        # 1. Word Count Score (Ideal target of 100–150 words - max 40 points)
        if 100 <= word_count <= 150:
            score += 40.0
        elif 80 <= word_count < 100 or 150 < word_count <= 180:
            score += 25.0
        elif 50 <= word_count < 80 or 180 < word_count <= 220:
            score += 10.0
        else:
            score += 5.0

        # 2. Clarity / Pacing (Direct, actionable sentences: ideal 15–25 words per step - max 30 points)
        if scenes:
            avg_words_per_scene = word_count / len(scenes)
            if 15 <= avg_words_per_scene <= 25:
                score += 30.0
            elif 10 <= avg_words_per_scene < 15 or 25 < avg_words_per_scene <= 30:
                score += 20.0
            else:
                score += 10.0
        else:
            score += 10.0

        # 3. Structural Steps (Awards points for verified presence of "step_title" markers containing "Introduction", "Step", and "Summary" - max 30 points)
        has_intro = False
        has_step = False
        has_summary = False
        for scene in scenes:
            title = scene.get("step_title", "").lower()
            if "introduction" in title or "intro" in title:
                has_intro = True
            if "step" in title:
                has_step = True
            if "summary" in title or "conclusion" in title or "outro" in title:
                has_summary = True

        if has_intro:
            score += 10.0
        if has_step:
            score += 10.0
        if has_summary:
            score += 10.0
            
    else:
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



def query_gemini_for_question(question: str) -> dict:
    """
    Queries Google Gemini (or falls back to Pollinations LLM proxy) using the centralized LLM client.
    Returns a structured dictionary with a summary paragraph, section title, and key features.
    """
    import json
    
    prompt = (
        f"You are a world-class professional educational instructor.\n"
        f"For the question: '{question}', generate a structured JSON object containing a detailed, high-level summary paragraph and a list of exactly 5 key features.\n"
        f"The JSON MUST be formatted EXACTLY like this with no other text, markdown formatting, or wrappers:\n"
        f"{{\n"
        f"  \"summary\": \"[A highly professional, bold summary paragraph of 2-3 sentences, maximum 45-50 words, detailing the core definition and importance of the topic]\",\n"
        f"  \"section_title\": \"🔑 Key Features of [TopicName]\",\n"
        f"  \"bullets\": [\n"
        f"    {{\"title\": \"[Feature 1 Title (2-4 words)]\", \"description\": \"[Brief explanation of Feature 1, beginner-friendly]\"}},\n"
        f"    {{\"title\": \"[Feature 2 Title]\", \"description\": \"[Brief explanation]\"}},\n"
        f"    {{\"title\": \"[Feature 3 Title]\", \"description\": \"[Brief explanation]\"}},\n"
        f"    {{\"title\": \"[Feature 4 Title]\", \"description\": \"[Brief explanation]\"}},\n"
        f"    {{\"title\": \"[Feature 5 Title]\", \"description\": \"[Brief explanation]\"}}\n"
        f"  ]\n"
        f"}}\n"
        f"Choose an appropriate, professional, and matching emoji for the section_title (e.g. 🔑 for features, ⚙️ for mechanics, 🛠️ for tools, etc.).\n"
        f"Return ONLY the raw JSON string. Do not wrap it in ```json ... ``` blocks."
    )
    
    default_data = {
        "summary": f"{question.strip('? ').capitalize()} is an important technical concept that is widely used, highly scalable, and essential for modern developers and programmers.",
        "section_title": f"🔑 Key Features of {question.strip('? ').capitalize()}",
        "bullets": [
            {"title": "Easy to Learn", "description": "Designed with a simple, clear, and readable structure suitable for beginners."},
            {"title": "Highly Versatile", "description": "Applicable across web development, scripting, data operations, and automation."},
            {"title": "Open Source", "description": "Free to use, modify, and distribute with a massive global supportive community."},
            {"title": "Robust Ecosystem", "description": "Supported by thousands of external libraries, packages, and frameworks."},
            {"title": "High Demand", "description": "Widely adopted by top tech companies globally, offering excellent career growth."}
        ]
    }

    # Specific hardcoded answer for "python" question
    if "python" in question.lower():
        return {
            "summary": "Python is a high-level, open-source programming language known for its simplicity, readability, and versatility. It's widely used in web development, data science, artificial intelligence, automation, and more, making it one of the most popular languages globally.",
            "section_title": "🔑 Key Features of Python",
            "bullets": [
                {"title": "Easy to Learn & Read", "description": "Uses clear syntax and indentation, making it beginner-friendly."},
                {"title": "Cross-Platform", "description": "Runs on Windows, macOS, Linux, and even mobile operating systems."},
                {"title": "Open Source", "description": "Free to use, modify, and distribute under the Python Software Foundation license."},
                {"title": "Extensive Libraries", "description": "Thousands of modules available via PyPI (Python Package Index)."},
                {"title": "Versatile Applications", "description": "From web apps (Django, Flask) to machine learning (TensorFlow, PyTorch)."}
            ]
        }

    try:
        print(f"[script_polisher] Simple Q&A: Querying central LLM client for '{question}'...", flush=True)
        response_text = query_llm(prompt, response_format_json=True, temperature=0.4, max_tokens=500)
        if response_text:
            cleaned_json = clean_json_string(response_text)
            parsed = json.loads(cleaned_json)
            if parsed.get("summary") and parsed.get("bullets"):
                return parsed
    except Exception as e:
        print(f"[script_polisher] Simple Q&A querying failed: {e}", flush=True)

    return default_data


def polish_script(raw_script: str, mode: str = "shorts", language: str = "English") -> str:
    """
    Orchestrates script polishing. Supports modes:
      - 'shorts' (default): viral YouTube Shorts — 5-7 scenes, 60-80 words, hook-first.
      - 'dialogue': multi-character conversational banter — alternating 2 characters with speaker tags.
      - 'tutorial': instructional How-To — 6-9 numbered steps, 100-150 words, calm tone.
    language: target narration language (e.g. 'Hindi', 'Bengali'). Defaults to 'English'.
    """
    import json
    if mode == "tutorial":
        mode_label = "Tutorial"
    elif mode == "dialogue":
        mode_label = "Dialogue"
    else:
        mode_label = "Shorts"

    # Simple Question-Answer Detection for Tutorial Mode
    if mode == "tutorial":
        clean_raw = raw_script.strip().lower()
        is_simple_question = (
            clean_raw.endswith("?") or
            any(clean_raw.startswith(q) for q in ["what is", "how to", "why is", "explain", "define", "what are", "who is", "how does"])
        ) and len(raw_script.split()) < 15
        
        if is_simple_question:
            print(f"[script_polisher] Detected Simple Q&A Prompt: '{raw_script}'", flush=True)
            qa_data = query_gemini_for_question(raw_script)
            
            # Construct a beautiful, fluent narration reading out the summary and the complete bullet details (titles and descriptions)
            summary_text = qa_data.get("summary", "")
            section_name = qa_data.get("section_title", "").replace("🔑", "").replace("⚙️", "").replace("🛠️", "").strip()
            
            bullets_text_list = []
            for b in qa_data.get("bullets", []):
                title = b.get("title", "").strip().rstrip(".")
                desc = b.get("description", "").strip().rstrip(".")
                if title and desc:
                    bullets_text_list.append(f"{title}: {desc}")
                elif title:
                    bullets_text_list.append(title)
            
            narration_parts = [summary_text]
            if bullets_text_list:
                narration_parts.append(f"Regarding the {section_name}:")
                # Join with full stops so TTS pauses naturally between key points!
                narration_parts.append(". ".join(bullets_text_list) + ".")
            narration_text = " ".join(narration_parts)
            
            print(f"[script_polisher] Generated Narration: '{narration_text}'", flush=True)
            
            # Format custom slide scene with rich structured data
            formatted_title = raw_script.strip("? ").upper() + "?"
            scene = {
                "scene_number": 1,
                "step_title": "Q&A",
                "slide_title": formatted_title,
                "summary": qa_data.get("summary", ""),
                "section_title": qa_data.get("section_title", ""),
                "bullets": qa_data.get("bullets", []), # List of dicts [{"title": "...", "description": "..."}, ...]
                "code_snippet": "",
                "layout_type": "simple_qa",
                "narration": narration_text,
                "visual": f"A clean 3D illustration representing {raw_script}, glowing highlights, vector logo style"
            }
            return json.dumps([scene], ensure_ascii=False, indent=2)

    import concurrent.futures

    # Phase 1 & 2: Dynamic Style Meta-Prompting Layer
    style_modifiers = analyze_script_style(raw_script)
    if mode == "dialogue":
        base_prompt = DIALOGUE_SYSTEM_PROMPT
    elif mode == "tutorial":
        base_prompt = TUTORIAL_SYSTEM_PROMPT
    else:
        base_prompt = SYSTEM_PROMPT

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
