try:
    import whisper
except ImportError:
    whisper = None
import os
import re
import json

def select_available_font(preferred_fonts: list[str]) -> str:
    """
    Checks the Windows Fonts directory (if on Windows) to see if preferred fonts are installed.
    Returns the first matching preferred font, or the last font as a global fallback.
    """
    import sys
    if sys.platform == "win32":
        fonts_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
        try:
            installed_files = os.listdir(fonts_dir)
            installed_files_lower = [f.lower() for f in installed_files]
            
            for font in preferred_fonts:
                font_normalized = font.lower().replace(" ", "")
                for file in installed_files_lower:
                    if font_normalized in file and (file.endswith(".ttf") or file.endswith(".otf")):
                        return font
        except Exception:
            pass
            
    # Default to the first preferred font as FFmpeg handles internal fallbacks if needed
    return preferred_fonts[0]

_whisper_model_cache: dict = {}
_faster_whisper_model_cache: dict = {}

def get_whisper_model(model_name="small"):
    """
    Returns a cached OpenAI Whisper model. Cache is keyed by model name so different
    model sizes can coexist without silently returning the wrong model.
    """
    global _whisper_model_cache
    if model_name not in _whisper_model_cache:
        if whisper is None:
            raise ImportError("openai-whisper is not installed.")
        print(f"[caption_generator] Loading OpenAI Whisper model '{model_name}' into memory (lazy cache)...", flush=True)
        _whisper_model_cache[model_name] = whisper.load_model(model_name)
    return _whisper_model_cache[model_name]

def get_faster_whisper_model(model_name="small"):
    """
    Returns a cached Faster-Whisper model using 8-bit quantized CPU inference
    for ~5-10x faster execution and low RAM consumption.
    """
    global _faster_whisper_model_cache
    if model_name not in _faster_whisper_model_cache:
        from faster_whisper import WhisperModel
        print(f"[caption_generator] Loading Faster-Whisper model '{model_name}' (device=cpu, compute_type=int8)...", flush=True)
        _faster_whisper_model_cache[model_name] = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _faster_whisper_model_cache[model_name]

# Maps voice language name → Whisper language code for accurate transcription
WHISPER_LANGUAGE_MAP = {
    "English":  "en",
    "Hindi":    "hi",
    "Bengali":  "bn",
    "Punjabi":  "pa",
    "Bhojpuri": "hi",  # Closest supported language
}

