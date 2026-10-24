"""
Publish The Magic Pot (जादुई मटका) to both YouTube Shorts and Instagram Reels.
"""

import sys
import os
import json
import time
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
from scripts.upload_tracker import record_upload, is_uploaded
from scripts.upload_instagram_reel import get_instagram_client

JOB_DIR = os.path.join(backend_dir, "output", "magic_pot")
VIDEO_PATH = os.path.join(JOB_DIR, "final_video.mp4")
COVER_PATH = os.path.join(JOB_DIR, "scene_1.jpg")

TITLE = "मिट्टी में मिला एक जादुई मटका! जो डाला 100 गुना हो गया! 🏺✨ The Magic Pot | 3D Hindi Kahaniya #Shorts"

IG_CAPTION = """मिट्टी में मिला एक जादुई मटका! जो डाला 100 गुना हो गया! 🏺✨ लालच ने क्या हश्र किया? 👇

गरीब किसान मोहन को खेत में खुदाई करते हुए मिला एक चमत्कारी मटका! जब उसने एक कुल्हाड़ी रखी, तो सौ कुल्हाड़ियां बाहर आ गईं! 🪓 जब तांबे का सिक्का डाला, तो सोने का ढेर लग गया! 💰
लेकिन लालची जमींदार धरमु ने रात में चोरी करने की कोशिश की, तो क्या हुआ? 😱

🌟 कहानी की सीख: बांटने से खुशियां बढ़ती हैं, पर लालच का फल हमेशा बुरा होता है! ❤️🌾

💬 अगर आपको यह जादुई मटका मिलता, तो आप सबसे पहले इसमें क्या डालते? Comments में बताएं! 👇
💾 इस सीख को Save करें और दोस्तों के साथ Share करें!

👉 पूरी 3D कहानी YouTube पर देखें! Link in Bio 🔗✨

#HindiReels #HindiKahaniya #MoralStories #Panchatantra #JaduiMatka #MagicPot #KidsAnimation #HindiStories #ReelsIndia #PanchatantraTales #3DAnimation #ExplorePage"""

def publish_instagram():
    print("\n" + "=" * 70)
    print("📸 CROSS-POSTING TO INSTAGRAM REELS: @magicaltaleskid")
    print("=" * 70)

    try:
        cl = get_instagram_client()
        print(f"👤 Logged in as: @{cl.username}")

        print("⏳ Uploading Reel to Instagram...")
        media = cl.clip_upload(
            path=VIDEO_PATH,
            caption=IG_CAPTION,
            thumbnail=COVER_PATH if os.path.exists(COVER_PATH) else None
        )
        reel_url = f"https://www.instagram.com/reel/{media.code}/"
        print("=" * 70)
        print(f"🎉 INSTAGRAM REEL UPLOAD SUCCESSFUL! 🚀")
        print(f"📍 Media ID  : {media.id}")
        print(f"🔗 Reel Link : {reel_url}")
        print("=" * 70)

        # Record in unified duplicate prevention tracker
        record_upload("instagram", "magic_pot", media_id=str(media.id), url=reel_url, title=f"Reel {TITLE}")

        # Post pinned comment with YouTube link
        try:
            yt_comment = "👉 इस जादुई कहानी का पूरा 3D अनुभव और अगली कहानी YouTube पर देखें! Link in Bio 🔗✨"
            cl.media_comment(media.id, yt_comment)
            print("💬 Automatically posted engagement comment directing traffic to YouTube bio link!")
        except Exception as ce:
            print(f"Note: Could not post first comment ({ce})")

        return reel_url
    except Exception as e:
        print(f"❌ Instagram Reel upload error: {e}")
        return None

def main():
    # 1. Record YouTube upload that already succeeded
    yt_id = "vPdF1JQcZz8"
    yt_url = f"https://www.youtube.com/shorts/{yt_id}"
    record_upload("youtube", "magic_pot", media_id=yt_id, url=yt_url, title=TITLE)
    print(f"✅ YouTube Upload already confirmed and tracked: {yt_url}")

    # 2. Upload to Instagram
    ig_url = publish_instagram()

    print("\n" + "=" * 75)
    print("🎉 MULTI-PLATFORM PUBLISHING COMPLETED!")
    print(f"  • YouTube Shorts : {yt_url}")
    if ig_url:
        print(f"  • Instagram Reel : {ig_url}")
    print("=" * 75)

if __name__ == "__main__":
    main()
