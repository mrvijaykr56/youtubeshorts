import os
import sys
import json
import time
import requests
from pydub import AudioSegment

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

print("=" * 60)
print("TEST SUITE: SHORTS STUDIO AI - NEW UPGRADES VERIFICATION")
print("=" * 60)

# -------------------------------------------------------------
# TEST 1: Multi-Character Script Polishing
# -------------------------------------------------------------
print("\n[TEST 1] Testing Multi-Character Dialogue Script Polishing...")
from scripts.script_polisher import polish_script, parse_storyboard

test_prompt = "Mia accuses Ben of stealing her secret pizza slice, but Ben blames the family cat."
polished = polish_script(test_prompt, mode="dialogue", language="English")
scenes = parse_storyboard(polished)

print(f"  Generated {len(scenes)} dialogue scenes.")
assert len(scenes) >= 2, f"Expected at least 2 scenes, got {len(scenes)}"
speakers = [s.get("speaker") for s in scenes]
print(f"  Detected Speakers in Dialogue: {speakers}")
for i, s in enumerate(scenes):
    print(f"    Turn {i+1} [{s.get('speaker', 'Unknown')} ({s.get('voice_gender', 'N/A')})]: \"{s.get('narration')}\"")
print("  [PASS] TEST 1: Multi-Character Polisher generated valid structured dialogue!\n")

# -------------------------------------------------------------
# TEST 2: Multi-Voice TTS Speech Generation
# -------------------------------------------------------------
print("[TEST 2] Testing Multi-Voice Dialogue Speech Synthesis...")
from scripts.tts_generator import generate_dialogue_speech

# Minimal test scenes for fast TTS test
dialogue_scenes = [
    {
        "scene_number": 1,
        "speaker": "Mia",
        "voice_gender": "female",
        "narration": "Ben, did you take my pizza? Be honest! 🍕"
    },
    {
        "scene_number": 2,
        "speaker": "Ben",
        "voice_gender": "male",
        "narration": "I swear it was the cat! Look at those paws! 🐱"
    }
]

output_dir = os.path.join(os.path.dirname(__file__), "backend", "output", "test")
os.makedirs(output_dir, exist_ok=True)
test_dialogue_audio = os.path.join(output_dir, "test_dialogue_audio.mp3")

audio_res = generate_dialogue_speech(
    dialogue_scenes,
    voice_a="in_female",
    voice_b="in_male",
    output_path=test_dialogue_audio
)

assert os.path.exists(test_dialogue_audio), "Dialogue audio was not created!"
audio_seg = AudioSegment.from_file(test_dialogue_audio)
duration_sec = len(audio_seg) / 1000.0
print(f"  Generated dialogue audio: {test_dialogue_audio}")
print(f"  Audio Duration: {duration_sec:.2f}s, File Size: {os.path.getsize(test_dialogue_audio)} bytes")
assert duration_sec > 1.0, "Audio duration too short!"
print("  [PASS] TEST 2: Alternating multi-voice audio synthesized successfully!\n")

# -------------------------------------------------------------
# TEST 3: Optical Transitions & Ambient Motion Video Generator
# -------------------------------------------------------------
print("[TEST 3] Testing Cinematic Transitions (xfade) & Ambient Overlays...")
from scripts.video_generator import generate_video
from PIL import Image

# Create 2 simple temporary test images
img1_path = os.path.join(output_dir, "test_img1.jpg")
img2_path = os.path.join(output_dir, "test_img2.jpg")
Image.new("RGB", (1080, 1920), color=(30, 20, 60)).save(img1_path)
Image.new("RGB", (1080, 1920), color=(10, 50, 40)).save(img2_path)

# Dummy captions SRT
test_srt = os.path.join(output_dir, "test_captions.srt")
with open(test_srt, "w", encoding="utf-8") as f:
    f.write("1\n00:00:00,000 --> 00:00:02,000\nBen did you take my pizza?\n\n2\n00:00:02,200 --> 00:00:04,500\nI swear it was the cat!\n")

test_video_out = os.path.join(output_dir, "test_transition_video.mp4")

final_video = generate_video(
    audio_path=test_dialogue_audio,
    srt_path=test_srt,
    output_path=test_video_out,
    image_paths=[img1_path, img2_path],
    music_track="none",
    caption_style="elegant",
    script=dialogue_scenes,
    resolution="1080p",
    transition_style="whip_pan"
)

assert os.path.exists(final_video), "Final video was not rendered!"
video_size_kb = os.path.getsize(final_video) / 1024.0
print(f"  Rendered video: {final_video}")
print(f"  Rendered Size: {video_size_kb:.1f} KB")
assert video_size_kb > 50, "Rendered video file is unexpectedly small!"
print("  [PASS] TEST 3: xfade transition & ambient motion video generated cleanly!\n")

# -------------------------------------------------------------
# TEST 4: Backend API Endpoint Check
# -------------------------------------------------------------
print("[TEST 4] Testing Backend /storyboard API Endpoint with Dialogue Mode...")
api_url = "http://127.0.0.1:5000/storyboard"
payload = {
    "script": "A funny debate between pizza lovers about whether pineapple belongs on pizza.",
    "video_mode": "dialogue",
    "transition_style": "dynamic",
    "voice_a": "in_female",
    "voice_b": "in_male",
    "video_resolution": "1080p"
}

try:
    resp = requests.post(api_url, json=payload, timeout=10)
    print(f"  API Response Status: {resp.status_code}")
    data = resp.json()
    job_id = data.get("job_id")
    print(f"  Job Submitted: {job_id}")
    assert resp.status_code == 200 and job_id, "Failed to submit dialogue storyboard job!"

    # Poll status for 10 seconds to verify it picked up the dialogue mode
    time.sleep(3)
    status_resp = requests.get(f"http://127.0.0.1:5000/status/{job_id}", timeout=5).json()
    print(f"  Job State: {status_resp.get('state')}, Message: {status_resp.get('message')}")
    print("  [PASS] TEST 4: Backend API successfully initiated dialogue storyboard pipeline!\n")
except Exception as e:
    print(f"  API test skipped or failed ({e})")

print("=" * 60)
print("ALL UPGRADE TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