def generate_captions(audio_path, output_srt_path, style="elegant", hook_title="",
                      total_duration=0.0, cta_text="", script_language="English",
                      width=1080, height=1920):
    """
    Transcribes the given audio file using Faster-Whisper (with automatic fallback
    to OpenAI Whisper) and saves the output as an ASS (Advanced SubStation Alpha) subtitle file.
    script_language: narration language (e.g. 'Hindi') — used to pick Whisper model size
                     and pass the correct language code to Whisper for better accuracy.
    width/height: output video resolution — used to set ASS PlayRes correctly.
    Returns the path of the generated ASS file.
    """
    output_ass_path = output_srt_path.replace(".srt", ".ass")
    whisper_lang = WHISPER_LANGUAGE_MAP.get(script_language, "en")

    # Use 'medium' model for Indian languages — 'small' has poor accuracy on Devanagari/Bengali/Gurmukhi
    model_name = "medium" if script_language != "English" else "small"

    segments = None

    # Step 1: Try ultra-fast Faster-Whisper (5-second transcription on CPU)
    try:
        fw_model = get_faster_whisper_model(model_name)
        print(f"[caption_generator] Transcribing with Faster-Whisper '{model_name}', language='{whisper_lang}' (style: {style})...", flush=True)
        fw_segments_gen, _ = fw_model.transcribe(audio_path, word_timestamps=True, language=whisper_lang)
        segments = []
        for seg in fw_segments_gen:
            words = []
            if seg.words:
                for w in seg.words:
                    words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                    })
            segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "words": words,
            })
        print(f"[caption_generator] [OK] Faster-Whisper produced {len(segments)} segments successfully.", flush=True)
    except Exception as fw_err:
        print(f"[caption_generator] Faster-Whisper notice: {fw_err}. Falling back to standard Whisper...", flush=True)
        segments = None

    # Step 2: Fallback to standard OpenAI Whisper
    if segments is None:
        try:
            model = get_whisper_model(model_name)
            print(f"[caption_generator] Transcribing with OpenAI Whisper '{model_name}', language='{whisper_lang}' (style: {style})...", flush=True)
            result = model.transcribe(audio_path, word_timestamps=True, language=whisper_lang)
            segments = result.get("segments", [])
        except Exception as e:
            print(f"[caption_generator] Whisper failed: {e}. Falling back to placeholder captions.", flush=True)
            duration = total_duration if total_duration > 0 else 15.0
            segments = [{"start": 0.0, "end": duration,
                         "text": hook_title if hook_title else "AI Shorts Studio", "words": []}]

    if style in ["tiktok", "viral"]:
        if style == "viral":
            generate_ass_viral_hype(segments, output_ass_path, hook_title=hook_title,
                                    total_duration=total_duration, cta_text=cta_text,
                                    width=width, height=height)
        else:
            generate_ass_tiktok(segments, output_ass_path, hook_title=hook_title,
                                total_duration=total_duration, cta_text=cta_text,
                                width=width, height=height)
    else:
        generate_ass_elegant(segments, output_ass_path, hook_title=hook_title,
                             total_duration=total_duration, cta_text=cta_text,
                             width=width, height=height)
        
    # Save Whisper segment timestamps to a JSON metadata file for video alignment
    try:
        segment_times = [
            {"start": seg["start"], "end": seg["end"], "text": seg.get("text", "").strip()}
            for seg in segments
        ]
        segments_json_path = output_srt_path.replace(".srt", "_segments.json")
        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segment_times, f, indent=4)
        print(f"[caption_generator] Segment metadata saved to {segments_json_path}", flush=True)
    except Exception as e:
        print(f"[caption_generator] Warning: failed to save segments metadata JSON: {e}", flush=True)

    print(f"[caption_generator] [OK] ASS subtitles saved to {output_ass_path}", flush=True)
    return output_ass_path


def format_ass_time(seconds: float) -> str:
    """
    Converts seconds into ASS timestamp format (H:MM:SS.cs)
    """
    if seconds < 0:
        seconds = 0.0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int(round((seconds - int(seconds)) * 100))
    if centiseconds == 100:
        secs += 1
        centiseconds = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def chunk_words_semantically(all_words, max_size=3, max_chars=18):
    """
    Groups words into short, visually stable phrases. Ends a chunk early if
    a word ends with punctuation or character length exceeds vertical-screen safety bounds.
    """
    chunks = []
    current_chunk = []
    current_chars = 0
    
    for w in all_words:
        word_clean = w["word"]
        raw_word = w.get("raw_word", "")
        
        # Determine if adding this word triggers a boundary split
        should_split = False
        if len(current_chunk) >= max_size:
            should_split = True
        # Accounts for cumulative word length plus space delimiters
        elif current_chunk and (current_chars + len(word_clean) + len(current_chunk) > max_chars):
            should_split = True
            
        if should_split and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_chars = 0
            
        current_chunk.append(w)
        current_chars += len(word_clean)
        
        # End chunk early at sentence-ending punctuation only (. ! ?)
        # Commas and semicolons are clause-internal and must NOT split, as they
        # would produce awkward single-word subtitle flashes mid-phrase.
        if raw_word:
            clean_raw = raw_word.strip()
            if clean_raw and clean_raw[-1] in ".!?":
                chunks.append(current_chunk)
                current_chunk = []
                current_chars = 0
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return [c for c in chunks if c]


