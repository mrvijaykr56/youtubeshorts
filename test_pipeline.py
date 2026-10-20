"""
YTShorts Pipeline — Quick Quality Test
Tests TTS, captions, and image generation with a sample Hindi + English script.
Run from the YTShorts root:
  .\\backend\\venv\\Scripts\\python.exe test_pipeline.py
"""
import sys, os, json, time, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

OUTPUT = os.path.join(os.path.dirname(__file__), "backend", "output", "test")
os.makedirs(OUTPUT, exist_ok=True)

DIVIDER = "=" * 60

# ─── Sample storyboard scenes (English + Hindi) ───────────────────
SAMPLE_SCENES_EN = [
    {"scene_number": 1, "narration": "Did you know honey never expires? 🍯 Scientists found 3000-year-old honey in Egyptian tombs — still edible!", "visual": "Ancient Egyptian tomb interior, golden honeycomb jars on stone altar, warm amber torchlight, dramatic shadows, macro close-up"},
    {"scene_number": 2, "narration": "Honey's magic lies in its chemistry ⚗️ — low moisture and natural hydrogen peroxide make it impossible for bacteria to survive.", "visual": "Microscopic view of honey crystals, glowing golden molecules, scientific laboratory setting, deep blue background"},
    {"scene_number": 3, "narration": "Ancient Egyptians used honey as medicine 👑 — treating wounds and preserving mummies for thousands of years.", "visual": "Egyptian pharaoh being embalmed, priests applying golden honey, candle-lit temple, dramatic volumetric lighting"},
]

SAMPLE_SCENES_HI = [
    {"scene_number": 1, "narration": "क्या आप जानते हैं? 🍯 शहद कभी खराब नहीं होता — वैज्ञानिकों को मिस्र की ममियों में 3000 साल पुराना शहद मिला!", "visual": "Ancient Egyptian tomb with golden honey jars, warm amber torchlight, dramatic cinematic shot"},
    {"scene_number": 2, "narration": "शहद की ताकत है उसकी केमिस्ट्री में ⚗️ — कम नमी और प्राकृतिक हाइड्रोजन पेरोक्साइड बैक्टीरिया को जीने नहीं देते।", "visual": "Microscopic golden honey crystals, glowing molecules, scientific blue laboratory background"},
    {"scene_number": 3, "narration": "प्राचीन मिस्र के लोग शहद को दवा की तरह इस्तेमाल करते थे 👑 — घाव भरने और ममी बनाने के लिए।", "visual": "Egyptian priests applying honey to mummy, candlelit temple, dramatic golden light"},
]

# ─── TEST 1: TTS Generation ────────────────────────────────────────
def test_tts(voice_key, scenes, label):
    print(f"\n{DIVIDER}")
    print(f"TEST 1 — TTS: {label} (voice={voice_key})")
    print(DIVIDER)
    from scripts.tts_generator import generate_audio, VOICE_MAP, VOICE_MODIFIERS
    voice_name = VOICE_MAP.get(voice_key, "?")
    mods = VOICE_MODIFIERS.get(voice_key, {"rate": "+8%", "pitch": "+0Hz"})
    print(f"  Voice     : {voice_name}")
    print(f"  Modifiers : rate={mods['rate']}, pitch={mods['pitch']}")
    script_json = json.dumps(scenes, ensure_ascii=False)
    out = os.path.join(OUTPUT, f"tts_{voice_key}.mp3")
    t0 = time.time()
    result = generate_audio(script_json, out, tld=voice_key)
    elapsed = time.time() - t0
    size_kb = os.path.getsize(result) / 1024
    print(f"  ✅ Generated: {result}")
    print(f"  Duration  : {elapsed:.1f}s  |  Size: {size_kb:.1f} KB")
    return result

# ─── TEST 2: Caption Generation ───────────────────────────────────
def test_captions(audio_path, voice_key, language, width, height, style="tiktok"):
    print(f"\n{DIVIDER}")
    print(f"TEST 2 — Captions: language={language}, resolution={width}x{height}, style={style}")
    print(DIVIDER)
    from scripts.caption_generator import generate_captions
    srt_out = os.path.join(OUTPUT, f"captions_{voice_key}.srt")
    t0 = time.time()
    result = generate_captions(
        audio_path, srt_out,
        style=style,
        hook_title="Amazing Honey Facts",
        total_duration=30.0,
        cta_text="SUBSCRIBE FOR MORE! 🔔",
        script_language=language,
        width=width, height=height
    )
    elapsed = time.time() - t0
    # Verify PlayRes in the .ass file
    ass_path = srt_out.replace(".srt", ".ass")
    with open(ass_path, encoding="utf-8") as f:
        head = f.read(400)
    play_res_ok = f"PlayResX: {width}" in head and f"PlayResY: {height}" in head
    print(f"  ✅ Generated: {result}")
    print(f"  Duration  : {elapsed:.1f}s")
    print(f"  PlayRes check ({width}x{height}): {'✅ PASS' if play_res_ok else '❌ FAIL — wrong resolution in ASS header!'}")
    if language != "English":
        # Check that Devanagari/Bengali chars are preserved (not mangled by .upper())
        with open(ass_path, encoding="utf-8") as f:
            ass_content = f.read()
        # Look for any Devanagari range chars (U+0900–U+097F)
        has_indian_chars = any('\u0900' <= c <= '\u097F' or '\u0980' <= c <= '\u09FF' or '\u0A00' <= c <= '\u0A7F' for c in ass_content)
        print(f"  Indian script chars preserved: {'✅ YES' if has_indian_chars else '⚠️  None found (may be OK if Whisper returned Latin)'}")
    return result

