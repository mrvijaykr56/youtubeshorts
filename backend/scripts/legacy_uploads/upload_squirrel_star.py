import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.youtube_uploader import upload_video

video_path = os.path.abspath("backend/output/squirrel_star/final_video.mp4")

if not os.path.exists(video_path):
    print(f"Error: Video not found at {video_path}")
    sys.exit(1)

title = "The Baby Squirrel Who Found A Star! 🐿️⭐ | Kids Bedtime Stories #Shorts"

description = """Under the quiet midnight sky, brave baby squirrel Cheeku saw a tiny glowing shooting star tumble into the deep enchanted forest! 🐿️✨

While all the other animals were fast asleep, little Cheeku crept through the dark and found the frightened little star trembling in the leaves. Cupping it gently in his tiny paws, Cheeku embarked on a daring journey to climb the tallest tree and send his new friend back home. Watch till the end to see the magical stardust shower! 🌟❤️

🌟 Moral of the Story:
No one is too small to have a big heart and do brave things! When you help a friend, your own light shines brightest. ✨

🔔 Subscribe to @MagicalTalesKidz for magical 3D moral bedtime stories and fairy tales for kids!
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #SquirrelStory #BedtimeStories #MoralStories #HindiKahaniya #FairyTales #3DAnimation #PixarStyle #YouTubeShorts #Shorts
"""

tags = [
    "MagicalTalesKidz",
    "kids stories",
    "squirrel story for kids",
    "baby squirrel",
    "bedtime stories",
    "moral stories for kids",
    "hindi kahaniya",
    "fairy tales",
    "shooting star story",
    "3d animated stories",
    "pixar style",
    "shorts",
    "yt shorts"
]

print("=" * 60)
print(f"🚀 Uploading 'The Baby Squirrel Who Found A Star!' to @MagicalTalesKidz...")
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