def generate_ass_tiktok(segments, output_ass_path, hook_title="", total_duration=0.0,
                        cta_text="", width=1080, height=1920):
    """
    Generates an ASS subtitle file with word-by-word highlights.
    Groups words into short phrases (max 3 words) using smart semantic chunking
    while highlighting the active spoken word in vibrant yellow.
    """
    all_words = []
    for segment in segments:
        if "words" in segment:
            for w in segment["words"]:
                word_text = w["word"].strip()
                # For Indian scripts preserve original casing; uppercase only Latin
                if word_text.isascii():
                    word_clean = re.sub(r'[^a-zA-Z0-9\']', '', word_text)
                else:
                    word_clean = word_text.strip()
                if word_clean:
                    all_words.append({
                        "word": word_clean.upper() if word_clean.isascii() else word_clean,
                        "raw_word": word_text,
                        "start": w["start"],
                        "end": w["end"]
                    })
        else:
            # Fallback if words timestamps key is missing in some segment
            words = segment.get("text", "").split()
            seg_duration = segment["end"] - segment["start"]
            if words:
                word_dur = seg_duration / len(words)
                for j, w in enumerate(words):
                    if w.isascii():
                        word_clean = re.sub(r'[^a-zA-Z0-9\']', '', w)
                    else:
                        word_clean = w.strip()
                    if word_clean:
                        all_words.append({
                            "word": word_clean.upper() if word_clean.isascii() else word_clean,
                            "raw_word": w,
                            "start": segment["start"] + j * word_dur,
                            "end": segment["start"] + (j + 1) * word_dur
                        })
                        
    # Group words into chunks semantically (max 3 words)
    chunks = chunk_words_semantically(all_words, max_size=3, max_chars=18)
        
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("ScriptType: v4.00+\n")
        f.write(f"PlayResX: {width}\n")
        f.write(f"PlayResY: {height}\n\n")
        
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Select premium geometric font (Montserrat with Arial Black fallback)
        active_font = select_available_font(["Montserrat", "Arial Black"])
        # Style definition: Alignment 5 = Middle-centered, Font, Size 80 (bigger & bolder), Primary White, Outline Black, OutlineWidth 4, Shadow 3 (high contrast shadow)
        f.write(f"Style: Default,{active_font},80,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,3,5,30,30,0,1\n")
        if hook_title:
            f.write(f"Style: HookTitle,{active_font},105,&H0000FFFF,&H00000000,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,0,8,30,30,220,1\n")
        if cta_text:
            f.write(f"Style: OutroTitle,{active_font},95,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,3,5,30,30,0,1\n")
        f.write("\n")
        
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        if hook_title:
            f.write(f"Dialogue: 0,0:00:00.00,0:00:03.00,HookTitle,,0,0,0,,{hook_title.upper()}\n")
        
        for chunk in chunks:
            if not chunk:
                continue
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]
            
            # Create dialogue events for each word in the chunk
            for active_idx in range(len(chunk)):
                start_time = format_ass_time(chunk[active_idx]["start"])
                # End time: start of next word, or chunk end + 150ms trailing buffer
                # (Whisper word-end timestamps tend to be 50-100ms early; the buffer
                # prevents the last highlighted word from vanishing too quickly.)
                if active_idx < len(chunk) - 1:
                    end_time = format_ass_time(chunk[active_idx + 1]["start"])
                else:
                    end_time = format_ass_time(chunk_end + 0.15)
                    
                # Build the text with active word highlighted
                words_styled = []
                for idx, w in enumerate(chunk):
                    if idx == active_idx:
                        # Highlight active word in golden yellow (&H0000FFFF&) and swell size to 115% for TikTok pop effect
                        words_styled.append(f"{{\\fscx115\\fscy115\\c&H0000FFFF&}}{w['word']}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}")
                    else:
                        words_styled.append(w["word"])
                        
                dialogue_text = " ".join(words_styled)
                
                # --- ADAPTIVE FONT SIZING FOR TIKTOK ---
                # Default style size is 80. Reduce font size if the phrase is long to prevent line wrapping.
                raw_chunk_text = " ".join(w["word"] for w in chunk)
                total_chars = len(raw_chunk_text)
                if total_chars > 20:
                    font_size = 62
                elif total_chars > 14:
                    font_size = 72
                else:
                    font_size = 80
                dialogue_text = f"{{\\fs{font_size}}}" + dialogue_text
                
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{dialogue_text}\n")


