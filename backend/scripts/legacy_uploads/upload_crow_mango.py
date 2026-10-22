import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.youtube_uploader import upload_video

video_path = os.path.abspath("backend/output/crow_mango/final_video.mp4")

if not os.path.exists(video_path):
    print(f"Error: Video not found at {video_path}")
    sys.exit(1)

title = "The Greedy Crow & The Golden Mango! 🦅🥭 | Kids Moral Stories #Shorts"

description = """High in a sunlit mango orchard, clever crow Kalu found a magical giant Golden Mango glowing in the trees! 🦅✨

When hungry little forest birds asked for a tiny bite, greedy Kalu flew away with the whole fruit, refusing to share. But when the heavy mango slipped into a dark, thorny bush, only teamwork and kindness could save the day. Watch how Kalu learns that true sweetness comes from sharing! 🥭❤️

🌟 Moral of the Story:
Selfishness leaves you alone, but sharing brings friends and true joy! Happiness only grows when shared. ❤️✨

🔔 Subscribe to @MagicalTalesKidz for magical 3D moral bedtime stories and fairy tales for kids!
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #CrowStory #BedtimeStories #MoralStories #HindiKahaniya #MangoStory #3DAnimation #PixarStyle #YouTubeShorts #Shorts
"""

tags = [
    "MagicalTalesKidz",
    "kids stories",
    "crow story for kids",
    "golden mango story",
    "moral stories for kids",
    "bedtime stories",
    "hindi kahaniya",
    "fairy tales",
    "greedy crow",
    "3d animated stories",
    "pixar style",
    "shorts",
    "yt shorts"
]

print("=" * 60)
print(f"🚀 Uploading 'The Greedy Crow & The Golden Mango!' to @MagicalTalesKidz...")
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
