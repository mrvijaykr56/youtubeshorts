"""
Video-to-Video Multi-Clip Assembly Engine for YTShorts
Assembles multiple generated AI video clips (e.g. from Google Veo, VideoFX, Luma, Kling, RunWay)
into a unified, broadcast-grade Ultra 4K / 8K YouTube Short or Instagram Reel.

Key Capabilities:
1. Smart Scaling & Framing: Converts any aspect ratio/resolution into pristine 9:16 vertical (1080p, 4K, 8K).
2. Intelligent Duration Matching: Automatically trims or speed-ramps clips to match voiceover narration per scene.
3. Hardware-Accelerated Rendering: Uses Intel QSV (h264_qsv) / NVIDIA NVENC (h264_nvenc) with libx264 fallback.
4. Seamless Cinematic Transitions: Applies xfade transitions (dissolve, whip_pan, fadeblack, slide) + whoosh SFX.
5. Audio Sync & Ducking: Synchronizes TTS voiceover narration with dynamic sidechain-compressed BGM.
6. Kinetic ASS Subtitle Burn: Transcribes or synthesizes word-by-word highlighted captions.
"""

import os
import sys
import json
import glob
import re
import subprocess
import argparse
from typing import List, Dict, Optional, Tuple
from pydub import AudioSegment

# Force UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.video_generator import detect_best_gpu_encoder, get_video_encoder_args