def generate_ass_elegant(segments, output_ass_path, hook_title="", total_duration=0.0,
                         cta_text="", width=1080, height=1920):
    """
    Generates an elegant bottom-aligned ASS subtitle file.
    Word data (if available) is chunked into max 3-word groups for readability.
    Falls back to raw segment text if no word-level data is present.
    """
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("ScriptType: v4.00+\n")
        f.write(f"PlayResX: {width}\n")
        f.write(f"PlayResY: {height}\n\n")
        
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        active_font = select_available_font(["Inter", "Trebuchet MS", "Arial"])
        f.write(f"Style: Default,{active_font},48,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2.5,1.5,2,30,30,100,1\n")
        if hook_title:
            f.write(f"Style: HookTitle,{active_font},100,&H0000FFFF,&H00000000,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,0,8,30,30,220,1\n")
        if cta_text:
            f.write(f"Style: OutroTitle,{active_font},95,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,3,5,30,30,0,1\n")
        f.write("\n")
        
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        if hook_title:
            f.write(f"Dialogue: 0,0:00:00.00,0:00:03.00,HookTitle,,0,0,0,,{hook_title.upper()}\n")
        
        for segment in segments:
            if "words" in segment and segment["words"]:
                # Chunk word-level data into short phrases (max 3 words) for readability
                all_words = []
                for w in segment["words"]:
                    word_text = w["word"].strip()
                    word_clean = re.sub(r'[^a-zA-Z0-9\'\-,!?.]', '', word_text)
                    if word_clean:
                        all_words.append({
                            "word": word_clean,
                            "raw_word": word_text,
                            "start": w["start"],
                            "end": w["end"]
                        })
                chunks = chunk_words_semantically(all_words, max_size=3, max_chars=24)
                for chunk in chunks:
                    if not chunk:
                        continue
                    start_time = format_ass_time(chunk[0]["start"])
                    end_time = format_ass_time(chunk[-1]["end"])
                    text = " ".join(w["word"] for w in chunk)
                    
                    # --- ADAPTIVE FONT SIZING FOR ELEGANT (CHUNKED) ---
                    # Default style size is 48.
                    total_chars = len(text)
                    if total_chars > 22:
                        font_size = 38
                    elif total_chars > 16:
                        font_size = 44
                    else:
                        font_size = 48
                    text = f"{{\\fs{font_size}}}" + text
                    
                    f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
            else:
                # Fallback: use full segment text if no word timestamps
                start_time = format_ass_time(segment["start"])
                end_time = format_ass_time(segment["end"])
                text = segment["text"].strip()
                
                # --- ADAPTIVE FONT SIZING FOR ELEGANT (RAW SEGMENT FALLBACK) ---
                # Default style size is 48.
                total_chars = len(text)
                if total_chars > 35:
                    font_size = 32
                elif total_chars > 24:
                    font_size = 40
                else:
                    font_size = 48
                text = f"{{\\fs{font_size}}}" + text
                
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
                
        if total_duration > 0 and cta_text:
            outro_start = format_ass_time(total_duration)
            outro_end = format_ass_time(total_duration + 2.0)
            f.write(f"Dialogue: 0,{outro_start},{outro_end},OutroTitle,,0,0,0,,{{\\fscx115\\fscy115\\c&H0000FFFF&}}{cta_text.upper()}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}\n")


