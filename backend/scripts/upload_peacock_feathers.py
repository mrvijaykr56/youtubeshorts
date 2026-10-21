import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.youtube_uploader import upload_video

video_path = os.path.abspath("backend/output/peacock_feathers/final_video.mp4")

if not os.path.exists(video_path):
    print(f"Error: Video not found at {video_path}")
    sys.exit(1)

title = "The Peacock Who Lost His Feathers! 🦚😢 | Kids Moral Stories #Shorts"

description = """Proud peacock Neel loved dancing by the forest pond, admiring his glittering turquoise feathers! 🦚✨

When a sudden freezing storm struck the forest, Neel chose to spread his giant tail like an umbrella to protect shivering baby bunnies and fawns. But the fierce wind ripped his beautiful feathers away, leaving him heartbroken and bare. Watch how true kindness brings the most magical transformation! 🌈❤️

🌟 Moral of the Story:
True beauty isn't about feathers or looks—it's the kindness inside your heart! When you care for others, your soul shines brightest. ❤️✨

🔔 Subscribe to @MagicalTalesKidz for magical 3D moral bedtime stories and fairy tales for kids!
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #PeacockStory #BedtimeStories #MoralStories #HindiKahaniya #FairyTales #3DAnimation #PixarStyle #YouTubeShorts #Shorts
"""

tags = [
    "MagicalTalesKidz",
    "kids stories",
    "peacock story for kids",
    "moral stories for kids",
    "bedtime stories",
    "hindi kahaniya",
    "fairy tales",
    "neel the peacock",
    "true beauty story",
    "3d animated stories",
    "pixar style",
    "shorts",
    "yt shorts"
]

print("=" * 60)
print(f"🚀 Uploading 'The Peacock Who Lost His Feathers!' to @MagicalTalesKidz...")
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
