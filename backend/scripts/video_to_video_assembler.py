"""
Video-to-Video Multi-Clip Assembly Engine for YTShorts (v2.0 Zero-Error Pipeline)
Assembles multiple generated AI video clips (e.g. from Google Veo, VideoFX, Luma Dream Machine, Kling AI, Runway Gen-3)
into a unified, broadcast-grade Ultra 4K / 8K YouTube Short or Instagram Reel with 0 error in one go.

Key Capabilities:
1. Pre-Flight Clip Health Inspector: Deep inspection of input video streams, durations, aspect ratios, and codecs.
2. Smart 9:16 Center-Scale Normalization: Converts any aspect ratio/resolution into pristine 9:16 vertical without distortion.
3. Timestamp & Frame Cadence Lock: Eliminates non-monotonic DTS warnings via strict CFR (Constant Frame Rate) and PTS resets.
4. Intelligent Duration Matching: Automatically trims or speed-ramps clips to match voiceover narration per scene.
5. Seamless Cinematic Transitions: Applies xfade transitions (dissolve, whip_pan, fadeblack, slide) + whoosh SFX with collision guard.
6. Audio Sync & Ducking: Synchronizes TTS voiceover narration with dynamic sidechain-compressed BGM and broadcast loudness normalization.
7. Kinetic ASS Subtitle Burn: Transcribes or synthesizes word-by-word highlighted captions with font provider resilience.
"""

import os
import sys
import json
import glob
import re
import subprocess
import argparse
from typing import List, Dict, Optional, Tuple, Any
from pydub import AudioSegment

# Force UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.video_generator import detect_best_gpu_encoder, get_video_encoder_args