EMOJI_MAP = {
    # Space & Cosmic
    "space": "🚀", "planet": "🪐", "star": "⭐", "earth": "🌍", "alien": "👽", "rocket": "🚀",
    "moon": "🌙", "sun": "☀️", "galaxy": "🌌", "universe": "🌌", "nasa": "🚀",
    "asteroid": "☄️", "comet": "☄️", "blackhole": "🕳️", "telescope": "🔭",
    # Wealth & Success
    "money": "💰", "cash": "💵", "rich": "🤑", "gold": "🪙", "diamond": "💎", "crypto": "🪙",
    "bitcoin": "🪙", "dollar": "💵", "pay": "💳", "buy": "🛍️", "sell": "📈",
    "growth": "📈", "build": "🔨", "success": "🏆", "win": "🏆", "lose": "❌",
    "business": "💼", "boss": "👑", "profit": "💰", "invest": "📈", "stock": "📊",
    # Emotions & Reactions
    "shocking": "😱", "shocked": "😱", "mindblowing": "🤯", "crazy": "🤪", "insane": "🤯",
    "fear": "😨", "angry": "😡", "sad": "😢", "happy": "😊", "love": "❤️",
    "heart": "❤️", "danger": "⚠️", "alert": "🚨", "warning": "⚠️", "secret": "🤫",
    "hidden": "🔍", "mystery": "🕵️", "wow": "😮", "omg": "😱", "incredible": "🤯",
    # Science & Smart
    "science": "🔬", "scientist": "👨‍🔬", "brain": "🧠", "smart": "💡", "idea": "💡",
    "genius": "🧠", "knowledge": "📚", "book": "📚", "read": "📖", "learn": "🎓",
    "teach": "👨‍🏫", "microscope": "🔬", "virus": "🦠", "bacteria": "🦠",
    "experiment": "🧪", "dna": "🧬", "chemistry": "⚗️", "atom": "⚛️",
    # Time & History
    "time": "⏱️", "year": "📅", "history": "📜", "ancient": "🏛️", "pyramid": "📐",
    "clock": "⏰", "watch": "⌚", "stopwatch": "⏱️", "calendar": "📅", "future": "🚀",
    "past": "📜", "egypt": "🇪🇬", "pharaoh": "👑", "king": "👑", "queen": "👑",
    "medieval": "⚔️", "century": "📜", "decade": "📅", "era": "🏛️",
    # Geography & Nations
    "china": "🇨🇳", "india": "🇮🇳", "usa": "🇺🇸", "america": "🇺🇸", "russia": "🇷🇺",
    "japan": "🇯🇵", "europe": "🌍", "africa": "🌍", "ocean": "🌊", "sea": "🌊",
    "mountain": "⛰️", "desert": "🏜️", "jungle": "🌴", "arctic": "❄️", "coral": "🪸",
    # Elements & Physics
    "fire": "🔥", "hot": "🔥", "burn": "🔥", "cold": "❄️", "ice": "❄️", "water": "💧",
    "fish": "🐟", "shark": "🦈", "whale": "🐋", "light": "💡", "dark": "🌑",
    "shadow": "👤", "lightning": "⚡", "storm": "⛈️", "nuclear": "☢️", "radiation": "☢️",
    "gravity": "🌍", "magnet": "🧲", "electricity": "⚡",
    # Food & Health
    "food": "🍔", "honey": "🍯", "sweet": "🍬", "eat": "😋", "coffee": "☕",
    "tea": "🍵", "drink": "🥤", "apple": "🍎", "banana": "🍌", "muscle": "💪",
    "gym": "🏋️", "fit": "💪", "strong": "💪", "weak": "🥀", "doctor": "👨‍⚕️",
    "health": "🏥", "medicine": "💊", "hospital": "🏥", "sick": "🤒", "cure": "💊",
    # Animals & Nature
    "dog": "🐶", "cat": "🐱", "animal": "🦁", "pet": "🐾", "lion": "🦁",
    "tiger": "🐯", "bear": "🐻", "snake": "🐍", "bird": "🐦", "tree": "🌳",
    "flower": "🌸", "nature": "🌲", "climate": "🌡️", "environment": "🌿",
    "bee": "🐝", "spider": "🕷️", "wolf": "🐺", "eagle": "🦅", "dinosaur": "🦕",
    # Technology & Action
    "car": "🚗", "speed": "⚡", "fast": "⚡", "slow": "🐢", "run": "🏃",
    "jump": "🦘", "fly": "✈️", "drive": "🚗", "game": "🎮", "play": "🎮",
    "tech": "💻", "computer": "💻", "phone": "📱", "ai": "🤖", "robot": "🤖",
    "camera": "📷", "photo": "📸", "video": "🎥", "movie": "🎬", "film": "🎬",
    "internet": "🌐", "satellite": "🛰️", "drone": "🚁", "submarine": "🤿",
    # War & Danger
    "death": "💀", "dead": "💀", "kill": "☠️", "fight": "⚔️", "war": "⚔️",
    "weapon": "⚔️", "gun": "🔫", "bomb": "💣", "explosion": "💥", "smoke": "💨",
    "military": "🎖️", "army": "⚔️", "soldier": "🪖", "nuclear": "☢️",
    # Society
    "city": "🏙️", "night": "🌙", "skull": "💀", "ghost": "👻", "vampire": "🧛",
    # General
    "world": "🌐", "people": "👥", "man": "👨", "woman": "👩", "baby": "👶",
    "house": "🏠", "building": "🏢", "flag": "🚩", "map": "🗺️", "music": "🎵",
    "song": "🎶", "sing": "🎤", "guitar": "🎸", "piano": "🎹",
    # Adjectives & Logic
    "easy": "✅", "hard": "🧱", "real": "💯", "fake": "❌", "stop": "🛑",
    "look": "👀", "listen": "👂", "truth": "💯", "lie": "🤥", "proof": "📋"
}


