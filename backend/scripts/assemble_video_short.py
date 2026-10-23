"""
YTShorts Video-to-Video Assembly Runner
CLI & programmatic entry point to assemble YouTube Shorts directly from 5 generated AI video clips
(e.g., Google Veo / VideoFX / Luma / Kling).

Usage:
  python assemble_video_short.py --job_dir ../output/test_video_short --resolution 4k --voice in_female
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.video_to_video_assembler import assemble_video_to_video, generate_sample_test_clips
import json
import glob

def main():
    parser = argparse.ArgumentParser(description="Assemble YouTube Short from AI Video Clips")
    parser.add_argument("--job_dir", type=str, required=True, help="Directory containing video clips and optional script.json")
    parser.add_argument("--voice", type=str, default="in_female", help="Voice profile key (in_female, in_male, hi_male, etc.)")
    parser.add_argument("--caption_style", type=str, default="tiktok", help="Subtitle style (tiktok, elegant, karaoke)")
    parser.add_argument("--caption_lang", type=str, default="English", help="Caption language (English, Hindi)")
    parser.add_argument("--music", type=str, default="none", help="Background music (none, lofi, upbeat)")
    parser.add_argument("--resolution", type=str, default="4k", help="Target resolution (1080p, 4k, 8k)")
    parser.add_argument("--transition", type=str, default="dynamic", help="Transitions (dynamic, dissolve, whip_pan, flash, none)")
    parser.add_argument("--mode", type=str, default="speed_ramp", help="Duration adaptation mode (speed_ramp, trim)")
    parser.add_argument("--generate_samples", action="store_true", help="Synthesize test clips if directory lacks clips")
    args = parser.parse_args()

    job_dir = os.path.abspath(args.job_dir)
    os.makedirs(job_dir, exist_ok=True)

    # 1. Discover or create script
    script_file = os.path.join(job_dir, "script.json")
    if not os.path.exists(script_file):
        default_scenes = [
            {"scene": 1, "narration": "Deep beneath the ocean surface lies a hidden realm that modern science cannot explain."},
            {"scene": 2, "narration": "In twenty twenty-six, autonomous deep-sea probes detected rhythmic light pulses miles underwater."},
            {"scene": 3, "narration": "Bioluminescent structures pulsed in perfect, intelligent geometric formations."},
            {"scene": 4, "narration": "Every shockwave transmitted synchronized resonance across the entire ocean floor."},
            {"scene": 5, "narration": "Are these ancient earthly guardians, or visitors from beyond our stars? Subscribe for more!"}
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

    print(f"Found {len(clips)} video clips for assembly.")
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
        duration_mode=args.mode
    )

if __name__ == "__main__":
    main()
