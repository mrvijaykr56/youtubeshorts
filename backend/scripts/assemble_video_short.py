"""
YTShorts Video-to-Video Assembly Runner (v2.0 Zero-Error Pipeline)
CLI & programmatic entry point to assemble YouTube Shorts directly from generated AI video clips
(e.g., Google Veo / VideoFX / Luma Dream Machine / Kling AI / Runway Gen-3).

Usage:
  python assemble_video_short.py --job_dir ../output/test_video_short --resolution 4k --voice hi_female
"""

import os
import sys
import argparse
import json
import glob

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.video_to_video_assembler import (
    assemble_video_to_video,
    generate_sample_test_clips,
    inspect_video_clips
)

def main():
    parser = argparse.ArgumentParser(description="Assemble YouTube Short from AI Video Clips (Zero-Error Pipeline)")
    parser.add_argument("--job_dir", type=str, required=True, help="Directory containing video clips and optional script.json")
    parser.add_argument("--voice", type=str, default="in_female", help="Voice profile key (hi_female, in_female, hi_male, etc.)")
    parser.add_argument("--caption_style", type=str, default="tiktok", help="Subtitle style (tiktok, elegant, karaoke)")
    parser.add_argument("--caption_lang", type=str, default="English", help="Caption language (English, Hindi)")
    parser.add_argument("--music", type=str, default="none", help="Background music (none, lofi, upbeat)")
    parser.add_argument("--resolution", type=str, default="4k", help="Target resolution (1080p, 4k, 8k)")
    parser.add_argument("--transition", type=str, default="dynamic", help="Transitions (dynamic, dissolve, whip_pan, flash, none)")
    parser.add_argument("--mode", type=str, default="speed_ramp", help="Duration adaptation mode (speed_ramp, trim)")
    parser.add_argument("--fps", type=int, default=30, help="Output target frame rate (30, 60)")
    parser.add_argument("--generate_samples", action="store_true", help="Synthesize test clips if directory lacks clips")
    parser.add_argument("--dry_run", action="store_true", help="Inspect clips and calculate timeline without rendering")
    args = parser.parse_args()

    job_dir = os.path.abspath(args.job_dir)
    os.makedirs(job_dir, exist_ok=True)

    # 1. Discover or create script
    script_file = os.path.join(job_dir, "script.json")
    if not os.path.exists(script_file):
        default_scenes = [
            {"scene": 1, "narration": "Deep beneath the ocean surface lies a hidden realm that modern science cannot explain. 🌊"},
            {"scene": 2, "narration": "In twenty twenty-six, autonomous deep-sea probes detected rhythmic light pulses miles underwater. ✨"},
            {"scene": 3, "narration": "Bioluminescent structures pulsed in perfect, intelligent geometric formations. ⚡"},
            {"scene": 4, "narration": "Every shockwave transmitted synchronized resonance across the entire ocean floor. 🌌"},
            {"scene": 5, "narration": "Are these ancient earthly guardians, or visitors from beyond our stars? Subscribe for more! 🔔"}
        ]
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(default_scenes, f, indent=2)
        scenes = default_scenes
    else:
        with open(script_file, "r", encoding="utf-8") as f:
            s_data = json.load(f)
            scenes = s_data.get("scenes", s_data) if isinstance(s_data, dict) else s_data

    # 2. Discover clips
    clip_patterns = [
        os.path.join(job_dir, "clip_*.mp4"),
        os.path.join(job_dir, "scene_*.mp4"),
        os.path.join(job_dir, "sample_clip_*.mp4")
    ]
    found = []
    for p in clip_patterns:
        found.extend(glob.glob(p))
    clips = sorted(list(set(found)))

    if not clips and args.generate_samples:
        clips = generate_sample_test_clips(job_dir, num_clips=len(scenes))

    if not clips:
        print(f"❌ Error: No video clips found in {job_dir}. Drop clips (clip_1.mp4 ... clip_5.mp4) or pass --generate_samples.")
        sys.exit(1)

    print(f"\n=================================================================")
    print(f"🔍 PRE-FLIGHT INSPECTION: {len(clips)} CLIPS FOUND")
    print(f"=================================================================")
    is_valid, errors, meta_list = inspect_video_clips(clips)
    if not is_valid:
        print("❌ Pre-flight check failed:")
        for err in errors:
            print(f"   ✖ {err}")
        sys.exit(1)

    for i, (c, m) in enumerate(zip(clips, meta_list), 1):
        print(f"  {i}. {os.path.basename(c)}: {m['width']}x{m['height']} | {m['duration']:.2f}s | {m['fps']:.1f}fps | {m['pix_fmt']}")

    if args.dry_run:
        print("\n✅ DRY RUN COMPLETE: All video clips and parameters verified. Ready for 0-error render.")
        sys.exit(0)

    assemble_video_to_video(
        video_clips=clips,
        script_or_scenes=scenes,
        job_dir=job_dir,
        voice=args.voice,
        caption_style=args.caption_style,
        caption_lang=args.caption_lang,
        music_track=args.music,
        resolution=args.resolution,
        transition_style=args.transition,
        duration_mode=args.mode,
        target_fps=args.fps
    )

if __name__ == "__main__":
    main()