def get_contextual_emoji(word: str) -> str:
    """
    Looks up and matches emojis for words using a lightweight stemming process
    (stripping punctuation, plurals, gerunds, past tense, and adverbs).
    """
    word_lower = word.lower().strip()
    word_lower = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', word_lower)
    if not word_lower:
        return ""
        
    # 1. Direct match
    if word_lower in EMOJI_MAP:
        return EMOJI_MAP[word_lower]
        
    # 2. Plural strip
    if word_lower.endswith("s") and len(word_lower) > 3:
        stem = word_lower[:-1]
        if stem in EMOJI_MAP:
            return EMOJI_MAP[stem]
        if word_lower.endswith("es") and len(word_lower) > 4:
            stem = word_lower[:-2]
            if stem in EMOJI_MAP:
                return EMOJI_MAP[stem]
                
    # 3. Gerund strip
    if word_lower.endswith("ing") and len(word_lower) > 5:
        stem = word_lower[:-3]
        if stem in EMOJI_MAP:
            return EMOJI_MAP[stem]
        # double consonants, e.g. running -> run
        if len(stem) > 3 and stem[-1] == stem[-2]:
            stem_single = stem[:-1]
            if stem_single in EMOJI_MAP:
                return EMOJI_MAP[stem_single]
                
    # 4. Past tense strip
    if word_lower.endswith("ed") and len(word_lower) > 4:
        stem = word_lower[:-2]
        if stem in EMOJI_MAP:
            return EMOJI_MAP[stem]
        if stem.endswith("i"): # e.g. cried -> cry
            stem_y = stem[:-1] + "y"
            if stem_y in EMOJI_MAP:
                return EMOJI_MAP[stem_y]
                
    # 5. Adverb strip
    if word_lower.endswith("ly") and len(word_lower) > 4:
        stem = word_lower[:-2]
        if stem in EMOJI_MAP:
            return EMOJI_MAP[stem]
            
    return ""