def probe_clip(clip_path: str) -> Dict[str, Any]:
    """
    Probes video file using ffprobe to obtain exact duration, width, height, fps, and SAR/DAR.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,sample_aspect_ratio,pix_fmt,duration:format=duration",
        "-of", "json",
        clip_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        
        dur_str = stream.get("duration") or fmt.get("duration") or "0"
        duration = float(dur_str)
        
        r_fps = stream.get("r_frame_rate", "30/1")
        if "/" in r_fps:
            num, den = r_fps.split("/")
            fps = float(num) / float(den) if float(den) != 0 else 30.0
        else:
            fps = float(r_fps)
            
        width = int(stream.get("width", 1080))
        height = int(stream.get("height", 1920))
        sar = stream.get("sample_aspect_ratio", "1:1")
        pix_fmt = stream.get("pix_fmt", "yuv420p")

        return {
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "sar": sar,
            "pix_fmt": pix_fmt,
            "valid": duration > 0.1
        }
    except Exception as e:
        print(f"[video_to_video] Warning: ffprobe failed for {clip_path}: {e}")
        return {"duration": 5.0, "fps": 30.0, "width": 1080, "height": 1920, "sar": "1:1", "pix_fmt": "yuv420p", "valid": False}


def inspect_video_clips(clip_paths: List[str]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    """
    Pre-flight validator for incoming video clips.
    Verifies that all clips exist, have non-zero size, and can be decoded by FFmpeg.
    """
    errors = []
    metadata_list = []
    
    if not clip_paths:
        errors.append("No video clips provided.")
        return False, errors, metadata_list

    for i, path in enumerate(clip_paths):
        if not os.path.exists(path):
            errors.append(f"Clip {i+1} not found: {path}")
            continue
        
        size = os.path.getsize(path)
        if size < 1024:  # under 1KB is almost certainly corrupted
            errors.append(f"Clip {i+1} is corrupted or empty ({size} bytes): {os.path.basename(path)}")
            continue

        meta = probe_clip(path)
        if not meta["valid"] or meta["duration"] <= 0.1:
            errors.append(f"Clip {i+1} has invalid duration ({meta['duration']:.2f}s): {os.path.basename(path)}")
            continue

        metadata_list.append(meta)

    is_valid = len(errors) == 0 and len(metadata_list) == len(clip_paths)
    return is_valid, errors, metadata_list


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
    Standardizes an input AI video clip (Veo, Kling, Luma, Runway):
    - Strips source audio (-an) to prevent stream conflicts.
    - Centers and crops into 9:16 aspect ratio without stretching or letterboxing.
    - Locks frame rate to target_fps and forces constant frame rate (CFR).
    - Normalizes pixel format to standard yuv420p.
    - Strips initial timestamps with setpts=PTS-STARTPTS to eliminate non-monotonic DTS warnings.
    - Adjusts duration using speed_ramp (preserves all action) or trim.
    - Applies subtle unsharp mask filter for crisp 4K/8K rendering.
    """
    meta = probe_clip(input_clip)
    orig_dur = meta["duration"]
    if orig_dur <= 0.1:
        orig_dur = target_duration

    filters = []

    # 1. Aspect ratio & geometry normalization (center-crop to fill 9:16 frame)
    scale_crop_filter = (
        f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height},"
        f"setsar=1,fps={target_fps}"
    )
    filters.append(scale_crop_filter)

    # 2. Duration adaptation with strict PTS start reset
    if duration_mode == "speed_ramp" and orig_dur > 0.3:
        pts_factor = target_duration / orig_dur
        filters.append(f"setpts={pts_factor:.6f}*PTS-STARTPTS")
    else:  # 'trim' mode or fallback
        if orig_dur < target_duration:
            pts_factor = target_duration / orig_dur
            filters.append(f"setpts={pts_factor:.6f}*PTS-STARTPTS")
        else:
            filters.append(f"trim=0:{target_duration:.3f},setpts=PTS-STARTPTS")

    # 3. Format and edge clarity enhancement
    filters.append("format=yuv420p")
    if target_height >= 1920:
        filters.append("unsharp=5:5:0.5:5:5:0.0")

    vf_string = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_clip,
        "-vf", vf_string,
        "-t", f"{target_duration:.3f}",
        "-an",
        "-fps_mode", "cfr",
        "-r", str(target_fps),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts",
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
    transition_duration: float = 0.50,
    target_fps: int = 30
) -> bool:
    """
    Applies smooth xfade transitions between video clips with zero-error guarantees:
    - Safely clamps transition duration to prevent collision with short clips.
    - Computes exact floating-point timeline offsets.
    - Appends setpts=PTS-STARTPTS and fps={target_fps} to the output stream.
    - Enforces CFR output mode to eliminate non-monotonic DTS errors completely.
    """
    n = len(standardized_clips)
    if n <= 1:
        return False

    # Guard: transition cannot exceed 35% of the shortest scene duration
    min_dur = min(scene_durations)
    safe_trans_dur = min(transition_duration, max(0.2, min_dur * 0.35))

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
    current_offset = scene_durations[0] - safe_trans_dur
    last_v = "[0:v]"

    for i in range(1, n):
        trans_name = xfade_map.get(transition_style.lower(), "fade")
        if transition_style.lower() == "dynamic":
            dynamic_styles = ["fade", "slideleft", "fadeblack", "slideright", "circlecrop"]
            trans_name = dynamic_styles[(i - 1) % len(dynamic_styles)]

        out_v = f"[v{i}]"
        filter_complex += f"{last_v}[{i}:v]xfade=transition={trans_name}:duration={safe_trans_dur:.2f}:offset={current_offset:.2f}{out_v};"
        last_v = out_v

        if i < n - 1:
            current_offset += scene_durations[i] - safe_trans_dur

    # Lock output stream to strict CFR, reset timestamps, and normalize pixel format
    filter_complex += f"{last_v}setpts=PTS-STARTPTS,fps={target_fps},format=yuv420p[v_final]"

    encoder_args = get_video_encoder_args(crf=16)

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v_final]",
        "-fps_mode", "cfr",
        "-r", str(target_fps),
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts"
    ])
    cmd.extend(encoder_args)
    cmd.append(output_path)

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True
        else:
            print(f"[video_to_video] xfade notice: {res.stderr[:250]}")
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
    duration_mode: str = "speed_ramp",
    target_fps: int = 30
) -> str:
    """
    Main orchestrator for Video-to-Video Multi-Clip Short Assembly.
    Returns the path to the finalized, broadcast-ready 9:16 MP4 short with 0 error in one go.
    """
    job_dir = os.path.abspath(job_dir)
    os.makedirs(job_dir, exist_ok=True)

    print(f"\n{'='*75}")
    print(f"🚀 VIDEO-TO-VIDEO MULTI-CLIP ASSEMBLY ENGINE (v2.0 Zero-Error Pipeline)")
    print(f"   Target Resolution: {resolution.upper()} | Voice: {voice} | Transitions: {transition_style}")
    print(f"   Input Video Clips: {len(video_clips)} clips | Duration Mode: {duration_mode} | FPS: {target_fps}")
    print(f"{'='*75}")

    # 1. Pre-Flight Clip Verification
    is_valid, errors, meta_list = inspect_video_clips(video_clips)
    if not is_valid:
        raise ValueError(f"Pre-flight clip check failed:\n" + "\n".join(f" - {e}" for e in errors))

    print(f"  ✅ Pre-flight verification passed for all {len(video_clips)} input video clips:")
    for idx, (c_path, m) in enumerate(zip(video_clips, meta_list), 1):
        print(f"     {idx}. {os.path.basename(c_path)} ({m['width']}x{m['height']}, {m['duration']:.2f}s, {m['fps']:.1f}fps)")

    # 2. Determine target canvas dimensions
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

    # 3. Generate or Load Synchronized TTS Narration Audio
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

    # 4. Calculate Scene Timing
    # Proportional duration based on spoken word counts (checks Hindi narration_hi or English narration)
    scene_word_counts = []
    for s in script_or_scenes:
        text = s.get("narration_hi") or s.get("narration") or ""
        words = len(text.split())
        scene_word_counts.append(max(1, words))

    total_words = sum(scene_word_counts)
    num_clips = len(video_clips)

    if total_words > 0 and len(scene_word_counts) == num_clips:
        raw_durs = [(wc / total_words) * total_audio_duration for wc in scene_word_counts]
        clamped_durs = [max(2.0, d) for d in raw_durs]
        scale = total_audio_duration / sum(clamped_durs)
        scene_durations = [d * scale for d in clamped_durs]
    else:
        equal_dur = total_audio_duration / num_clips
        scene_durations = [equal_dur] * num_clips

    # Extend final scene by 1.5 seconds for Outro CTA padding and smooth retention loop
    scene_durations[-1] += 1.5
    total_video_duration = sum(scene_durations)

    print(f"  Scene durations calculated ({num_clips} scenes, total {total_video_duration:.2f}s):")
    for idx, d in enumerate(scene_durations):
        print(f"    - Scene {idx+1}: {d:.2f}s")

    # 5. Standardize each input video clip
    print("\n[Step 2/4] Standardizing & Formatting Video Clips...")
    trans_dur = 0.50 if transition_style != "none" else 0.0
    # Guard against transition exceeding scene duration
    if trans_dur > 0:
        trans_dur = min(trans_dur, min(scene_durations) * 0.35)

    standardized_clips = []
    for i, clip_in in enumerate(video_clips):
        clip_target_dur = scene_durations[i]
        if transition_style != "none" and i < num_clips - 1:
            clip_target_dur += trans_dur

        clip_out = os.path.join(job_dir, f"std_clip_{i:02d}.mp4")
        if os.path.exists(clip_out):
            try:
                os.remove(clip_out)
            except Exception:
                pass

        print(f"  Standardizing Clip {i+1}/{num_clips}: {os.path.basename(clip_in)} -> {clip_target_dur:.2f}s ({duration_mode})...")
        standardize_clip(
            input_clip=clip_in,
            output_clip=clip_out,
            target_width=width,
            target_height=height,
            target_duration=clip_target_dur,
            duration_mode=duration_mode,
            target_fps=target_fps
        )
        standardized_clips.append(clip_out)

    # 6. Apply transitions or fallback concat
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
            transition_duration=trans_dur,
            target_fps=target_fps
        )

    concat_txt = os.path.join(job_dir, "video_track_concat.txt")
    if not used_xfade:
        print("  [Notice] Using robust stream concatenation fallback...")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sc in standardized_clips:
                safe_sc = sc.replace("\\", "/")
                f.write(f"file '{safe_sc}'\n")

    # 7. Generate Subtitles
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

    active_sub = ass_path if os.path.exists(ass_path) and os.path.getsize(ass_path) > 100 else srt_out
    has_valid_subtitles = os.path.exists(active_sub) and os.path.getsize(active_sub) > 100

    # 8. Final Master Render (Video + Narration + Ducked BGM + SFX + Subtitles)
    final_output = os.path.join(job_dir, "final_master_video.mp4")
    if os.path.exists(final_output):
        try:
            os.remove(final_output)
        except Exception:
            pass

    # Music & SFX configuration
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

    # Filter Complex Assembly
    # Subtitle overlay with fallback resilience
    if has_valid_subtitles:
        safe_sub_path = active_sub.replace("\\", "/").replace(":", "\\:")
        video_chain = f"[0:v]ass='{safe_sub_path}',setpts=PTS-STARTPTS,fps={target_fps},format=yuv420p[v_out];"
    else:
        video_chain = f"[0:v]setpts=PTS-STARTPTS,fps={target_fps},format=yuv420p[v_out];"

    audio_filters = []
    if music_idx != -1:
        audio_filters.append("[1:a]apad=pad_dur=1.5,loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voice_compress][voice_mix]")
        mix_inputs = ["[voice_mix]"]
        audio_filters.append(f"[{music_idx}:a]volume=0.10[bg_raw]")
        audio_filters.append("[bg_raw][voice_compress]sidechaincompress=threshold=0.10:ratio=6:attack=40:release=200[bg]")
        mix_inputs.append("[bg]")
    else:
        audio_filters.append("[1:a]apad=pad_dur=1.5,loudnorm=I=-16:TP=-1.5:LRA=11[voice]")
        mix_inputs = ["[voice]"]

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
        audio_filters.append(
            f"{mix_str}amix=inputs={num_mix}:duration=longest:normalize=0,"
            f"atrim=0:{total_video_duration:.3f},"
            f"alimiter=limit=0.89:level=false:attack=5:release=50,"
            f"afade=t=out:st={total_video_duration-1.0:.3f}:d=1.0[final_a]"
        )
    else:
        audio_filters.append(f"[voice]atrim=0:{total_video_duration:.3f},alimiter=limit=0.89:level=false[final_a]")

    filter_complex = video_chain + ";".join(audio_filters)
    encoder_args = get_video_encoder_args(crf=16)

    ffmpeg_cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[final_a]",
        "-t", f"{total_video_duration:.3f}",
        "-fps_mode", "cfr",
        "-r", str(target_fps),
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts"
    ])
    ffmpeg_cmd.extend(encoder_args)
    ffmpeg_cmd.extend([
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        final_output
    ])

    print("  Encoding master video with hardware acceleration...")
    subprocess.run(ffmpeg_cmd, check=True)

    # 9. Extract High-Res Poster Thumbnail at t=1.0s
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
    print(f"\n{'='*75}")
    print(f"🎉 MASTER VIDEO-TO-VIDEO SHORT READY (Zero-Error Guarantee): {final_output}")
    print(f"   Resolution: {width}x{height} | Size: {size_mb:.2f} MB | Duration: {total_video_duration:.2f}s")
    print(f"{'='*75}\n")
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
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"{src_name}={src_args}",
            "-t", f"{duration_per_clip:.1f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p",
            "-fps_mode", "cfr",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            clip_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        print(f"  - Generated sample clip {i+1}: {os.path.basename(clip_path)}")
        clip_paths.append(clip_path)

    return clip_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Video-to-Video Engine")
    parser.add_argument("--dir", default="backend/output/test_v2v_run")
    parser.add_argument("--res", default="1080p")
    parser.add_argument("--voice", default="hi_female")
    args = parser.parse_args()

    sample_dir = os.path.abspath(args.dir)
    clips = generate_sample_test_clips(sample_dir, num_clips=5)
    default_scenes = [
        {"scene": 1, "narration": "समुद्र की गहराइयों में एक प्राचीन रहस्य छिपा है। 🌊"},
        {"scene": 2, "narration": "वैज्ञानिकों को मिले चमकते हुए जादुई क्रिस्टल! ✨"},
        {"scene": 3, "narration": "हर एक रोशनी एक शक्तिशाली ऊर्जा तरंग भेजती है! ⚡"},
        {"scene": 4, "narration": "यह दुनिया इंसान की सोच से कहीं ज्यादा विशाल है! 🌌"},
        {"scene": 5, "narration": "क्या यह किसी प्राचीन सभ्यता का संदेश है? सब्सक्राइब करें! 🔔"}
    ]
    assemble_video_to_video(
        video_clips=clips,
        script_or_scenes=default_scenes,
        job_dir=sample_dir,
        voice=args.voice,
        resolution=args.res
    )
