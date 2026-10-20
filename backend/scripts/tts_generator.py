import asyncio
import os
import edge_tts
from gtts import gTTS

# ---------------------------------------------------------------------------
# VOICE_MAP  —  profile key  →  Edge TTS neural voice
# ---------------------------------------------------------------------------
VOICE_MAP = {
    # Indian English
    "in_female":     "en-IN-NeerjaNeural",
    "in_male":       "en-IN-PrabhatNeural",

    # Hindi
    "hi_female":     "hi-IN-SwaraNeural",
    "hi_male":       "hi-IN-MadhurNeural",

    # Bengali (India)
    "bn_female":     "bn-IN-TanishaaNeural",
    "bn_male":       "bn-IN-BashkarNeural",

    # Punjabi
    "pa_female":     "pa-IN-VaaniNeural",
    "pa_male":       "pa-IN-OjasNeural",

    # Bhojpuri — no native Edge TTS voice; best approximated via Hindi
    # with a slightly warmer, slower delivery
    "bho_female":    "hi-IN-SwaraNeural",
    "bho_male":      "hi-IN-MadhurNeural",

    # Child Tone — Indian English voice at high pitch + faster rate
    "child_english": "en-IN-NeerjaNeural",
    "child_hindi":   "hi-IN-SwaraNeural",

    # Local Storyteller (VoiceStudio KittenTTS)
    "kittentts":     "kittentts",
}

# ---------------------------------------------------------------------------
# VOICE_MODIFIERS  —  per-profile pitch / rate overrides
# Default (not listed) → rate="+8%", pitch="+0Hz"
# ---------------------------------------------------------------------------
VOICE_MODIFIERS = {
    # Bhojpuri: distinctly warmer, slower, more melodic than standard Hindi
    "bho_female":    {"rate": "-5%",  "pitch": "+8Hz"},
    "bho_male":      {"rate": "-5%",  "pitch": "+5Hz"},

    # Child Tone: high pitch + quick delivery for a genuine child-like quality
    "child_english": {"rate": "+25%", "pitch": "+30Hz"},
    "child_hindi":   {"rate": "+25%", "pitch": "+30Hz"},
}

# Maps voice profile key → human-readable language name passed to script polisher
VOICE_LANGUAGE_MAP = {
    "in_female":     "English",
    "in_male":       "English",
    "hi_female":     "Hindi",
    "hi_male":       "Hindi",
    "bn_female":     "Bengali",
    "bn_male":       "Bengali",
    "pa_female":     "Punjabi",
    "pa_male":       "Punjabi",
    "bho_female":    "Bhojpuri",
    "bho_male":      "Bhojpuri",
    "child_english": "English",
    "child_hindi":   "Hindi",
    "kittentts":     "English",
}

# gTTS lang code fallback per voice prefix
GTTS_LANG_MAP = {
    "hi-": "hi",
    "bn-": "bn",
    "pa-": "pa",
    "en-": "en",
}


_kittentts_instance = None

def get_kittentts_engine():
    """
    Returns a cached KittenTTS engine instance with automated phonemizer/espeak configuration.
    Runs 100% locally on CPU inside this project without any external servers.
    """
    global _kittentts_instance
    if _kittentts_instance is None:
        import espeakng_loader
        espeakng_loader.make_library_available()
        os.environ["ESPEAK_DATA_PATH"] = str(espeakng_loader.get_data_path())
        import phonemizer
        phonemizer.backend.EspeakBackend.set_library(espeakng_loader.get_library_path())
        from kittentts import KittenTTS
        print("[tts_generator] Initializing embedded KittenTTS local engine on CPU...", flush=True)
        _kittentts_instance = KittenTTS()
    return _kittentts_instance

def generate_kittentts_local(text: str, output_path: str, voice: str = "expr-voice-2-f") -> str:
    """
    Synthesizes audio using KittenTTS running embedded directly in this project.
    Converts raw 24kHz float audio to standard MP3.
    """
    import soundfile as sf
    import subprocess
    tts = get_kittentts_engine()
    audio = tts.generate(text, voice=voice, speed=1.0)
    temp_wav = output_path + ".temp.wav"
    sf.write(temp_wav, audio, 24000)
    subprocess.run(["ffmpeg", "-y", "-i", temp_wav, "-q:a", "2", output_path], check=True, capture_output=True)
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
    return output_path

