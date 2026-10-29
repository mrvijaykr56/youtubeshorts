"""
Publish Festive Community Poll to Instagram Feed (@magicaltaleskid)
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

IMAGE_PATH = os.path.join(BASE_DIR, "output", "festive_poll_assets", "festive_poll_1080x1080.jpg")

CAPTION = """इस बार दीपावली और छठ पूजा पर आपके घर सबसे पसंदीदा पकवान कौन सा बनता है? 🪔✨

अपनी पसंद को VOTE करें (Comments में 1, 2, 3 या 4 लिखें) 👇

1. 🌾 ठेकुआ (Thekua) - छठ महापर्व का पावन प्रसाद
2. 🍬 काजू कतली (Kaju Katli) - दीपावली की शाही मिठाई
3. 🟡 बेसन के लड्डू (Besan Laddu) - देसी घी के दानेदार लड्डू
4. 🥟 मावे की गुजिया (Mawa Gujiya) - खास पारंपरिक गुजिया

🎬 पूरी 3D कहानियां देखने के लिए YouTube: @MagicalTalesKidz पर जाएं! (Link in Bio!) 🔔
.
.
#DiwaliSpecial #ChhathPuja #FestivePoll #Thekua #KajuKatli #BesanLaddoo #Gujiya #Diwali2026 #HindiKahaniya #MoralStories #MagicalTalesKidz #PollOfTheDay"""

PINNED_COMMENT = "👇 आपका सबसे पसंदीदा पकवान कौन सा है? 1, 2, 3 या 4 लिखकर Vote करें! ✨"

def publish_poll():
    print("=" * 70)
    print("🚀 PUBLISHING FESTIVE POLL GRAPHIC TO INSTAGRAM FEED")
    print("=" * 70)

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found at {IMAGE_PATH}")
        return None

    from scripts.upload_instagram_reel import get_instagram_client
    cl = get_instagram_client()
    if not cl:
        print("❌ Could not get Instagram client.")
        return None

    print(f"📁 Image Path: {IMAGE_PATH}")
    print("⏳ Uploading photo to Instagram feed...")

    try:
        media = cl.photo_upload(path=IMAGE_PATH, caption=CAPTION)
        post_url = f"https://www.instagram.com/p/{media.code}/"
        print("\n🎉 FESTIVE POLL POSTED TO INSTAGRAM SUCCESSFULLY!")
        print(f"📍 Media ID : {media.id}")
        print(f"🔗 Post Code: {media.code}")
        print(f"🌐 Post URL : {post_url}")

        # Pin comment
        try:
            time.sleep(3)
            c = cl.media_comment(media.id, PINNED_COMMENT)
            cl.comment_pin(media.id, c.pk)
            print("📌 Pinned voting prompt comment successfully!")
        except Exception as pin_err:
            print(f"⚠️ Comment pin warning: {pin_err}")

        return media.code, post_url
    except Exception as e:
        print(f"❌ Instagram photo upload failed: {e}")
        return None

if __name__ == "__main__":
    publish_poll()
