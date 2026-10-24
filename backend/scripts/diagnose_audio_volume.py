import subprocess
import json
import re

def analyze_audio_volume(video_path):
    print(f"\n==========================================")
    print(f"Analyzing audio for: {video_path}")
    print(f"==========================================")
    
    # 1. Overall volume detect
    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", "volumedetect",
        "-vn", "-sn", "-f", "null", "NUL"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stderr.splitlines():
        if "volumedetect" in line or "max_volume" in line or "mean_volume" in line:
            print("  [OVERALL]", line.strip())

    # 2. Check duration
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    dur_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    try:
        duration = float(dur_res.stdout.strip())
    except:
        duration = 60.0

    print(f"\n  Duration: {duration:.2f}s. Analyzing loudness in 10-second segments:")
    
    # 3. Analyze 10s segments
    seg_len = 10.0
    start = 0.0
    while start < duration:
        end = min(start + seg_len, duration)
        cur_len = end - start
        if cur_len < 2.0:
            break
        seg_cmd = [
            "ffmpeg", "-ss", f"{start:.2f}", "-t", f"{cur_len:.2f}",
            "-i", video_path,
            "-af", "ebur128",
            "-vn", "-sn", "-f", "null", "NUL"
        ]
        seg_res = subprocess.run(seg_cmd, capture_output=True, text=True)
        # Parse integrated loudness and true peak
        integrated = "N/A"
        tp = "N/A"
        lines = seg_res.stderr.splitlines()
        for i, l in enumerate(lines):
            if "Integrated loudness:" in l and i + 1 < len(lines):
                integrated = lines[i+1].strip()
            if "True peak:" in l and i + 1 < len(lines):
                tp = lines[i+1].strip()
        print(f"  Segment [{start:5.1f}s - {end:5.1f}s]: Integrated={integrated} | Peak={tp}")
        start += seg_len

if __name__ == "__main__":
    import os
    files_to_test = [
        "backend/output/thirsty_crow/final_video.mp4",
        "backend/output/hunter_and_pigeons/final_video.mp4",
        "backend/output/magic_pot/final_video.mp4",
        "backend/output/magic_millstone/final_master_video.mp4"
    ]
    for f in files_to_test:
        if os.path.exists(f):
            analyze_audio_volume(f)
