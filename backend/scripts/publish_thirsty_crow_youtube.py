"""
Publish The Clever Crow Short to YouTube using the YouTube Data API v3.
- Uploads final_video.mp4 with optimized viral SEO
- Sets category to 1 (Film & Animation) and privacy to Public
- Adds video to official playlist
- Updates uploads_tracker.json
"""

import sys
import os
import json
from datetime import datetime

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scripts.youtube_uploader import upload_video
from scripts.manage_channel import get_authenticated_service, get_or_create_playlist

VIDEO_PATH = os.path.join(backend_dir, "output", "thirsty_crow", "final_video.mp4")
TITLE = "कौवे ने एक घूंट पानी के लिए क्या कमाल किया? 🦅💧 The Clever Crow | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """#Shorts #HindiKahaniya #MoralStories #Panchatantra #ThirstyCrow #3DAnimation #HindiCartoon #BalKahani

कड़कड़ाती धूप में जब कालू कौवा प्यास से बेहाल था, तो उसे एक पुराना मिट्टी का घड़ा मिला। लेकिन पानी बहुत नीचे था! देखिए कैसे नन्हे चतुर कौवे ने अपनी सूझबूझ और मेहनत से नामुमकिन को मुमकिन बना दिया! 🦅🏺✨

🌟 कहानी की सीख (Moral of the Story):
सच्ची समझदारी, सब्र और लगातार मेहनत से हर बड़ी से बड़ी मुश्किल हल हो जाती है।

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation
"""

TAGS = [
    "chatur kauwa", "thirsty crow", "buddhiman kauwa", "kauwa aur ghada",
    "Hindi Kahaniya", "moral stories in hindi", "panchatantra stories",
    "kids moral stories", "3d animated stories", "hindi cartoon",
    "bal kahaniya", "jadui kahaniya", "stories for kids", "shorts", "yt shorts",
    "हिंदी कहानियां", "पंचतंत्र की कहानियां", "नैतिक कहानियां", "हिंदी कार्टून"
]

def publish():
    print("=" * 70)
    print("🎬 PUBLISHING TO YOUTUBE: The Clever Crow (बुद्धिमान कौवा)")
    print("=" * 70)

    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(f"Video file not found at {VIDEO_PATH}")

    file_size_mb = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"📁 Video Path : {VIDEO_PATH} ({file_size_mb:.2f} MB)")
    print(f"📌 Title      : {TITLE}")

    # 1. Upload Video
    video_id = upload_video(
        video_path=VIDEO_PATH,
        title=TITLE,
        description=DESCRIPTION,
        tags=TAGS,
        privacy_status="public",
        category_id="1"
    )

    if not video_id:
        raise RuntimeError("YouTube upload failed — received no video ID.")

    short_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"\n✅ Video successfully published to YouTube!")
    print(f"🔗 Video ID   : {video_id}")
    print(f"🌐 Shorts URL : {short_url}")

    # 2. Add to Official Playlist
    try:
        youtube = get_authenticated_service()
        playlist_id = get_or_create_playlist(youtube)
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print("✅ Added to official YouTube playlist.")
    except Exception as pl_err:
        print(f"⚠️ Playlist update warning: {pl_err}")

    # 3. Update uploads_tracker.json
    tracker_file = os.path.join(backend_dir, "uploads_tracker.json")
    try:
        tracker = {}
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker = json.load(f)

        if "youtube" not in tracker:
            tracker["youtube"] = {}

        tracker["youtube"]["thirsty_crow"] = {
            "title": TITLE,
            "video_id": video_id,
            "url": short_url,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "published"
        }

        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, ensure_ascii=False, indent=2)

        print(f"✅ Updated uploads_tracker.json with thirsty_crow YouTube entry.")
    except Exception as tr_err:
        print(f"⚠️ Tracker update warning: {tr_err}")

    print("=" * 70)
    return video_id, short_url

if __name__ == "__main__":
    publish()
