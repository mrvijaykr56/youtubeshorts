import os
import subprocess
import json
from pydub import AudioSegment

_gpu_encoder = None

def detect_best_gpu_encoder() -> str:
    """
    Autosenses the best available hardware-accelerated video encoder on the system
    by performing a genuine, lightweight 1-frame transcode test at runtime.
    Caches the result to avoid spawning subprocesses repeatedly.
    """
    global _gpu_encoder
    if _gpu_encoder is not None:
        return _gpu_encoder
        
    candidates = ["h264_nvenc", "h264_qsv", "h264_amf", "h264_videotoolbox"]
    for enc in candidates:
        test_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=128x128",
            "-t", "0.04",
            "-c:v", enc,
            "-f", "null",
            "-"
        ]
        try:
            res = subprocess.run(test_cmd, capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                _gpu_encoder = enc
                print(f"[tutorial_video_generator] Hardware-transcoding encoder selected and verified: {_gpu_encoder}", flush=True)
                return _gpu_encoder
        except Exception:
            pass
            
    _gpu_encoder = "libx264"
    print(f"[tutorial_video_generator] No functional hardware-accelerated GPU encoder detected. Falling back to software: {_gpu_encoder}", flush=True)
    return _gpu_encoder


def get_video_encoder_args(crf=None):
    """
    Returns FFmpeg encoding arguments optimized for maximum text legibility and quality.
    Utilizes GPU hardware encoders when available at visually lossless bitrates,
    falling back to CPU libx264 with stillimage tuning to keep vector text razor-sharp.
    """
    encoder = detect_best_gpu_encoder()
    
    # Restrict to visually lossless range (low qp / crf)
    target_crf = crf if crf is not None else 10
    target_crf = min(target_crf, 12)
    
    if encoder == "h264_nvenc":
        args = [
            "-c:v", "h264_nvenc",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        # visually lossless Constant QP
        args.extend(["-rc", "constqp", "-qp", str(target_crf)])
        return args
        
    elif encoder == "h264_qsv":
        args = [
            "-c:v", "h264_qsv",
            "-preset", "veryfast",
            "-pix_fmt", "nv12",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        args.extend(["-global_quality", str(target_crf)])
        return args
        
    elif encoder == "h264_videotoolbox":
        args = [
            "-c:v", "h264_videotoolbox",
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M",
            "-q:v", "75"  # High quality index
        ]
        return args
        
    elif encoder == "h264_amf":
        args = [
            "-c:v", "h264_amf",
            "-pix_fmt", "nv12",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        args.extend(["-rc", "cqp", "-qp_i", str(target_crf), "-qp_p", str(target_crf)])
        return args
        
    else:  # libx264 software fallback with stillimage tuning for pristine vector text legibility
        args = [
            "-c:v", "libx264",
            "-preset", "slow",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M",
            "-crf", str(target_crf)
        ]
        return args


def _make_step_overlay_filter(step_label: str, width: int, height: int) -> str:
    """
    Returns an FFmpeg drawtext vf filter fragment that renders a tutorial step
    label (e.g. 'STEP 1' / 'INTRODUCTION') as a clean pill-shaped overlay.
    """
    safe_label = step_label.upper().replace("'", "").replace("\\", "").replace(":", "")
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttf",
    ]
    fontfile_arg = ""
    for fp in font_candidates:
        if os.path.exists(fp):
            safe_fp = fp.replace("\\", "/").replace(":", "\\:")
            fontfile_arg = f"fontfile='{safe_fp}':"
            break
            
    scale_factor = height / 1920.0
    font_size = int(46 * scale_factor)
    border_w = int(18 * scale_factor)
    margin_x = int(44 * scale_factor)
    margin_y = int(52 * scale_factor)
    
    return (
        f"drawtext={fontfile_arg}"
        f"text='{safe_label}':"
        f"fontsize={font_size}:fontcolor=white:"
        f"x={margin_x}:y={margin_y}:"
        f"box=1:boxcolor=0x1a1a2e@0.82:boxborderw={border_w}"
    )


def _make_image_clip_ffmpeg(img_path: str, duration: float, width: int, height: int, output_path: str,
                             step_label: str = None, is_first: bool = False, is_last: bool = False):
    """
    Creates a perfectly static silent video clip for text slide frames.
    Static rendering prevents resampling noise and keeps the vector-sharp text pristine.
    """
    FPS = 30
    total_frames = int(duration * FPS)
    if total_frames <= 0:
        total_frames = 1
    
    # 1. Static scale pass to target output vertical resolution
    vf_filter = f"scale={width}:{height}"

    # 2. Dynamic White Flash Cut Transition on Scene Changes:
    if not is_first:
        vf_filter += ",fade=t=in:st=0:d=0.08:color=white"
    if is_last:
        outro_fade_dur = 0.45
        vf_filter += f",fade=t=out:st={duration - outro_fade_dur:.3f}:d={outro_fade_dur}:color=black"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", img_path,
        "-vf", vf_filter,
        "-t", f"{duration:.3f}",
        "-r", str(FPS)
    ] + get_video_encoder_args(crf=18) + [
        "-g", str(FPS),
        "-keyint_min", str(FPS),
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg slide clip failed:\n{result.stderr}")


def generate_video(
    audio_path: str,
    srt_path: str,
    output_path: str,
    image_paths: list | None = None,
    music_track: str = "none",
    caption_style: str = "elegant",
    music_volume: float = 0.12,
    script: str = "",
    tutorial_steps: list | None = None,
    resolution: str = "4k"
) -> str:
    """
    Compiles vertical educational step-by-step videos from slides.
    Supports dynamic resolution (1080p Full HD vs 4K Ultra HD) for master-grade sharpness.
    """
    res_clean = str(resolution).lower().strip()
    if "1080" in res_clean:
        width, height = 1080, 1920
        print("[tutorial_video_generator] Compiling master vertical video in 1080p Full HD (1080x1920)!", flush=True)
    else:
        width, height = 2160, 3840
        print("[tutorial_video_generator] Compiling master vertical video in 4K Ultra HD (2160x3840)!", flush=True)
    
    audio = AudioSegment.from_file(audio_path)
    narration_duration = len(audio) / 1000.0
    duration = narration_duration
    
    base_video_path = output_path.replace(".mp4", "_base.mp4")

    if image_paths and len(image_paths) > 0:
        # Calculate dynamic scene durations based on Whisper segments or spoken word count
        segments_json_path = srt_path.replace(".ass", "_segments.json").replace(".srt", "_segments.json")
        scene_durations = []
        loaded_from_whisper = False

        # Extract word counts per scene from storyboard script for accurate timing
        scene_word_counts = []
        if script:
            try:
                from scripts.script_polisher import parse_storyboard
                scenes = parse_storyboard(script)
                if len(scenes) == len(image_paths):
                    scene_word_counts = [max(1, len(s.get("narration", "").split())) for s in scenes]
            except Exception:
                pass
        
        if os.path.exists(segments_json_path):
            try:
                with open(segments_json_path, "r", encoding="utf-8") as f:
                    segments_data = json.load(f)
                
                if len(segments_data) == len(image_paths):
                    print(f"[tutorial_video_generator] 1:1 Whisper segment to scene alignment...", flush=True)
                    for i in range(len(image_paths)):
                        start = segments_data[i]["start"]
                        if i < len(image_paths) - 1:
                            end = segments_data[i+1]["start"]
                        else:
                            end = narration_duration
                        scene_durations.append(max(0.5, end - start))
                    loaded_from_whisper = True
            except Exception as e:
                print(f"[tutorial_video_generator] Warning: segments parse failed: {e}", flush=True)
                
        if not loaded_from_whisper:
            if scene_word_counts and sum(scene_word_counts) > 0:
                print(f"[tutorial_video_generator] Aligning scenes proportionally based on spoken word counts: {scene_word_counts}", flush=True)
                total_words = sum(scene_word_counts)
                raw_durs = [(wc / total_words) * narration_duration for wc in scene_word_counts]
                # Enforce minimum 1.0s per scene so fast scenes don't flash
                clamped_durs = [max(1.0, d) for d in raw_durs]
                scale = narration_duration / sum(clamped_durs)
                scene_durations = [d * scale for d in clamped_durs]
            else:
                print(f"[tutorial_video_generator] Falling back to standard equal split...", flush=True)
                clip_dur = narration_duration / len(image_paths)
                scene_durations = [clip_dur] * len(image_paths)

        # Outro padding
        duration = narration_duration + 2.0

        # Convert each slide image into a TIMED static clip
        scene_paths = []
        for i, img_path in enumerate(image_paths):
            scene_out = output_path.replace(".mp4", f"_scene_{i:02d}.mp4")
            scene_dur = scene_durations[i]
            if i == len(image_paths) - 1:
                scene_dur += 2.0
            is_first = (i == 0)
            is_last = (i == len(image_paths) - 1)
            print(f"[tutorial_video_generator] Building slide clip {i+1}/{len(image_paths)} ({scene_dur:.2f}s) label='{step_label}'", flush=True)
            _make_image_clip_ffmpeg(img_path, scene_dur, width, height, scene_out, step_label=step_label,
                                    is_first=is_first, is_last=is_last)
            scene_paths.append(scene_out)

        # Concat slides
        concat_list_path = output_path.replace(".mp4", "_concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for sp in scene_paths:
                safe_sp = sp.replace("\\", "/")
                f.write(f"file '{safe_sp}'\n")

        # Set background music
        music_path = ""
        if music_track in ["lofi", "upbeat"]:
            possible_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", f"{music_track}.mp3")
            if os.path.exists(possible_path):
                music_path = possible_path

        whoosh_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", "whoosh.mp3")
        has_whoosh = os.path.exists(whoosh_path) and len(image_paths) > 1

        # Build FFmpeg inputs
        ffmpeg_inputs = [
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-i", audio_path
        ]
        
        next_idx = 2
        music_idx = -1
        if music_path:
            ffmpeg_inputs.extend(["-i", music_path])
            music_idx = next_idx
            next_idx += 1
            
        whoosh_indices = []
        if has_whoosh:
            num_transitions = len(image_paths) - 1
            for _ in range(num_transitions):
                ffmpeg_inputs.extend(["-i", whoosh_path])
                whoosh_indices.append(next_idx)
                next_idx += 1

        # Audio filter graphs
        filter_parts = []
        if music_idx != -1:
            filter_parts.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voice_compress][voice_mix]")
            mix_inputs = ["[voice_mix]"]
        else:
            filter_parts.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[voice]")
            mix_inputs = ["[voice]"]
        
        if music_idx != -1:
            filter_parts.append(f"[{music_idx}:a]volume={music_volume:.3f}[bg_raw]")
            # Sidechain Ducking
            filter_parts.append(f"[bg_raw][voice_compress]sidechaincompress=threshold=0.10:ratio=6:attack=40:release=200[bg]")
            mix_inputs.append("[bg]")
            
        if whoosh_indices:
            cumulative_time = 0.0
            for idx, w_idx in enumerate(whoosh_indices):
                cumulative_time += scene_durations[idx]
                delay_ms = int(cumulative_time * 1000)
                filter_parts.append(f"[{w_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.35[whoosh_{idx}]")
                mix_inputs.append(f"[whoosh_{idx}]")
                
        num_mix = len(mix_inputs)
        mix_str = "".join(mix_inputs)
        if num_mix > 1:
            filter_parts.append(f"{mix_str}amix=inputs={num_mix}:duration=longest,atrim=0:{duration:.3f},afade=t=out:st={duration-1.0:.3f}:d=1.0[a]")
        else:
            filter_parts.append("[voice]anull[a]")
            
        filter_complex_str = ";".join(filter_parts)

        # Mix command
        concat_cmd = [
            "ffmpeg", "-y"
        ] + ffmpeg_inputs + [
            "-filter_complex", filter_complex_str,
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            base_video_path
        ]

        try:
            result = subprocess.run(concat_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr}")
        finally:
            for sp in scene_paths:
                if os.path.exists(sp):
                    try: os.remove(sp)
                    except Exception: pass
            if os.path.exists(concat_list_path):
                try: os.remove(concat_list_path)
                except Exception: pass
    else:
        # Fallback dark background
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x141428:size={width}x{height}:rate=30",
            "-i", audio_path,
            "-filter_complex", "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]",
            "-map", "0:v:0",
            "-map", "[a]"
        ] + get_video_encoder_args(crf=18) + [
            "-c:a", "aac", "-shortest",
            base_video_path
        ]
        subprocess.run(cmd, check=True)

    # Burn ASS subtitles
    try:
        safe_srt_path = os.path.relpath(srt_path, os.getcwd()).replace("\\", "/")
    except Exception:
        safe_srt_path = srt_path.replace("\\", "/")
        if ":" in safe_srt_path:
            parts = safe_srt_path.split(":", 1)
            safe_srt_path = f"{parts[0]}\\:{parts[1]}"

    vf_filter = (
        f"drawbox=x=0:y=ih-24:w=iw:h=14:color=black@0.4:t=fill,"
        f"drawbox=x=0:y=ih-24:w='iw*(t/{duration:.3f})':h=14:color=0x00F0FF@0.9:t=fill,"
        f"drawbox=x='iw*(t/{duration:.3f})-6':y=ih-26:w=6:h=18:color=white@0.95:t=fill,"
        f"subtitles='{safe_srt_path}'"
    )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", base_video_path,
        "-vf", vf_filter,
        "-c:a", "copy"
    ] + get_video_encoder_args(crf=18) + [
        output_path
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitles burn failed:\n{result.stderr}")

    if os.path.exists(base_video_path):
        os.remove(base_video_path)

    print(f"[tutorial_video_generator] Slide video complete: {os.path.getsize(output_path)/1024:.1f} KB")
    return output_path