def generate_audio(script_text, output_path, tld="com"):
    """
    Converts script text to high-fidelity audio using Microsoft Edge Neural TTS or embedded KittenTTS.
    Falls back to gTTS (Google Translate TTS) if offline or on error.
    Keeps the legacy `tld` argument name for full backward compatibility.
    """
    def clean_speech_text(text: str) -> str:
        import re
        text = re.sub(r'\[.*?\]', '', text)
        def clean_parentheses(match):
            content = match.group(1).strip()
            if len(content.split()) <= 4:
                return ""
            return f"({content})"
        text = re.sub(r'\((.*?)\)', clean_parentheses, text)
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    from scripts.script_polisher import parse_storyboard
    scenes = parse_storyboard(script_text)
    if scenes:
        spoken_text = " ... ".join([clean_speech_text(scene["narration"]) for scene in scenes])
    else:
        spoken_text = clean_speech_text(script_text)

    # Resolve voice and modifiers from profile key
    key = str(tld).lower().strip()

    # Special handling for KittenTTS — runs directly inside YTShorts!
    if key == "kittentts":
        print("[tts_generator] Running KittenTTS directly inside YTShorts (embedded engine)...", flush=True)
        try:
            generate_kittentts_local(spoken_text, output_path, voice="expr-voice-2-f")
            print(f"[tts_generator] [OK] Embedded KittenTTS generated {os.path.getsize(output_path)} bytes successfully.", flush=True)
        except Exception as local_err:
            print(f"[tts_generator] Embedded KittenTTS error ({local_err}). Checking VoiceStudio fallback...", flush=True)
            try:
                import requests
                payload = {
                    "model": "kittentts",
                    "input": spoken_text,
                    "voice": "kittentts",
                    "response_format": "mp3"
                }
                res = requests.post("http://127.0.0.1:3900/v1/audio/speech", json=payload, timeout=8)
                if res.status_code == 200 and len(res.content) > 1000:
                    with open(output_path, "wb") as f:
                        f.write(res.content)
                    print(f"[tts_generator] [OK] VoiceStudio KittenTTS generated {len(res.content)} bytes.", flush=True)
                else:
                    key = "child_english"
            except Exception:
                key = "child_english"

    voice = VOICE_MAP.get(key, key)  # pass-through if already a full voice name

    # Safety guard — default to Indian English if voice is unrecognised
    allowed_prefixes = ("en-IN", "hi-IN", "bn-IN", "pa-IN")
    if not any(voice.startswith(pref) for pref in allowed_prefixes):
        voice = "en-IN-NeerjaNeural"

    modifiers = VOICE_MODIFIERS.get(key, {})
    rate  = modifiers.get("rate",  "+8%")
    pitch = modifiers.get("pitch", "+0Hz")

    # If already generated via KittenTTS, skip running Edge TTS
    if not (os.path.exists(output_path) and os.path.getsize(output_path) > 1000):
        print(f"[tts_generator] Generating audio — voice: {voice}, rate: {rate}, pitch: {pitch}", flush=True)

    try:
        async def run_edge_tts():
            communicate = edge_tts.Communicate(spoken_text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)

        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, run_edge_tts())
                future.result(timeout=30)
        except RuntimeError:
            asyncio.run(run_edge_tts())

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            # Post-process: professional podcast broadcast audio mastering
            # 1. High-pass filter at 75Hz removes low-end sub-rumble
            # 2. Bass warmth shelf (+3dB at 120Hz) delivers Shure SM7B studio richness
            # 3. Presence equalizer (+1.5dB at 3kHz) enhances speech intelligibility
            # 4. Treble air shelf (+2.5dB at 8kHz) adds crystal-clear studio polish
            # 5. Smooth compand dynamics + broadcast-standard EBU R128 loudness (-16 LUFS)
            try:
                import subprocess
                norm_path = output_path + "._norm.mp3"
                mastering_filter = (
                    "highpass=f=75,"
                    "bass=g=3.0:f=120:w=0.6,"
                    "equalizer=f=3000:t=q:w=1.2:g=1.5,"
                    "treble=g=2.5:f=8000:w=0.5,"
                    "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-1:gain=2,"
                    "loudnorm=I=-16:TP=-1.5:LRA=11"
                )
                norm_result = subprocess.run([
                    "ffmpeg", "-y", "-i", output_path,
                    "-af", mastering_filter,
                    "-ar", "44100", "-b:a", "192k",
                    norm_path
                ], capture_output=True, timeout=30)
                if norm_result.returncode == 0 and os.path.exists(norm_path):
                    os.replace(norm_path, output_path)
                    print(f"[tts_generator] [OK] Professional podcast vocal mastering applied at {output_path}", flush=True)
                else:
                    print(f"[tts_generator] Warning: mastering failed, using raw TTS audio.", flush=True)
                    if os.path.exists(norm_path):
                        os.remove(norm_path)
            except Exception as norm_err:
                print(f"[tts_generator] Warning: loudnorm post-processing error: {norm_err}", flush=True)
            return output_path
        else:
            raise RuntimeError("Edge TTS generated file was empty or missing.")

    except Exception as e:
        print(f"[tts_generator] Edge TTS failed: {e}. Falling back to gTTS...", flush=True)
        try:
            lang = "en"
            fallback_tld = "co.in"
            for prefix, lang_code in GTTS_LANG_MAP.items():
                if voice.startswith(prefix):
                    lang = lang_code
                    break

            tts = gTTS(text=spoken_text, lang=lang, tld=fallback_tld)
            tts.save(output_path)
            print(f"[tts_generator] [OK] gTTS fallback saved to {output_path}", flush=True)
            return output_path
        except Exception as fallback_err:
            print(f"[tts_generator] [CRITICAL] gTTS also failed: {fallback_err}", flush=True)
            raise fallback_err


