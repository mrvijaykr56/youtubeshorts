import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.youtube_uploader import upload_video

video_path = os.path.abspath("backend/output/miku_laddoo/final_video.mp4")

if not os.path.exists(video_path):
    print(f"Error: Video not found at {video_path}")
    sys.exit(1)

title = "The Magic Laddoo Pot! 🐒🍬 Miku's Secret Kindness #Shorts"

description = """Once upon a time in an enchanted forest, naughty little monkey Miku found a glowing golden map hidden inside an ancient banyan tree! 🐒✨ 

The map promised a delicious pot of magical golden laddoos, but the pot would only open with a true act of kindness. Will Miku save a helpless little squirrel or chase the sweets alone? Watch till the end to see the magical lesson! 🍯❤️

🌟 Moral of the Story:
Kindness is the greatest treasure in the world! When you help others, magic happens. ❤️✨

🔔 Subscribe to @MagicalTalesKidz for magical 3D bedtime stories, fairy tales, and moral adventures every week! 
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #BedtimeStories #MoralStories #HindiKahaniya #MonkeyStory #3DAnimation #PixarStyle #YouTubeShorts #Shorts #Cartoon
"""

tags = [
    "MagicalTalesKidz",
    "kids stories",
    "moral stories for kids",
    "bedtime stories",
    "hindi kahaniya",
    "monkey stories",
    "animated stories",
    "fairy tales",
    "shorts",
    "yt shorts",
    "moral kahaniya",
    "stories in hindi",
    "miku monkey",
    "3d animation"
]

print("=" * 60)
print(f"🚀 Uploading Short to YouTube Channel @MagicalTalesKidz...")
print(f"   Video: {video_path}")
print(f"   Title: {title}")
print(f"   Privacy: private (Safe for review in YouTube Studio)")
print("=" * 60)

video_id = upload_video(
    video_path=video_path,
    title=title,
    description=description,
    tags=tags,
    privacy_status="private",
    category_id="1"
)

if video_id:
    print(f"\n🎉 UPLOAD SUCCESSFUL!")
    print(f"   Video ID: {video_id}")
    print(f"   YouTube Studio: https://studio.youtube.com/video/{video_id}/edit")
    print(f"   Direct Short Link: https://www.youtube.com/shorts/{video_id}")
else:
    print("\n❌ Upload failed or skipped.")