def generate_ass_viral_hype(segments, output_ass_path, hook_title="", total_duration=0.0,
                            cta_text="", width=1080, height=1920):
    """
    Generates an ASS subtitle file with rapid 1-2 word chunks, rotating neon highlights,
    and automated contextual emojis.
    """
    all_words = []
    for segment in segments:
        if "words" in segment:
            for w in segment["words"]:
                word_text = w["word"].strip()
                if word_text.isascii():
                    word_clean = re.sub(r'[^a-zA-Z0-9\']', '', word_text)
                else:
                    word_clean = word_text.strip()
                if word_clean:
                    all_words.append({
                        "word": word_clean.upper() if word_clean.isascii() else word_clean,
                        "raw_word": word_text,
                        "start": w["start"],
                        "end": w["end"]
                    })
        else:
            # Fallback if words timestamps key is missing in some segment
            words = segment.get("text", "").split()
            seg_duration = segment["end"] - segment["start"]
            if words:
                word_dur = seg_duration / len(words)
                for j, w in enumerate(words):
                    word_clean = re.sub(r'[^a-zA-Z0-9\']', '', w)
                    if word_clean:
                        all_words.append({
                            "word": word_clean.upper(),
                            "raw_word": w,
                            "start": segment["start"] + j * word_dur,
                            "end": segment["start"] + (j + 1) * word_dur
                        })
                        
    # Group words into chunks of max 2 words for extreme pacing using smart semantic chunker
    chunks = chunk_words_semantically(all_words, max_size=2, max_chars=14)
        
    colors = ["&H0000FFFF&", "&H0000FF00&", "&H00FFFF00&", "&H00FF00FF&"]
    
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("ScriptType: v4.00+\n")
        f.write(f"PlayResX: {width}\n")
        f.write(f"PlayResY: {height}\n\n")
        
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Select premium geometric font (Montserrat with Arial Black fallback)
        active_font = select_available_font(["Montserrat", "Arial Black"])
        # Bold, Size 88 (large neon look), Primary White, Outline Black, OutlineWidth 5, Shadow 3 (3D pop), Alignment 5
        f.write(f"Style: Default,{active_font},88,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,5,3,5,30,30,0,1\n")
        if hook_title:
            f.write(f"Style: HookTitle,{active_font},105,&H0000FFFF,&H00000000,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,0,8,30,30,220,1\n")
        if cta_text:
            f.write(f"Style: OutroTitle,{active_font},95,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,3,5,30,30,0,1\n")
        f.write("\n")
        
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        if hook_title:
            f.write(f"Dialogue: 0,0:00:00.00,0:00:03.00,HookTitle,,0,0,0,,{hook_title.upper()}\n")
        
        for chunk_idx, chunk in enumerate(chunks):
            if not chunk:
                continue
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]
            
            # Create dialogue events for each word in the chunk
            for active_idx in range(len(chunk)):
                start_time = format_ass_time(chunk[active_idx]["start"])
                if active_idx < len(chunk) - 1:
                    end_time = format_ass_time(chunk[active_idx + 1]["start"])
                else:
                    end_time = format_ass_time(chunk_end)
                    
                # Build the text with active word highlighted and optional emoji
                words_styled = []
                for idx, w in enumerate(chunk):
                    if idx == active_idx:
                        # Select rotating color for this highlight
                        highlight_color = colors[(chunk_idx + active_idx) % len(colors)]
                        
                        # Check for contextual emoji using our smart stemmer
                        emoji = get_contextual_emoji(w['word'])
                        word_with_emoji = f"{w['word']} {emoji}".strip() if emoji else w['word']
                        
                        # Active word swells to 120% and changes to rotating neon color
                        words_styled.append(f"{{\\fscx120\\fscy120\\c{highlight_color}}}{word_with_emoji}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}")
                    else:
                        words_styled.append(w["word"])
                        
                dialogue_text = " ".join(words_styled)
                
                # --- ADAPTIVE FONT SIZING FOR VIRAL HYPE ---
                # Default style size is 88. Contextual Emojis add to visual length.
                raw_chunk_text = " ".join(w["word"] for w in chunk)
                total_chars = len(raw_chunk_text)
                if total_chars > 16:
                    font_size = 68
                elif total_chars > 11:
                    font_size = 78
                else:
                    font_size = 88
                dialogue_text = f"{{\\fs{font_size}}}" + dialogue_text
                
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{dialogue_text}\n")
                
        if total_duration > 0 and cta_text:
            outro_start = format_ass_time(total_duration)
            outro_end = format_ass_time(total_duration + 2.0)
            f.write(f"Dialogue: 0,{outro_start},{outro_end},OutroTitle,,0,0,0,,{{\\fscx115\\fscy115\\c&H0000FFFF&}}{cta_text.upper()}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}\n")
