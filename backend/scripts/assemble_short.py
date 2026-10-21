"""
YTShorts Standalone Assembly Script
Assembles a complete, broadcast-quality YouTube Short from a validated storyboard JSON
and generated images (scene_1.jpg, scene_2.jpg, ...).

Steps:
1. Reads script.json and validates image assets.
2. Generates TTS narration audio via Edge-TTS / KittenTTS.
3. Transcribes and generates synchronized .ass subtitles via Whisper.
4. Assembles final 1080p/4K MP4 with Ken Burns motion, xfade transitions, audio ducking, and subtitle burn.
"""

import os
import sys
import json
import glob
import re
import argparse

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def assemble_short(
    job_dir: str,
    voice: str = "in_female",
    caption_style: str = "tiktok",
    caption_lang: str = "English",
    music_track: str = "none",
    resolution: str = "1080p",
    transition_style: str = "dynamic"
) -> str:
    """
    Assembles a finalized YouTube Short from job_dir containing script.json and scene_*.jpg/png.
    Returns path to finalized mp4.
    """
    job_dir = os.path.abspath(job_dir)
    print(f"\n{'='*65}")
    print(f"🎬 ASSEMBLING YOUTUBE SHORT: {os.path.basename(job_dir)}")
    print(f"{'='*65}")

    # 1. Load storyboard
    script_file = os.path.join(job_dir, "script.json")
    if not os.path.exists(script_file):
        raise FileNotFoundError(f"Missing script.json in {job_dir}")

    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", script_data) if isinstance(script_data, dict) else script_data
    if not isinstance(scenes, list) or len(scenes) == 0:
        raise ValueError("script.json does not contain a valid list of scenes")

    print(f"  Loaded {len(scenes)} scenes from script.json")

    # Run pre-flight storyboard validation
    try:
        from scripts.storyboard_validator import validate_storyboard
        val_res = validate_storyboard(scenes)
        if not val_res.get("valid", True):
            print(f"  ⚠️ Storyboard validation warnings/errors:")
            for w in val_res.get("warnings", []):
                print(f"     - [WARN] {w}")
            for e in val_res.get("errors", []):
                print(f"     - [ERROR] {e}")
        else:
            print(f"  ✅ Pre-flight Storyboard Validation Passed ({val_res.get('word_count', 0)} words, est {val_res.get('estimated_duration_s', 0):.1f}s)")
    except Exception as val_e:
        print(f"  ⚠️ Validation check skipped: {val_e}")

    # 2. Collect image assets
    image_patterns = [
        os.path.join(job_dir, "scene_*.jpg"),
        os.path.join(job_dir, "scene_*.png"),
        os.path.join(job_dir, "scene_*.jpeg")
    ]
    raw_images = []
    for pat in image_patterns:
        raw_images.extend(glob.glob(pat))

    # Sort numerically by scene number
    def extract_scene_num(p):
        match = re.search(r'scene_(\d+)', os.path.basename(p))
        return int(match.group(1)) if match else 9999

    sorted_images = sorted(list(set(raw_images)), key=extract_scene_num)

    if len(sorted_images) == 0:
        raise FileNotFoundError(f"No scene images (scene_1.jpg/png...) found in {job_dir}")

    print(f"  Found {len(sorted_images)} scene image assets:")
    for img in sorted_images:
        size_kb = os.path.getsize(img) / 1024.0
        print(f"    - {os.path.basename(img)} ({size_kb:.1f} KB)")

    if len(sorted_images) < len(scenes):
        print(f"  ⚠️ Warning: {len(scenes)} scenes in script, but only {len(sorted_images)} images found. Reusing available images.")

    # 3. Generate TTS Narration Audio
    print("\n[Step 1/3] Generating TTS Narration Audio...")
    from scripts.tts_generator import generate_audio
    audio_path = os.path.join(job_dir, "narration.mp3")
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception:
            pass
    script_json_str = json.dumps(scenes, ensure_ascii=False)
    generate_audio(script_json_str, audio_path, tld=voice)
    print(f"  ✅ Generated narration audio: {audio_path} ({os.path.getsize(audio_path)/1024:.1f} KB)")

    # 4. Generate Captions & Subtitles
    print("\n[Step 2/3] Transcribing & Generating ASS Subtitles via Whisper...")
    from scripts.caption_generator import generate_captions
    from pydub import AudioSegment

    audio_seg = AudioSegment.from_file(audio_path)
    total_dur = len(audio_seg) / 1000.0

    width, height = (2160, 3840) if resolution.lower() == "4k" else (1080, 1920)
    srt_out = os.path.join(job_dir, "captions.srt")
    
    hook_title = ""  # Disabled: Do not add title banner to video


    from scripts.tts_generator import VOICE_LANGUAGE_MAP
    script_lang = VOICE_LANGUAGE_MAP.get(voice, "English")
    ass_path = srt_out.replace(".srt", ".ass")
    for f_stale in (srt_out, ass_path):
        if os.path.exists(f_stale):
            try:
                os.remove(f_stale)
            except Exception:
                pass

    # When voice is Hindi, use direct synchronized ASS synthesis (supports English or Hindi subtitles)
    if "hi" in voice:
        from scripts.caption_generator import generate_bilingual_ass
        print(f"  [Hindi Audio Mode] Audio in Hindi, synthesizing synchronized {caption_lang} subtitles...")
        generate_bilingual_ass(
            scenes=scenes,
            total_duration=total_dur,
            output_ass_path=ass_path,
            style=caption_style,
            width=width,
            height=height,
            cta_text="SUBSCRIBE FOR MORE! 🔔",
            display_lang=caption_lang
        )
    else:
        generate_captions(
            audio_path=audio_path,
            output_srt_path=srt_out,
            style=caption_style,
            hook_title=hook_title,
            total_duration=total_dur,
            cta_text="SUBSCRIBE FOR MORE! 🔔",
            script_language=script_lang,
            width=width,
            height=height
        )
    active_sub_path = ass_path if os.path.exists(ass_path) else srt_out
    print(f"  ✅ Generated Subtitles: {active_sub_path}")

    # 5. Assemble Video with FFmpeg
    print(f"\n[Step 3/3] Rendering Video ({resolution}, transitions={transition_style}, music={music_track})...")
    from scripts.video_generator import generate_video

    final_mp4 = os.path.join(job_dir, "final_video.mp4")
    result = generate_video(
        audio_path=audio_path,
        srt_path=active_sub_path,
        output_path=final_mp4,
        image_paths=sorted_images,
        music_track=music_track,
        caption_style=caption_style,
        script=scenes,
        resolution=resolution,
        transition_style=transition_style
    )

    size_mb = os.path.getsize(final_mp4) / (1024.0 * 1024.0)
    print("\n" + "=" * 65)
    print(f"🎉 FINAL VIDEO READY: {final_mp4}")
    print(f"   Resolution: {width}x{height} | Size: {size_mb:.2f} MB")
    print("=" * 65 + "\n")
    return final_mp4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble YouTube Short from script.json and scene images.")
    parser.add_argument("--job_dir", type=str, required=True, help="Directory containing script.json and scene_*.jpg/png")
    parser.add_argument("--voice", type=str, default="in_female", help="Voice profile key (in_female, in_male, hi_male, etc.)")
    parser.add_argument("--caption_style", type=str, default="tiktok", help="Subtitle style (tiktok, elegant, karaoke, etc.)")
    parser.add_argument("--caption_lang", type=str, default="English", help="Caption display language (English, Hindi, etc.)")
    parser.add_argument("--music", type=str, default="none", help="Background music (none, lofi, upbeat)")
    parser.add_argument("--resolution", type=str, default="1080p", help="Resolution (1080p or 4k)")
    parser.add_argument("--transition", type=str, default="dynamic", help="Scene transitions (dynamic, whip_pan, dissolve, flash, none)")
    args = parser.parse_args()

    assemble_short(
        job_dir=args.job_dir,
        voice=args.voice,
        caption_style=args.caption_style,
        caption_lang=args.caption_lang,
        music_track=args.music,
        resolution=args.resolution,
        transition_style=args.transition
    )
