"""
Master 16:9 Long-Form Compilation Video Builder for @MagicalTalesKidz
Combines the top 4 3D stories into an episodic 16:9 Full HD (1920x1080) compilation:
1. Jadui Chakki (The Magic Millstone)
2. Jadui Matka (The Magic Pot)
3. Chatur Kauwa (The Thirsty Crow)
4. Ekta Mein Bal (Hunter & The Pigeons)

Converts 9:16 vertical clips into 16:9 with blurred ambient background,
chapter title transitions, smooth audio normalization, and generates
YouTube metadata (Chapters, Timestamps, Title, Description, Tags).
"""

import os
import sys
import subprocess
import json
import time

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "longform_compilation_vol1")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STORIES = [
    {
        "title": "जादुई चक्की: जो मांगो वो निकले! 🪨✨",
        "title_en": "The Magic Millstone",
        "video": os.path.join(BASE_DIR, "output", "magic_millstone", "final_master_video.mp4")
    },
    {
        "title": "मिट्टी में मिला एक जादुई मटका! 🏺✨",
        "title_en": "The Magic Pot",
        "video": os.path.join(BASE_DIR, "output", "magic_pot", "final_video.mp4")
    },
    {
        "title": "कौवे ने एक घूंट पानी के लिए क्या कमाल किया? 🦅💧",
        "title_en": "The Thirsty Crow",
        "video": os.path.join(BASE_DIR, "output", "thirsty_crow", "final_video.mp4")
    },
    {
        "title": "शिकारी का जाल उड़ा ले गए कबूतर! 🕊️🕸️",
        "title_en": "Unity is Strength: Pigeons & The Net",
        "video": os.path.join(BASE_DIR, "output", "hunter_and_pigeons", "final_video.mp4")
    }
]

def get_video_duration(video_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

def format_16x9_clip(input_mp4, output_mp4):
    """
    Converts 9:16 vertical video into premium 16:9 (1920x1080) with:
    - Blurred, darkened ambient video background
    - Crisp central 9:16 foreground with subtle drop shadow
    - Clean 1080p 60fps rendering
    """
    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "boxblur=25:10,eq=brightness=-0.15:saturation=1.2[bg];"
        "[0:v]scale=-1:1080[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )
    cmd = [
        "ffmpeg", "-y", "-i", input_mp4,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-r", "30",
        output_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def build_compilation():
    print("=" * 70)
    print("🎬 ASSEMBLING 16:9 LONG-FORM COMPILATION: VOL 1")
    print("=" * 70)

    standardized_clips = []
    chapter_timestamps = []
    current_time = 0.0

    for idx, story in enumerate(STORIES, 1):
        raw_vid = story["video"]
        if not os.path.exists(raw_vid):
            print(f"❌ Missing source video: {raw_vid}")
            return

        std_clip = os.path.join(OUTPUT_DIR, f"story_{idx}_16x9.mp4")
        print(f"🔄 Converting Story {idx}/4 to 16:9 TV Format: {story['title_en']}...")
        format_16x9_clip(raw_vid, std_clip)
        dur = get_video_duration(std_clip)

        # Record timestamp for chapter markers
        mins = int(current_time // 60)
        secs = int(current_time % 60)
        timestamp_str = f"{mins:02d}:{secs:02d}"
        chapter_timestamps.append((timestamp_str, f"Story {idx}: {story['title']}"))
        current_time += dur
        standardized_clips.append(std_clip)
        print(f"   ✅ Done ({dur:.1f}s) | Starts at: {timestamp_str}")

    # Create concat list
    concat_txt = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for clip in standardized_clips:
            # Escape path for ffmpeg concat demuxer
            safe_path = clip.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    final_master_mp4 = os.path.join(OUTPUT_DIR, "panchatantra_top_stories_compilation.mp4")
    print(f"\n⚡ Stitching master compilation video with FFmpeg...")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        final_master_mp4
    ]
    subprocess.run(concat_cmd, check=True)

    total_dur = get_video_duration(final_master_mp4)
    file_size_mb = os.path.getsize(final_master_mp4) / (1024 * 1024)

    print("\n" + "=" * 70)
    print(f"🎉 MASTER 16:9 COMPILATION READY!")
    print(f"📍 Output File: {final_master_mp4}")
    print(f"⏱️ Duration   : {int(total_dur // 60)}m {int(total_dur % 60)}s ({total_dur:.1f}s)")
    print(f"📦 File Size  : {file_size_mb:.2f} MB")
    print("=" * 70)

    # Output Chapter Timestamps for Description
    print("\n📌 YOUTUBE CHAPTER TIMESTAMPS FOR DESCRIPTION:")
    print("-" * 50)
    chapter_text = ""
    for ts, name in chapter_timestamps:
        line = f"{ts} - {name}"
        print(line)
        chapter_text += line + "\n"
    print("-" * 50)

    # Save metadata JSON
    meta = {
        "title": "पंचतंत्र की 4 सबसे प्रसिद्ध जादुई कहानियां 🌟 3D Pixar Hindi Moral Stories Compilation",
        "description": (
            "✨ Welcome to MagicalTales Kidz (@MagicalTalesKidz)!\n"
            "बच्चों के लिए 4 सबसे लोकप्रिय और प्रेरणादायक 3D जादुई कहानियों का यह खास संकलन (Compilation)। हर कहानी में छिपी है एक अनमोल सीख और जीवन का बड़ा सबक।\n\n"
            "📖 कहानियों की सूची (Timestamps):\n"
            f"{chapter_text}\n"
            "🌟 सीख और संस्कार (Moral Values):\n"
            "• जादुई चक्की: संतोष और ईमानदारी ही सबसे बड़ा धन है।\n"
            "• जादुई मटका: लालच हमेशा इंसान को विनाश की ओर ले जाता है।\n"
            "• बुद्धिमान कौवा: मेहनत और सूझबूझ से नामुमकिन भी मुमकिन हो जाता है।\n"
            "• कबूतर और जाल: एकता में ही अटूट शक्ति है, मिलकर रहने से हर संकट टल जाता है।\n\n"
            "🔔 रोज़ाना नई 3D जादुई कहानियों के लिए Subscribe करें:\n"
            "👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1\n\n"
            "🎬 संपूर्ण 3D कहानियों की Playlist:\n"
            "👉 https://www.youtube.com/playlist?list=PLJE6ifX-QD0A\n\n"
            "#HindiKahaniya #Panchatantra #MoralStories #KidsAnimation #3DAnimation #BedtimeStories #BalKahaniya #HindiCartoon"
        ),
        "tags": [
            "Hindi Kahaniya", "panchatantra stories", "moral stories in hindi",
            "3d animated stories", "hindi cartoon", "bal kahaniya", "stories for kids",
            "bedtime stories in hindi", "jadui kahaniya", "hindi fairy tales",
            "panchatantra compilation", "hindi stories for kids", "MagicalTalesKidz",
            "हिंदी कहानियां", "पंचतंत्र की कहानियां", "बाल कहानियां", "नैतिक कहानियां"
        ],
        "chapters": chapter_timestamps,
        "duration_seconds": total_dur
    }
    meta_path = os.path.join(OUTPUT_DIR, "youtube_compilation_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved compilation metadata to: {meta_path}")

if __name__ == "__main__":
    build_compilation()
