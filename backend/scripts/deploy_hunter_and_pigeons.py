"""
Deploy Hunter & Pigeons (शिकारी और कबूतर - Unity is Strength) 3D Special to YouTube Shorts & Instagram Reels
- Video: backend/output/hunter_and_pigeons/final_video.mp4
- Cover: backend/output/hunter_and_pigeons/scene_3.jpg
- YouTube: Enforce Hindi audio/lang, madeForKids=False, add to official playlist, pin comment
- Instagram: Upload Reel with thumbnail, post caption, pin bio CTA comment
- Updates uploads_tracker.json
"""

import os
import sys
import json
import time
from datetime import datetime

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VIDEO_PATH = os.path.join(BASE_DIR, "output", "hunter_and_pigeons", "final_video.mp4")
COVER_PATH = os.path.join(BASE_DIR, "output", "hunter_and_pigeons", "scene_3.jpg")

TITLE = "शिकारी का जाल उड़ा ले गए कबूतर! 🕊️🕸️ Unity is Strength | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """#Shorts #Panchatantra #HindiKahaniya #MoralStories #UnityIsStrength #3DAnimation #MagicalTalesKidz #KidsStories

जब जंगल में बिखरे दानों के लालच में कबूतरों का पूरा झुंड शिकारी के जाल में फंस गया, तब समझदार कबूतर चीकू ने सबको क्या जादुई मंत्र दिया? देखिए कैसे एक साथ पंख फड़फड़ाकर कबूतर पूरा जाल लेकर आसमान में उड़ गए और नन्हे चूहे मीकू ने कैसे उनकी जान बचाई! 🕊️🕸️🐭✨

🌟 कहानी की सीख (Moral of the Story):
एकता में ही अटूट शक्ति है। जब सब मिलकर कदम उठाते हैं, तो बड़े से बड़ा संकट भी पलक झपकते टल जाता है! 🌟🕊️❤️

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#HindiStories #BalKahaniya #PanchatantraStories #HindiMoralStories #KidsAnimation #Shorts #YtShorts #ViralShorts
"""

TAGS = [
    "शिकारी और कबूतर", "Panchatantra Stories in Hindi", "Unity is Strength Story",
    "Shikari Aur Kabootar", "3D Hindi Kahaniya", "Moral Stories in Hindi",
    "Kids Moral Stories", "Hindi Cartoon", "Bal Kahaniya", "Kabootar Ki Kahani",
    "Chiku Kabootar", "एकता में बल है", "MagicalTalesKidz",
    "shorts", "yt shorts", "हिंदी कहानियां", "पंचतंत्र की कहानियां"
]

YT_PINNED_COMMENT = "🕊️ क्या आपने कभी देखा है कि मिल-जुलकर काम करने से बड़ी मुसीबत हल हो गई? Comments में अपनी कहानी बताएं! 👇❤️"

IG_CAPTION = """शिकारी के भारी जाल में जब फंसे सैकड़ों कबूतर, तो कैसे एक साथ मिलकर उन्होंने किया आसमान में चमत्कार? 🕊️🕸️✨

अकेले लड़ोगे तो हार जाओगे, लेकिन जब सब एक साथ हों तो लोहे का जाल भी उड़ जाता है! एकता में ही सबसे बड़ी ताकत है। 🌟❤️

🔔 Full 16:9 4K episodes watching on YouTube: @MagicalTalesKidz (Link in bio!)
.
.
#Panchatantra #HindiKahaniya #MoralStories #UnityIsStrength #KidsAnimation #3DAnimation #ShikariAurKabootar #MagicalTalesKidz #ViralReels #ReelsIndia #PanchatantraStories #HindiStories"""

IG_PINNED_COMMENT = "🎬 पूरा 4K वीडियो देखने के लिए YouTube पर जाएं: @MagicalTalesKidz (Link in Bio!) 🔔✨"


