import os
import sys
import time

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.youtube_uploader import upload_video

videos_to_upload = [
    {
        "id_name": "diwali_elephant",
        "video_path": os.path.abspath("backend/output/diwali_elephant/final_video.mp4"),
        "title": "The Baby Elephant Who Shared His ONLY Diya! 🐘🪔 | Kids Moral Stories #Shorts",
        "description": """What happens when a kind baby elephant gives away his ONLY Diwali light? 🐘✨

Little Golu was celebrating Diwali in the forest when he found a sad little white bunny sitting in the dark. Without a second thought, Golu handed over his only flickering diya. Watch what happens when true kindness lights up the world! 🪔❤️

🌟 Moral of the Story:
The more happiness we share, the brighter our world becomes! 

🔔 Subscribe to @MagicalTalesKidz for magical 3D moral bedtime stories and fairy tales for kids!
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #DiwaliStory #BabyElephant #MoralStories #HindiKahaniya #BedtimeStories #3DAnimation #PixarStyle #YouTubeShorts #Shorts
""",
        "tags": [
            "MagicalTalesKidz",
            "kids stories",
            "baby elephant story",
            "diwali stories for kids",
            "moral stories",
            "bedtime stories",
            "hindi kahaniya",
            "fairy tales",
            "3d animated stories",
            "pixar style",
            "shorts",
            "yt shorts",
            "golu elephant"
        ]
    },
    {
        "id_name": "diwali_lion",
        "video_path": os.path.abspath("backend/output/diwali_lion/final_video.mp4"),
        "title": "The Brave Little Lion Who Saved Diwali! 🦁🪔 | Bedtime Stories #Shorts",
        "description": """It was Diwali night when a sudden fierce storm extinguished every single light in the forest! 🌬️🪔

All the little animals cried in the dark, but brave little lion cub Sheru smiled and set off into the deep forest to find a way. Deep in a secret cave, he discovered hundreds of glowing golden fireflies... watch how Sheru brings Diwali light back to all his friends! 🌟🦁

🌟 Moral of the Story:
Even the smallest hero can bring light and joy to others!

🔔 Subscribe to @MagicalTalesKidz for daily animated fairy tales and bedtime stories for kids!
👉 https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#MagicalTalesKidz #KidsStories #DiwaliStory #LionCub #MoralStories #HindiKahaniya #BedtimeStories #3DAnimation #PixarStyle #YouTubeShorts #Shorts
""",
        "tags": [
            "MagicalTalesKidz",
            "kids stories",
            "lion story for kids",
            "diwali stories",
            "sheru the lion",
            "moral stories for kids",
            "bedtime stories",
            "hindi kahaniya",
            "fairy tales",
            "3d animation",
            "shorts",
            "yt shorts"
        ]
    }
]

print("=" * 65)
print("🚀 BATCH UPLOADING TO @MagicalTalesKidz")
print("=" * 65)

uploaded_results = []

for idx, item in enumerate(videos_to_upload, 1):
    v_path = item["video_path"]
    print(f"\n[{idx}/{len(videos_to_upload)}] Uploading: {item['id_name']}...")
    print(f"   Title: {item['title']}")
    print(f"   Path: {v_path}")
    
    if not os.path.exists(v_path):
        print(f"   ❌ Error: File not found at {v_path}")
        continue

    try:
        vid_id = upload_video(
            video_path=v_path,
            title=item["title"],
            description=item["description"],
            tags=item["tags"],
            privacy_status="private",
            category_id="1"
        )
        if vid_id:
            print(f"   ✅ SUCCESS! Video ID: {vid_id}")
            print(f"   YouTube Studio: https://studio.youtube.com/video/{vid_id}/edit")
            print(f"   Shorts Link: https://www.youtube.com/shorts/{vid_id}")
            uploaded_results.append({
                "name": item["id_name"],
                "video_id": vid_id,
                "url": f"https://www.youtube.com/shorts/{vid_id}",
                "studio_url": f"https://studio.youtube.com/video/{vid_id}/edit"
            })
        else:
            print("   ❌ Upload returned None.")
    except Exception as e:
        print(f"   ❌ Upload error: {e}")

    if idx < len(videos_to_upload):
        print("Waiting 5 seconds before next upload...")
        time.sleep(5)

print("\n" + "=" * 65)
print("🎉 BATCH UPLOAD SUMMARY:")
for r in uploaded_results:
    print(f" - {r['name']}: {r['url']} (Studio: {r['studio_url']})")
print("=" * 65)