def generate_dialogue_speech(
    scenes: list[dict],
    voice_a: str = "in_female",
    voice_b: str = "in_male",
    output_path: str = "dialogue.mp3"
) -> str:
    """
    Synthesizes multi-character dialogue speech by alternating voices per character.
    voice_a: character A voice (e.g. female)
    voice_b: character B voice (e.g. male)
    Stitches individual dialogue turns together with natural 220ms conversational pauses.
    """
    from pydub import AudioSegment

    combined_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=220)
    speakers_seen = []

    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "").strip()
        if not narration:
            continue

        speaker = scene.get("speaker", "").strip()
        gender = scene.get("voice_gender", "").lower().strip()

        if speaker and speaker not in speakers_seen:
            speakers_seen.append(speaker)

        if gender == "male":
            chosen_voice = voice_b
        elif gender == "female":
            chosen_voice = voice_a
        elif speaker and len(speakers_seen) > 1 and speaker == speakers_seen[1]:
            chosen_voice = voice_b
        else:
            chosen_voice = voice_a if i % 2 == 0 else voice_b

        turn_out = output_path.replace(".mp3", f"_turn_{i:02d}.mp3")
        try:
            print(f"[tts_generator] Generating turn {i+1} ({speaker or 'Voice'}): {narration[:40]}... with voice '{chosen_voice}'", flush=True)
            generate_audio(narration, turn_out, tld=chosen_voice)
            if os.path.exists(turn_out) and os.path.getsize(turn_out) > 500:
                turn_segment = AudioSegment.from_file(turn_out)
                if len(combined_audio) > 0:
                    combined_audio += pause
                combined_audio += turn_segment
        finally:
            if os.path.exists(turn_out):
                try:
                    os.remove(turn_out)
                except Exception:
                    pass

    if len(combined_audio) == 0:
        raise RuntimeError("No dialogue speech audio could be generated.")

    combined_audio.export(output_path, format="mp3", bitrate="192k")
    print(f"[tts_generator] [OK] Multi-character dialogue master audio exported to {output_path} ({len(combined_audio)/1000.0:.2f}s)", flush=True)
    return output_path