def deploy_to_youtube():
    print("\n" + "=" * 70)
    print("▶️ DEPLOYING HUNTER & PIGEONS TO YOUTUBE SHORTS (@MagicalTalesKidz)")
    print("=" * 70)

    from scripts.youtube_uploader import upload_video
    from scripts.manage_channel import get_authenticated_service, get_or_create_playlist

    print(f"📁 Video Path : {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH) / (1024*1024):.2f} MB)")
    print(f"📌 Title      : {TITLE}")

    video_id = upload_video(
        video_path=VIDEO_PATH,
        title=TITLE,
        description=DESCRIPTION,
        tags=TAGS,
        privacy_status="public",
        category_id="1"
    )

    if not video_id:
        print("❌ YouTube upload failed.")
        return None

    short_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"\n✅ Video successfully published to YouTube!")
    print(f"🔗 Video ID   : {video_id}")
    print(f"🌐 Shorts URL : {short_url}")

    # Set language, category, and madeForKids explicitly
    youtube = get_authenticated_service()
    try:
        update_body = {
            "id": video_id,
            "snippet": {
                "title": TITLE,
                "description": DESCRIPTION,
                "tags": TAGS,
                "categoryId": "1",
                "defaultLanguage": "hi",
                "defaultAudioLanguage": "hi"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        youtube.videos().update(part="snippet,status", body=update_body).execute()
        print("✅ Enforced defaultLanguage='hi', defaultAudioLanguage='hi', madeForKids=False.")
    except Exception as upd_err:
        print(f"⚠️ Video settings update warning: {upd_err}")

    # Add to Official Playlist
    try:
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
        print(f"✅ Added to official YouTube playlist ({playlist_id}).")
    except Exception as pl_err:
        print(f"⚠️ Playlist update warning: {pl_err}")

    # Post Pinned Engagement Comment
    try:
        print("💬 Inserting official engagement magnet comment...")
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": YT_PINNED_COMMENT
                        }
                    }
                }
            }
        ).execute()
        print("✅ Engagement comment posted on YouTube!")
    except Exception as ce:
        print(f"⚠️ YouTube comment insertion note: {ce}")

    # Update uploads_tracker.json
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    try:
        tracker = {}
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker = json.load(f)
        if "youtube" not in tracker:
            tracker["youtube"] = {}
        tracker["youtube"]["hunter_and_pigeons"] = {
            "title": TITLE,
            "video_id": video_id,
            "url": short_url,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "published"
        }
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, ensure_ascii=False, indent=2)
        print("✅ Updated uploads_tracker.json for YouTube.")
    except Exception as tr_err:
        print(f"⚠️ Tracker update warning: {tr_err}")

    return video_id, short_url


def deploy_to_instagram():
    print("\n" + "=" * 70)
    print("📸 DEPLOYING HUNTER & PIGEONS TO INSTAGRAM REELS (@magicaltaleskid)")
    print("=" * 70)

    from scripts.upload_instagram_reel import get_instagram_client
    cl = get_instagram_client()
    if not cl:
        print("❌ Could not obtain authenticated Instagram client.")
        return None

    print(f"📁 Video Path : {VIDEO_PATH}")
    print(f"🖼️ Cover Path : {COVER_PATH}")
    print("⚡ Uploading Reel to Instagram (this takes ~15-30s)...")

    try:
        media = cl.clip_upload(
            path=VIDEO_PATH,
            caption=IG_CAPTION,
            thumbnail=COVER_PATH
        )
        media_id = media.id
        media_code = media.code
        reel_url = f"https://www.instagram.com/reel/{media_code}/"
        print(f"\n🎉 REEL PUBLISHED TO INSTAGRAM SUCCESSFULLY!")
        print(f"📍 Media ID   : {media_id}")
        print(f"🔗 Reel Code  : {media_code}")
        print(f"🌐 Reel URL   : {reel_url}")

        # Auto-pin call to action comment
        try:
            time.sleep(3)
            comment = cl.media_comment(media_id, IG_PINNED_COMMENT)
            cl.comment_pin(media_id, comment.pk)
            print("📌 Pinned YouTube subscriber funnel comment successfully!")
        except Exception as pin_err:
            print(f"⚠️ Comment pin warning: {pin_err}")

        # Update tracker
        tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
        try:
            tracker = {}
            if os.path.exists(tracker_file):
                with open(tracker_file, "r", encoding="utf-8") as f:
                    tracker = json.load(f)
            if "instagram" not in tracker:
                tracker["instagram"] = {}
            tracker["instagram"]["hunter_and_pigeons"] = {
                "media_id": str(media_id),
                "code": media_code,
                "url": reel_url,
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "published"
            }
            with open(tracker_file, "w", encoding="utf-8") as f:
                json.dump(tracker, f, ensure_ascii=False, indent=2)
            print("✅ Updated uploads_tracker.json for Instagram.")
        except Exception as tr_err:
            print(f"⚠️ Tracker update warning: {tr_err}")

        return media_code, reel_url
    except Exception as ig_err:
        print(f"❌ Instagram Reel upload failed: {ig_err}")
        return None


if __name__ == "__main__":
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video file missing at: {VIDEO_PATH}")
        sys.exit(1)

    yt_res = deploy_to_youtube()
    ig_res = deploy_to_instagram()

    print("\n" + "=" * 70)
    print("🏁 HUNTER & PIGEONS DEPLOYMENT SUMMARY")
    print("=" * 70)
    if yt_res:
        print(f"▶️ YouTube Shorts : {yt_res[1]}")
    else:
        print("▶️ YouTube Shorts : FAILED / SKIPPED")
    if ig_res:
        print(f"📸 Instagram Reel : {ig_res[1]}")
    else:
        print("📸 Instagram Reel : FAILED / SKIPPED")
    print("=" * 70)