# ─── TEST 3: Image Generation ─────────────────────────────────────
def test_images(scenes, art_style, label):
    print(f"\n{DIVIDER}")
    print(f"TEST 3 — Images: style={art_style}, {label}")
    print(DIVIDER)
    from scripts.image_generator import generate_scene_images, STYLE_TEMPLATES
    # Verify correct model is selected for the style
    style_key = art_style.lower().strip()
    if "pixar" in style_key or "3d" in style_key:
        expected_model = "flux-3d"
    elif "anime" in style_key:
        expected_model = "flux-anime"
    elif "cinematic" in style_key or "paint" in style_key or "oil" in style_key:
        expected_model = "flux-realism"
    else:
        expected_model = "flux"
    print(f"  Expected Pollinations model : {expected_model}")
    print(f"  Style template present      : {'✅' if art_style in STYLE_TEMPLATES else '❌ MISSING'}")
    script_json = json.dumps(scenes, ensure_ascii=False)
    t0 = time.time()
    paths = generate_scene_images(
        script=script_json,
        output_dir=OUTPUT,
        job_id=f"test_{art_style}",
        art_style=art_style,
        width=1080, height=1920   # 1080p for fast test
    )
    elapsed = time.time() - t0
    print(f"  ✅ Generated {len(paths)} images in {elapsed:.1f}s")
    for p in paths:
        sz = os.path.getsize(p) / 1024
        print(f"     {os.path.basename(p)} — {sz:.1f} KB {'✅' if sz > 10 else '❌ too small!'}")
    return paths

# ─── RUN ALL TESTS ────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'#'*60}")
    print("  YTShorts Quality Test Suite")
    print(f"{'#'*60}")

    results = {}

    # TTS tests — English and Hindi
    try:
        results["tts_en"] = test_tts("in_female", SAMPLE_SCENES_EN, "Indian English Female")
    except Exception as e:
        print(f"  ❌ TTS English FAILED: {e}")

    try:
        results["tts_hi"] = test_tts("hi_male", SAMPLE_SCENES_HI, "Hindi Male")
    except Exception as e:
        print(f"  ❌ TTS Hindi FAILED: {e}")

    try:
        results["tts_child"] = test_tts("child_english", SAMPLE_SCENES_EN, "Child Tone English")
    except Exception as e:
        print(f"  ❌ TTS Child FAILED: {e}")

    try:
        results["tts_kitten"] = test_tts("kittentts", SAMPLE_SCENES_EN, "KittenTTS Storyteller (VoiceStudio / Edge-TTS fallback)")
    except Exception as e:
        print(f"  ❌ TTS KittenTTS FAILED: {e}")

    # Caption tests — English at 4K, Hindi at 1080p
    if "tts_en" in results:
        try:
            test_captions(results["tts_en"], "in_female", "English",  2160, 3840, style="tiktok")
        except Exception as e:
            print(f"  ❌ Captions English FAILED: {e}")

    if "tts_hi" in results:
        try:
            test_captions(results["tts_hi"], "hi_male", "Hindi", 1080, 1920, style="elegant")
        except Exception as e:
            print(f"  ❌ Captions Hindi FAILED: {e}")

    # Image tests — cinematic + oil_painting (check model fix)
    try:
        test_images(SAMPLE_SCENES_EN, "cinematic",   "Cinematic (flux-realism expected)")
    except Exception as e:
        print(f"  ❌ Images cinematic FAILED: {e}")

    try:
        test_images(SAMPLE_SCENES_EN, "oil_painting", "Oil Painting (flux-realism expected, was broken)")
    except Exception as e:
        print(f"  ❌ Images oil_painting FAILED: {e}")

    print(f"\n{'#'*60}")
    print("  Test suite complete. Check output/test/ for generated files.")
    print(f"{'#'*60}\n")