def probe_clip(clip_path: str) -> Dict[str, float]:
    """
    Probes video file using ffprobe to obtain exact duration, width, height, and fps.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration:format=duration",
        "-of", "json",
        clip_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        
        # Parse duration
        dur_str = stream.get("duration") or fmt.get("duration") or "0"
        duration = float(dur_str)
        
        # Parse fps
        r_fps = stream.get("r_frame_rate", "30/1")
        if "/" in r_fps:
            num, den = r_fps.split("/")
            fps = float(num) / float(den) if float(den) != 0 else 30.0
        else:
            fps = float(r_fps)
            
        width = int(stream.get("width", 1080))
        height = int(stream.get("height", 1920))
        return {
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height
        }
    except Exception as e:
        print(f"[video_to_video] Warning: ffprobe failed for {clip_path}: {e}")
        return {"duration": 5.0, "fps": 30.0, "width": 1080, "height": 1920}


def standardize_clip(
    input_clip: str,
    output_clip: str,
    target_width: int,
    target_height: int,
    target_duration: float,
    duration_mode: str = "speed_ramp",
    target_fps: int = 30
) -> str:
    """
    Standardizes an input AI video clip:
    - Strips source audio (-an) to prevent mix clashing.
    - Centers and crops into 9:16 aspect ratio without distortion.
    - Adjusts duration using either:
        * 'speed_ramp': smoothly changes speed (setpts) so all motion is preserved.
        * 'trim': trims excess video to exact target duration.
    - Enforces constant target_fps (e.g. 30 fps) and standard pixel format.
    - Applies subtle unsharp mask filter to enhance edge sharpness at 4K/8K.
    """
    meta = probe_clip(input_clip)
    orig_dur = meta["duration"]
    if orig_dur <= 0.1:
        orig_dur = target_duration

    # Build video filter chain
    filters = []

    # 1. Aspect ratio normalization: scale to cover canvas then crop center
    # Also add subtle unsharp enhancement for crisp 4K/8K playback
    scale_crop_filter = (
        f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height},"
        f"setsar=1,fps={target_fps}"
    )
    filters.append(scale_crop_filter)

    # 2. Duration adaptation
    if duration_mode == "speed_ramp" and orig_dur > 0.5:
        # PTS scaling factor: new_pts = (target_duration / orig_dur) * PTS
        pts_factor = target_duration / orig_dur
        filters.append(f"setpts={pts_factor:.6f}*PTS")
    else:  # 'trim' mode or fallback
        if orig_dur < target_duration:
            # If shorter, loop or slow down to fill duration
            pts_factor = target_duration / orig_dur
            filters.append(f"setpts={pts_factor:.6f}*PTS")

    # 3. Subtle edge clarity enhancement (unsharp) for high-res output
    if target_height >= 1920:
        filters.append("unsharp=5:5:0.5:5:5:0.0")

    vf_string = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_clip,
        "-vf", vf_string,
        "-t", f"{target_duration:.3f}",
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        output_clip
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    return output_clip


def create_xfade_video_clips(
    standardized_clips: List[str],
    scene_durations: List[float],
    transition_style: str,
    output_path: str,
    width: int,
    height: int,
    transition_duration: float = 0.5
) -> bool:
    """
    Applies smooth xfade transitions between video clips.
    Supports 'dissolve', 'whip_pan' (slideleft), 'fadeblack', 'circlecrop', etc.
    """
    n = len(standardized_clips)
    if n <= 1:
        return False

    # Map transition names to FFmpeg xfade filters
    xfade_map = {
        "dissolve": "fade",
        "whip_pan": "slideleft",
        "slide": "slideright",
        "flash": "fadeblack",
        "zoom": "circlecrop",
        "dynamic": "fade"
    }

    cmd = ["ffmpeg", "-y"]
    for sc in standardized_clips:
        cmd.extend(["-i", sc])

    filter_complex = ""
    # Calculate offset for each transition
    # Offset of i-th transition is cumulative duration up to clip i minus i * transition_duration
    current_offset = scene_durations[0] - transition_duration
    last_v = "[0:v]"

    for i in range(1, n):
        trans_name = xfade_map.get(transition_style.lower(), "fade")
        if transition_style.lower() == "dynamic":
            dynamic_styles = ["fade", "slideleft", "fadeblack", "slideright", "circlecrop"]
            trans_name = dynamic_styles[(i - 1) % len(dynamic_styles)]

        out_v = f"[v{i}]"
        filter_complex += f"{last_v}[{i}:v]xfade=transition={trans_name}:duration={transition_duration:.2f}:offset={current_offset:.2f}{out_v};"
        last_v = out_v

        if i < n - 1:
            current_offset += scene_durations[i] - transition_duration

    # Strip trailing semicolon
    filter_complex = filter_complex.rstrip(";")

    encoder_args = get_video_encoder_args(crf=16)

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", last_v
    ])
    cmd.extend(encoder_args)
    cmd.append(output_path)

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True
        else:
            print(f"[video_to_video] xfade rendering encountered notice: {res.stderr[:300]}")
            return False
    except Exception as e:
        print(f"[video_to_video] xfade exception: {e}")
        return False


def assemble_video_to_video(
    video_clips: List[str],
    script_or_scenes: List[Dict],
    job_dir: str,
    voice: str = "in_female",
    caption_style: str = "tiktok",
    caption_lang: str = "English",
    music_track: str = "none",
    resolution: str = "4k",
    transition_style: str = "dynamic",
    duration_mode: str = "speed_ramp"
) -> str:
    """
    Main orchestrator for Video-to-Video Multi-Clip Short Assembly.
    Returns the path to the finalized, broadcast-ready 9:16 MP4 short.
    """
    job_dir = os.path.abspath(job_dir)
    os.makedirs(job_dir, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"🚀 VIDEO-TO-VIDEO MULTI-CLIP ASSEMBLY ENGINE")
    print(f"   Target Resolution: {resolution.upper()} | Voice: {voice} | Transitions: {transition_style}")
    print(f"   Input Video Clips: {len(video_clips)} clips | Mode: {duration_mode}")
    print(f"{'='*70}")

    if not video_clips:
        raise ValueError("No video clips provided to assemble_video_to_video.")

    # 1. Determine target canvas dimensions
    res_clean = resolution.lower().strip()
    if "8k" in res_clean:
        width, height = 4320, 7680
        print("  [Resolution] ULTRA 8K Vertical (4320x7680)")
    elif "4k" in res_clean:
        width, height = 2160, 3840
        print("  [Resolution] 4K Ultra HD Vertical (2160x3840)")
    else:
        width, height = 1080, 1920
        print("  [Resolution] 1080p Full HD Vertical (1080x1920)")

    # 2. Generate or Load TTS Narration Audio
    print("\n[Step 1/4] Generating Synchronized TTS Narration Audio...")
    from scripts.tts_generator import generate_audio
    audio_path = os.path.join(job_dir, "narration.mp3")
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception:
            pass

    script_json_str = json.dumps(script_or_scenes, ensure_ascii=False)
    generate_audio(script_json_str, audio_path, tld=voice)
    audio_seg = AudioSegment.from_file(audio_path)
    total_audio_duration = len(audio_seg) / 1000.0
    print(f"  ✅ Narration audio ready ({total_audio_duration:.2f}s): {audio_path}")

    # 3. Calculate Scene Timing
    # Calculate proportional duration per scene based on word counts
    scene_word_counts = [max(1, len(s.get("narration", "").split())) for s in script_or_scenes]
    total_words = sum(scene_word_counts)
    num_clips = len(video_clips)

    if total_words > 0 and len(scene_word_counts) == num_clips:
        raw_durs = [(wc / total_words) * total_audio_duration for wc in scene_word_counts]
        clamped_durs = [max(1.5, d) for d in raw_durs]
        scale = total_audio_duration / sum(clamped_durs)
        scene_durations = [d * scale for d in clamped_durs]
    else:
        equal_dur = total_audio_duration / num_clips
        scene_durations = [equal_dur] * num_clips

    # Extend final scene by 1.8 seconds for Outro CTA padding
    scene_durations[-1] += 1.8
    total_video_duration = sum(scene_durations)

    print(f"  Scene durations calculated ({num_clips} scenes, total {total_video_duration:.2f}s):")
    for idx, d in enumerate(scene_durations):
        print(f"    - Scene {idx+1}: {d:.2f}s")

    # 4. Standardize each input video clip
    print("\n[Step 2/4] Standardizing & Formatting Video Clips...")
    trans_dur = 0.50 if transition_style != "none" else 0.0
    standardized_clips = []

    for i, clip_in in enumerate(video_clips):
        clip_target_dur = scene_durations[i]
        # When using xfade, add transition overlap to all clips except the last
        if transition_style != "none" and i < num_clips - 1:
            clip_target_dur += trans_dur

        clip_out = os.path.join(job_dir, f"std_clip_{i:02d}.mp4")
        if os.path.exists(clip_out):
            try:
                os.remove(clip_out)
            except Exception:
                pass

        print(f"  Processing Clip {i+1}/{num_clips}: {os.path.basename(clip_in)} -> {clip_target_dur:.2f}s ({duration_mode})...")
        standardize_clip(
            input_clip=clip_in,
            output_clip=clip_out,
            target_width=width,
            target_height=height,
            target_duration=clip_target_dur,
            duration_mode=duration_mode,
            target_fps=30
        )
        standardized_clips.append(clip_out)

    # 5. Apply transitions or concat
    print("\n[Step 3/4] Blending Clips with Cinematic Transitions...")
    xfade_mp4 = os.path.join(job_dir, "video_track_xfade.mp4")
    used_xfade = False

    if transition_style != "none" and len(standardized_clips) > 1:
        used_xfade = create_xfade_video_clips(
            standardized_clips=standardized_clips,
            scene_durations=scene_durations,
            transition_style=transition_style,
            output_path=xfade_mp4,
            width=width,
            height=height,
            transition_duration=trans_dur
        )

    concat_txt = os.path.join(job_dir, "video_track_concat.txt")
    if not used_xfade:
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sc in standardized_clips:
                safe_sc = sc.replace("\\", "/")
                f.write(f"file '{safe_sc}'\n")

    # 6. Generate Subtitles
    print("\n[Step 4/4] Transcribing & Burning ASS Subtitles...")
    from scripts.caption_generator import generate_captions, generate_bilingual_ass
    srt_out = os.path.join(job_dir, "captions.srt")
    ass_path = srt_out.replace(".srt", ".ass")

    for f_stale in (srt_out, ass_path):
        if os.path.exists(f_stale):
            try:
                os.remove(f_stale)
            except Exception:
                pass

    if "hi" in voice.lower():
        print(f"  Synthesizing Hindi/Bilingual synchronized {caption_lang} subtitles...")
        generate_bilingual_ass(
            scenes=script_or_scenes,
            total_duration=total_audio_duration,
            output_ass_path=ass_path,
            style=caption_style,
            width=width,
            height=height,
            cta_text="SUBSCRIBE FOR MORE! 🔔",
            display_lang=caption_lang
        )
    else:
        from scripts.tts_generator import VOICE_LANGUAGE_MAP
        script_lang = VOICE_LANGUAGE_MAP.get(voice, "English")
        generate_captions(
            audio_path=audio_path,
            output_srt_path=srt_out,
            style=caption_style,
            hook_title="",
            total_duration=total_audio_duration,
            cta_text="SUBSCRIBE FOR MORE! 🔔",
            script_language=script_lang,
            width=width,
            height=height
        )

    active_sub = ass_path if os.path.exists(ass_path) else srt_out

    # 7. Final Master Render (Video + Narration + Ducked BGM + SFX + Subtitles)
    final_output = os.path.join(job_dir, "final_master_video.mp4")
    if os.path.exists(final_output):
        try:
            os.remove(final_output)
        except Exception:
            pass

    # Music & SFX
    music_path = ""
    if music_track in ["lofi", "upbeat"]:
        candidate_bgm = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", f"{music_track}.mp3")
        if os.path.exists(candidate_bgm):
            music_path = candidate_bgm

    whoosh_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", "whoosh.mp3")
    has_whoosh = os.path.exists(whoosh_path) and len(video_clips) > 1

    ffmpeg_cmd = ["ffmpeg", "-y"]

    # Input 0: Visual track
    if used_xfade:
        ffmpeg_cmd.extend(["-i", xfade_mp4])
    else:
        ffmpeg_cmd.extend(["-f", "concat", "-safe", "0", "-i", concat_txt])

    # Input 1: Narration audio
    ffmpeg_cmd.extend(["-i", audio_path])

    input_idx = 2
    music_idx = -1
    whoosh_indices = []

    if music_path:
        ffmpeg_cmd.extend(["-stream_loop", "-1", "-i", music_path])
        music_idx = input_idx
        input_idx += 1

    if has_whoosh:
        num_transitions = len(video_clips) - 1
        for _ in range(num_transitions):
            ffmpeg_cmd.extend(["-i", whoosh_path])
            whoosh_indices.append(input_idx)
            input_idx += 1

    # Complex Filter Setup
    # 1. Subtitle filter
    safe_sub_path = active_sub.replace("\\", "/").replace(":", "\\:")
    vf_sub = f"ass='{safe_sub_path}'"

    # 2. Audio mixing with sidechain ducking & whoosh cues
    audio_filters = []
    if music_idx != -1:
        audio_filters.append("[1:a]apad=pad_dur=1.8,loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voice_compress][voice_mix]")
        mix_inputs = ["[voice_mix]"]
    else:
        audio_filters.append("[1:a]apad=pad_dur=1.8,loudnorm=I=-16:TP=-1.5:LRA=11[voice]")
        mix_inputs = ["[voice]"]

    if music_idx != -1:
        audio_filters.append(f"[{music_idx}:a]volume=0.10[bg_raw]")
        audio_filters.append("[bg_raw][voice_compress]sidechaincompress=threshold=0.10:ratio=6:attack=40:release=200[bg]")
        mix_inputs.append("[bg]")

    if whoosh_indices:
        cumulative_time = 0.0
        for w_pos, w_idx in enumerate(whoosh_indices):
            cumulative_time += scene_durations[w_pos]
            delay_ms = int(cumulative_time * 1000)
            audio_filters.append(f"[{w_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.35[whoosh_{w_pos}]")
            mix_inputs.append(f"[whoosh_{w_pos}]")

    num_mix = len(mix_inputs)
    mix_str = "".join(mix_inputs)
    if num_mix > 1:
        audio_filters.append(f"{mix_str}amix=inputs={num_mix}:duration=longest,atrim=0:{total_video_duration:.3f},afade=t=out:st={total_video_duration-1.0:.3f}:d=1.0[final_a]")
    else:
        audio_filters.append(f"[voice]atrim=0:{total_video_duration:.3f}[final_a]")

    final_a_map = "[final_a]"
    filter_complex = f"[0:v]{vf_sub}[v_out];" + ";".join(audio_filters)

    encoder_args = get_video_encoder_args(crf=16)

    ffmpeg_cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", final_a_map,
        "-t", f"{total_video_duration:.3f}"
    ])
    ffmpeg_cmd.extend(encoder_args)
    ffmpeg_cmd.extend([
        "-c:a", "aac",
        "-b:a", "192k",
        final_output
    ])

    print("  Encoding master video with hardware acceleration...")
    subprocess.run(ffmpeg_cmd, check=True)

    # 8. Generate High-Res Poster Thumbnail from Hook Scene
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    try:
        thumb_cmd = [
            "ffmpeg", "-y",
            "-ss", "1.0",
            "-i", final_output,
            "-vframes", "1",
            "-q:v", "2",
            thumb_path
        ]
        subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if os.path.exists(thumb_path):
            print(f"   🖼️  Poster Thumbnail Ready: {thumb_path}")
    except Exception:
        pass

    size_mb = os.path.getsize(final_output) / (1024.0 * 1024.0)
    print(f"\n{'='*70}")
    print(f"🎉 MASTER VIDEO-TO-VIDEO SHORT READY: {final_output}")
    print(f"   Resolution: {width}x{height} | Size: {size_mb:.2f} MB | Duration: {total_video_duration:.2f}s")
    print(f"{'='*70}\n")
    return final_output


def generate_sample_test_clips(output_dir: str, num_clips: int = 5, duration_per_clip: float = 8.0) -> List[str]:
    """
    Synthesizes animated 9:16 sample video clips using FFmpeg test patterns.
    Used for instant automated pipeline verification without needing external downloads.
    """
    os.makedirs(output_dir, exist_ok=True)
    patterns = [
        ("testsrc2", "rate=30"),
        ("smptehdbars", "rate=30"),
        ("gradients", "s=1080x1920:r=30:c0=0x1E3A8A:c1=0x9333EA:speed=0.01"),
        ("mandelbrot", "s=1080x1920:rate=30:maxiter=100"),
        ("cellauto", "s=1080x1920:rate=30:rule=30")
    ]

    clip_paths = []
    print(f"[sample_generator] Synthesizing {num_clips} sample 9:16 video clips...")

    for i in range(num_clips):
        clip_path = os.path.join(output_dir, f"sample_clip_{i+1:02d}.mp4")
        if os.path.exists(clip_path) and os.path.getsize(clip_path) > 10000:
            clip_paths.append(clip_path)
            continue

        src_name, src_args = patterns[i % len(patterns)]
        # Use lavfi to synthesize an animated pattern directly
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"{src_name}={src_args}",
            "-t", f"{duration_per_clip:.1f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            clip_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        clip_paths.append(clip_path)
        print(f"  - Generated sample clip {i+1}: {os.path.basename(clip_path)}")

    return clip_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble Multi-Clip Video into YouTube Short")
    parser.add_argument("--job_dir", type=str, required=True, help="Job working directory")
    parser.add_argument("--clips", type=str, nargs="*", default=None, help="Paths to video clips")
    parser.add_argument("--script", type=str, default="", help="Path to script.json")
    parser.add_argument("--voice", type=str, default="in_female", help="Voice profile key")
    parser.add_argument("--caption_style", type=str, default="tiktok", help="Subtitle style")
    parser.add_argument("--caption_lang", type=str, default="English", help="Subtitle language")
    parser.add_argument("--music", type=str, default="none", help="Background music (none, lofi, upbeat)")
    parser.add_argument("--resolution", type=str, default="4k", help="Resolution: 1080p, 4k, 8k")
    parser.add_argument("--transition", type=str, default="dynamic", help="Transition style: dynamic, dissolve, whip_pan, flash")
    parser.add_argument("--mode", type=str, default="speed_ramp", help="Duration adaptation mode: speed_ramp, trim")
    parser.add_argument("--generate_samples", action="store_true", help="Generate synthetic test clips if none exist")
    args = parser.parse_args()

    # Load script.json
    script_file = args.script if args.script else os.path.join(args.job_dir, "script.json")
    if not os.path.exists(script_file):
        # Default test script
        scenes = [
            {"scene": 1, "narration": "Deep beneath the ocean surface lies a hidden realm that science cannot explain."},
            {"scene": 2, "narration": "In twenty twenty-six, robotic probes detected rhythmic light pulses miles underwater."},
            {"scene": 3, "narration": "Bioluminescent organisms moved in perfect, intelligent geometric formations."},
            {"scene": 4, "narration": "Every pulse transmitted synchronized energy across the entire ocean floor."},
            {"scene": 5, "narration": "Are these ancient earthly creatures, or something from beyond our world? Subscribe for more!"}
        ]
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(scenes, f, indent=2)
    else:
        with open(script_file, "r", encoding="utf-8") as f:
            s_data = json.load(f)
            scenes = s_data.get("scenes", s_data) if isinstance(s_data, dict) else s_data

    # Find or generate clips
    clips = args.clips
    if not clips:
        clip_patterns = [
            os.path.join(args.job_dir, "clip_*.mp4"),
            os.path.join(args.job_dir, "scene_*.mp4"),
            os.path.join(args.job_dir, "sample_clip_*.mp4")
        ]
        found = []
        for p in clip_patterns:
            found.extend(glob.glob(p))
        clips = sorted(list(set(found)))

    if not clips and args.generate_samples:
        clips = generate_sample_test_clips(args.job_dir, num_clips=len(scenes))

    if not clips:
        print("No clips found. Use --generate_samples to generate test clips.")
        sys.exit(1)

    assemble_video_to_video(
        video_clips=clips,
        script_or_scenes=scenes,
        job_dir=args.job_dir,
        voice=args.voice,
        caption_style=args.caption_style,
        caption_lang=args.caption_lang,
        music_track=args.music,
        resolution=args.resolution,
        transition_style=args.transition,
        duration_mode=args.mode
    )
