import os
import subprocess
import json
from pydub import AudioSegment

_gpu_encoder = None

def detect_best_gpu_encoder() -> str:
    """
    Autosenses the best available hardware-accelerated video encoder on the system
    by performing a genuine, lightweight 1-frame transcode test at runtime.
    Caches the result for high-performance reuse.
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
                print(f"[video_generator] Hardware-transcoding encoder selected and verified: {_gpu_encoder}", flush=True)
                return _gpu_encoder
        except Exception:
            pass
            
    _gpu_encoder = "libx264"
    print(f"[video_generator] No functional hardware-accelerated GPU encoder detected. Falling back to software: {_gpu_encoder}", flush=True)
    return _gpu_encoder


def get_video_encoder_args(crf=None):
    """
    Returns high-fidelity FFmpeg arguments tailored to the autosensed GPU encoder,
    optimized specifically for massive, pristine vertical Ultra 4K video encoding.
    """
    encoder = detect_best_gpu_encoder()
    
    # Visual lossless tuning: set CRF equivalent based on encoder type
    # For NVIDIA/QSV/AMF/CPU we lock target bitrates to a massive 50 Megabits per second
    # to guarantee absolute 4K detail retention.
    if encoder == "h264_nvenc":
        args = [
            "-c:v", "h264_nvenc",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        if crf is not None:
            args.extend(["-rc", "constqp", "-qp", str(min(crf, 15))])
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
        if crf is not None:
            args.extend(["-global_quality", str(min(crf, 18))])
        return args
        
    elif encoder == "h264_videotoolbox":
        args = [
            "-c:v", "h264_videotoolbox",
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        if crf is not None:
            args.extend(["-q:v", "65"])
        return args
        
    elif encoder == "h264_amf":
        args = [
            "-c:v", "h264_amf",
            "-pix_fmt", "nv12",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        if crf is not None:
            args.extend(["-rc", "cqp", "-qp_i", str(min(crf, 18)), "-qp_p", str(min(crf, 18))])
        return args
        
    else:  # libx264 software fallback
        args = [
            "-c:v", "libx264",
            "-preset", "slow",       # Better quality than veryfast at same bitrate
            "-pix_fmt", "yuv420p",
            "-b:v", "50M",
            "-maxrate", "60M",
            "-bufsize", "100M"
        ]
        if crf is not None:
            args.extend(["-crf", str(crf)])
        return args


def _make_image_clip_ffmpeg(img_path: str, duration: float, width: int, height: int, output_path: str,
                             motion_type: str = "zoom_in",
                             is_first: bool = False, is_last: bool = False):
    """
    Uses FFmpeg to scale an image and create a fixed-duration silent video clip at 30fps.
    Applies a smooth Ken Burns motion effect (zoom_in, zoom_out, pan_right, pan_left).
    30fps is used for smoother zoompan sub-pixel stepping on YouTube Shorts displays.
    """
    FPS = 30
    total_frames = int(duration * FPS)
    if total_frames <= 0:
        total_frames = 1
    
    # Scale image to be 10% larger than target to allow crop movement without showing borders
    scale_w = int(width * 1.1)
    scale_h = int(height * 1.1)
    
    # 1. Base upscale with aspect ratio increase
    vf_filter = f"scale={scale_w}:{scale_h}:force_original_aspect_ratio=increase"

    # Scale sway amplitude proportionally with resolution so effect is visible at 4K
    sway_amp = max(5, int(5 * height / 1920))
    fade_dur = 0.55   # 550ms — cinematic standard (was 350ms)

    # 2. Dynamic time-based Crop filter matching motion_type with Organic Handheld Sway Simulator
    if motion_type == "zoom_in":
        vf_filter += f",crop='{width}*(1.10-0.10*n/{total_frames})':'{height}*(1.10-0.10*n/{total_frames})':'(in_w-out_w)/2 + {sway_amp}*sin(2*PI*n/25)':'(in_h-out_h)/2 + {sway_amp}*cos(2*PI*n/25)'"
    elif motion_type == "zoom_out":
        vf_filter += f",crop='{width}*(1.00+0.10*n/{total_frames})':'{height}*(1.00+0.10*n/{total_frames})':'(in_w-out_w)/2 + {sway_amp}*sin(2*PI*n/25)':'(in_h-out_h)/2 + {sway_amp}*cos(2*PI*n/25)'"
    elif motion_type == "pan_right":
        vf_filter += f",crop='{width}':'{height}':'(in_w-out_w)*(n/{total_frames}) + {sway_amp}*sin(2*PI*n/25)':'(in_h-out_h)/2 + {sway_amp}*cos(2*PI*n/25)'"
    elif motion_type == "pan_left":
        vf_filter += f",crop='{width}':'{height}':'(in_w-out_w)*(1-n/{total_frames}) + {sway_amp}*sin(2*PI*n/25)':'(in_h-out_h)/2 + {sway_amp}*cos(2*PI*n/25)'"
    else:
        vf_filter += f",crop='{width}':'{height}':'(in_w-out_w)/2 + {sway_amp}*sin(2*PI*n/25)':'(in_h-out_h)/2 + {sway_amp}*cos(2*PI*n/25)'"

    # 3. Final scale pass to target output vertical resolution
    vf_filter += f",scale={width}:{height}"

    # 4. Cinematic Color Grade & Vignette
    vf_filter += f",vignette=0.39,eq=contrast=1.12:saturation=1.12:brightness=0.01"

    # 5. Resolution-scaled film grain (lighter on 1080p so it doesn't clog subtitle text)
    grain_strength = 4 if height >= 2160 else 2
    vf_filter += f",noise=alls={grain_strength}:allf=t+u"

    # 5b. Organic Ambient Motion Overlay (Dynamic Warm Light Leak & Floating Bokeh Mote Drift)
    # A soft warm golden light flare that slowly sweeps across the upper frame
    vf_filter += f",drawbox=x=in_w*0.25:y=0:w=in_w*0.5:h=in_h*0.35:color=0xffb347@0.04:t=fill"

    # 6. Dynamic White Flash Cut Transition on Scene Changes (fallback when xfade is not active):
    # On scene changes, inject an ultra-fast high-energy white lens impact flash (80ms).
    if not is_first and motion_type == "flash_cut":
        vf_filter += ",fade=t=in:st=0:d=0.08:color=white"
    
    # Smooth outro fade-to-black only at the very end of the final video clip
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
        raise RuntimeError(f"FFmpeg scene clip failed:\n{result.stderr}")


def _create_xfade_video(scene_paths: list[str], scene_durations: list[float], transition_style: str, output_video_path: str, width: int, height: int, crf: int = 18) -> bool:
    """
    Combines scene clips using FFmpeg xfade filter for cinematic optical scene transitions.
    Supported styles:
      - 'whip_pan': smooth left/right sweeps
      - 'dissolve': blur crossfade
      - 'flash': lens impact flash
      - 'slide': directional push
      - 'dynamic': alternating mix of transitions
    """
    if len(scene_paths) <= 1:
        return False

    TRANSITION_DUR = 0.35  # 350ms transition window

    style_map = {
        "whip_pan": ["smoothleft", "smoothright", "slideleft", "slideright"],
        "dissolve": ["dissolve", "fade", "fadeblack"],
        "flash": ["fadewhite", "circlecrop"],
        "slide": ["slideup", "slidedown", "slideleft"],
        "dynamic": ["smoothleft", "dissolve", "fadewhite", "slideup", "smoothright"]
    }
    transitions_pool = style_map.get(transition_style, style_map["dynamic"])

    cmd = ["ffmpeg", "-y"]
    for sp in scene_paths:
        cmd.extend(["-i", sp])

    filter_chains = []
    # Calculate transition offsets
    cur_offset = max(0.1, scene_durations[0])
    last_v = "0:v"

    for i in range(1, len(scene_paths)):
        next_v = f"{i}:v"
        out_v = f"v{i}" if i < len(scene_paths) - 1 else "v_final"
        trans = transitions_pool[(i - 1) % len(transitions_pool)]

        chain = f"[{last_v}][{next_v}]xfade=transition={trans}:duration={TRANSITION_DUR:.2f}:offset={cur_offset:.3f}[{out_v}]"
        filter_chains.append(chain)

        last_v = out_v
        if i < len(scene_paths) - 1:
            cur_offset += max(0.1, scene_durations[i])

    filter_str = ";".join(filter_chains)
    cmd.extend([
        "-filter_complex", filter_str,
        "-map", "[v_final]"
    ])
    cmd.extend(get_video_encoder_args(crf=crf))
    cmd.extend([output_video_path])

    try:
        print(f"[video_generator] Rendering cinematic xfade transitions ({transition_style}) across {len(scene_paths)} scenes...", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 1000:
            print(f"[video_generator] [OK] Cinematic xfade transitions rendered successfully!", flush=True)
            return True
        else:
            print(f"[video_generator] Notice: xfade fallback to concat: {res.stderr[:200]}", flush=True)
            return False
    except Exception as e:
        print(f"[video_generator] Notice: xfade fallback to concat ({e})", flush=True)
        return False


def generate_video(
    audio_path: str,
    srt_path: str,
    output_path: str,
    image_paths: list | None = None,
    music_track: str = "none",
    caption_style: str = "elegant",
    music_volume: float = 0.12,
    script: str = "",
    resolution: str = "4k",
    transition_style: str = "dynamic"
) -> str:
    """
    Generates a 9:16 vertical video using dynamic AI images as background with Ken Burns zoom.
    Supports dynamic resolution (1080p Full HD vs 4K Ultra HD) for master-grade sharpness.
    Mixes copyright-free background music if specified with automatic sidechain compression ducking.
    Burns in styled captions (Standard Bottom vs TikTok Middle Flash).
    transition_style: 'dynamic', 'whip_pan', 'dissolve', 'flash', 'slide', or 'none'.
    """
    # Respect user selected resolution (1080p Full HD vs 4K Ultra HD)
    res_clean = str(resolution).lower().strip()
    if "1080" in res_clean:
        width, height = 1080, 1920
        print("[video_generator] Rendering final master video in 1080p Full HD (1080x1920)!", flush=True)
    else:
        width, height = 2160, 3840
        print("[video_generator] Rendering final master video in 4K Ultra HD (2160x3840)!", flush=True)
    audio = AudioSegment.from_file(audio_path)
    narration_duration = len(audio) / 1000.0
    duration = narration_duration

    print(f"[video_generator] Audio duration: {narration_duration:.2f}s, Music: {music_track}, Style: {caption_style}")

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
                
                # If segment count maps 1:1 with scenes, use precise segment time offsets
                if len(segments_data) == len(image_paths):
                    print(f"[video_generator] Perfect 1:1 Whisper segment to scene alignment detected!", flush=True)
                    for i in range(len(image_paths)):
                        start = segments_data[i]["start"]
                        if i < len(image_paths) - 1:
                            end = segments_data[i+1]["start"]
                        else:
                            end = narration_duration
                        scene_durations.append(max(0.5, end - start))
                    loaded_from_whisper = True
            except Exception as e:
                print(f"[video_generator] Warning: failed to parse segments JSON: {e}", flush=True)
                
        if not loaded_from_whisper:
            if scene_word_counts and sum(scene_word_counts) > 0:
                print(f"[video_generator] Aligning scenes proportionally based on spoken word counts: {scene_word_counts}", flush=True)
                total_words = sum(scene_word_counts)
                raw_durs = [(wc / total_words) * narration_duration for wc in scene_word_counts]
                # Enforce minimum 1.0s per scene so fast scenes don't flash
                clamped_durs = [max(1.0, d) for d in raw_durs]
                scale = narration_duration / sum(clamped_durs)
                scene_durations = [d * scale for d in clamped_durs]
            else:
                print(f"[video_generator] Fallback to equal split durations...", flush=True)
                clip_dur = narration_duration / len(image_paths)
                scene_durations = [clip_dur] * len(image_paths)

        # Add 2-second Outro Card padding to final video duration
        duration = narration_duration + 2.0

        # Convert each AI image into a timed zoompan video clip with alternating motions.
        scene_paths = []
        motions = ["zoom_in", "zoom_out", "pan_right", "pan_left"]
        for i, img_path in enumerate(image_paths):
            scene_out = output_path.replace(".mp4", f"_scene_{i:02d}.mp4")
            motion_type = motions[i % len(motions)]
            scene_dur = scene_durations[i]
            # Extend the very last scene clip by 2.0 seconds for the Outro CTA Card
            if i == len(image_paths) - 1:
                scene_dur += 2.0
            print(f"[video_generator] Creating scene {i+1}/{len(image_paths)} ({scene_dur:.2f}s) motion={motion_type}", flush=True)
            is_first = (i == 0)
            is_last = (i == len(image_paths) - 1)
            # Add transition overlap duration to each clip except the last when xfade is active
            clip_dur = scene_dur
            if transition_style != "none" and not is_last:
                clip_dur += 0.35
            _make_image_clip_ffmpeg(img_path, clip_dur, width, height, scene_out,
                                    motion_type=motion_type,
                                    is_first=is_first, is_last=is_last)
            scene_paths.append(scene_out)

        # Step 2: Render transitions (xfade) or fallback to concat list
        xfade_video_path = output_path.replace(".mp4", "_xfade.mp4")
        used_xfade = False
        if transition_style != "none" and len(scene_paths) > 1:
            used_xfade = _create_xfade_video(scene_paths, scene_durations, transition_style, xfade_video_path, width, height)

        concat_list_path = output_path.replace(".mp4", "_concat.txt")
        if not used_xfade:
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for sp in scene_paths:
                    safe_sp = sp.replace("\\", "/")
                    f.write(f"file '{safe_sp}'\n")

        # Step 3: Mix audio with Sidechain Compression (Ducking)
        music_path = ""
        if music_track in ["lofi", "upbeat"]:
            possible_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", f"{music_track}.mp3")
            if os.path.exists(possible_path):
                music_path = possible_path
                print(f"[video_generator] Found background music track at: {music_path}", flush=True)

        whoosh_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", "whoosh.mp3")
        has_whoosh = os.path.exists(whoosh_path) and len(image_paths) > 1

        # Track and build FFmpeg inputs dynamically
        if used_xfade:
            ffmpeg_inputs = [
                "-i", xfade_video_path,
                "-i", audio_path
            ]
        else:
            ffmpeg_inputs = [
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-i", audio_path
            ]
        
        # Input index mapping:
        # Index 0: concat video
        # Index 1: main narration audio
        next_idx = 2
        
        music_idx = -1
        if music_path:
            ffmpeg_inputs.extend(["-i", music_path])
            music_idx = next_idx
            next_idx += 1
            
        whoosh_indices = []
        if has_whoosh:
            num_transitions = len(image_paths) - 1
            print(f"[video_generator] Found transition whoosh SFX at: {whoosh_path}. Loading {num_transitions} instances.", flush=True)
            for _ in range(num_transitions):
                ffmpeg_inputs.extend(["-i", whoosh_path])
                whoosh_indices.append(next_idx)
                next_idx += 1

        # Build FFmpeg filter_complex strings dynamically
        filter_parts = []
        
        # 1. Main narration audio: Apply R128 loudness normalization
        # If we have background music, we must split the voice track into two streams using asplit:
        # [voice_compress] to control the sidechaincompress ducking, and [voice_mix] to actually mix in the final audio.
        # This prevents FFmpeg's "Stream specifier matches no streams" error from double-consuming a stream.
        if music_idx != -1:
            filter_parts.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[voice_compress][voice_mix]")
            mix_inputs = ["[voice_mix]"]
        else:
            filter_parts.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[voice]")
            mix_inputs = ["[voice]"]
        
        # 2. Background music: Set custom background volume and apply Sidechain ducking
        if music_idx != -1:
            filter_parts.append(f"[{music_idx}:a]volume={music_volume:.3f}[bg_raw]")
            # Fast-Response Sidechain Ducking: threshold=0.10, ratio=6, attack=40ms, release=200ms
            # This allows the background music to instantly swell up during natural verbal pauses and ellipses,
            # and duck back down the millisecond the narrator resumes speaking.
            filter_parts.append(f"[bg_raw][voice_compress]sidechaincompress=threshold=0.10:ratio=6:attack=40:release=200[bg]")
            mix_inputs.append("[bg]")
            
        # 3. Transition Whooshes: Apply delay and custom transition volume based on cumulative scene cuts
        if whoosh_indices:
            cumulative_time = 0.0
            for idx, w_idx in enumerate(whoosh_indices):
                cumulative_time += scene_durations[idx]
                delay_ms = int(cumulative_time * 1000)
                # Apply delay (both channels for stereo support) and volume=0.35
                filter_parts.append(f"[{w_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.35[whoosh_{idx}]")
                mix_inputs.append(f"[whoosh_{idx}]")
                
        # 4. Blend all audio inputs using amix with normalize=0 and lookahead limiter
        # IMPORTANT: amix by default has normalize=1 and dropout_transition=2.
        # When short transition whooshes (0.43s) reach EOF, default amix dynamically recalibrates
        # and ramps up the volume divisor (from 1/6 to 1/5 to 1/4... to 1/2), causing the voice volume
        # to creep up and end 4x louder (+13.6 dB) at the climax of the video.
        # Setting normalize=0 disables dynamic gain ramps, and alimiter guarantees True Peak protection (-1.0 dB).
        num_mix = len(mix_inputs)
        mix_str = "".join(mix_inputs)
        if num_mix > 1:
            # atrim after amix ensures the final audio is exactly the narration + 2s outro duration
            # alimiter=limit=0.89 (-1.0 dBFS) with level=false prevents clipping without pumping quiet passages
            # afade smoothly fades out the final 1.0 second
            filter_parts.append(
                f"{mix_str}amix=inputs={num_mix}:duration=longest:normalize=0,"
                f"atrim=0:{duration:.3f},"
                f"alimiter=limit=0.89:level=false:attack=5:release=50,"
                f"afade=t=out:st={duration-1.0:.3f}:d=1.0[a]"
            )
        else:
            filter_parts.append("[voice]alimiter=limit=0.89:level=false[a]")
            
        filter_complex_str = ";".join(filter_parts)

        # Assemble and execute final FFmpeg concat and audio mix command
        # Use stream-copy for video (saves a full encode pass — subtitle burn will re-encode)
        concat_cmd = [
            "ffmpeg", "-y"
        ] + ffmpeg_inputs + [
            "-filter_complex", filter_complex_str,
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",   # Stream-copy video — no re-encode here, saving time & quality
            "-c:a", "aac",
            "-b:a", "192k",  # Broadcast-quality audio (was unspecified ~128kbps default)
            "-shortest",
            base_video_path
        ]

        try:
            result = subprocess.run(concat_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr}")
        finally:
            # Always clean up temp scene clips, even on failure
            for sp in scene_paths:
                if os.path.exists(sp):
                    try: os.remove(sp)
                    except Exception: pass
            if os.path.exists(concat_list_path):
                try: os.remove(concat_list_path)
                except Exception: pass

    else:
        # Fallback: dark gradient background with loudnorm narration audio
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x141428:size={width}x{height}:rate=30",
            "-i", audio_path,
            "-filter_complex", "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]",
            "-map", "0:v:0",
            "-map", "[a]"
        ] + get_video_encoder_args(crf=18) + [
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            base_video_path
        ]
        subprocess.run(cmd, check=True)

    # Step 4: Burn subtitles with style mappings
    # Convert subtitles path to a relative path to avoid absolute drive letter colons (e.g. C:) which crash FFmpeg on Windows
    try:
        safe_srt_path = os.path.relpath(srt_path, os.getcwd()).replace("\\", "/")
    except Exception:
        safe_srt_path = srt_path.replace("\\", "/")
        if ":" in safe_srt_path:
            parts = safe_srt_path.split(":", 1)
            safe_srt_path = f"{parts[0]}\\:{parts[1]}"

    # All output is now .ass (Advanced SubStation Alpha) — always contains
    # embedded style tags. Never use force_style overrides for .ass files.
    # (Legacy .srt branch removed — system always generates .ass via Whisper.)
    # Phase 4: Subtitle burning pass (clean frame without bottom scrubber line)
    vf_filter = f"subtitles='{safe_srt_path}'"

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", base_video_path,
        "-vf", vf_filter,
        "-c:a", "copy"  # Audio already at 192k AAC from concat step — no re-encode needed
    ] + get_video_encoder_args(crf=18) + [
        output_path
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle burn failed:\n{result.stderr}")

    # Cleanup base video
    if os.path.exists(base_video_path):
        os.remove(base_video_path)

    print(f"[video_generator] Final video complete: {os.path.getsize(output_path)/1024:.1f} KB")
    return output_path
