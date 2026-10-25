"""
Deploy Diwali Special Short to YouTube & Instagram
- Video: backend/output/diwali_magic_diya/final_video.mp4
- Uploads to YouTube with Hindi metadata, playlist addition, COPPA settings
- Uploads to Instagram Reels with cover image, curiosity caption, and pinned YouTube link
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

VIDEO_PATH = os.path.join(BASE_DIR, "output", "diwali_magic_diya", "final_video.mp4")
COVER_PATH = os.path.join(BASE_DIR, "output", "diwali_magic_diya", "scene_1.jpg")
META_PATH = os.path.join(BASE_DIR, "output", "diwali_magic_diya", "metadata.json")

TITLE = "गरीब बच्चे की जादुई दिवाली और सोने का दीया! 🪔✨ The Magic Diya | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """#Shorts #DiwaliSpecial #HindiKahaniya #MoralStories #Panchatantra #3DAnimation #DiwaliKahani #LakshmiMata #MagicalTalesKidz

दीपावली की घनी काली रात में जब अमीर सेठ के सारे विदेशी झूमर आंधी में टूट गए, तब नन्हे राजू के निस्वार्थ भाव और एक मिट्टी के दीये ने क्या चमत्कार किया? देखिए कैसे माता लक्ष्मी ने उस दीये को अमर सोने का दीया बना दिया! 🪔✨

🌟 कहानी की सीख (Moral of the Story):
सच्ची दिवाली पटाखों के शोर में नहीं, बल्कि किसी गरीब के चेहरे पर मुस्कान लाने और मन की पवित्रता में है। ❤️

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #DiwaliSpecial #DiwaliStory #HindiKahaniya #MoralStories #KidsAnimation
"""

TAGS = [
    "Diwali Hindi Story", "Diwali Special Story", "3D Diwali Cartoon",
    "Diwali Kahaniya", "The Magic Diya Hindi", "गरीब की दिवाली",
    "जादुई दीया", "दीपावली की कहानी", "Lakshmi Mata Story",
    "Moral Stories in Hindi", "3D Animated Stories", "Hindi Cartoon",
    "Bal Kahaniya", "MagicalTalesKidz", "shorts", "yt shorts",
    "हिंदी कहानियां", "पंचतंत्र की कहानियां", "नैतिक कहानियां"
]

IG_CAPTION = """दीपावली की अंधेरी रात में जब आंधी ने सब बुझा दिया, तब नन्हे राजू के मिट्टी के दीये ने क्या चमत्कार किया? 🪔✨

सच्ची दिवाली पटाखों के शोर में नहीं, बल्कि किसी गरीब के चेहरे पर मुस्कान लाने में है! ❤️

🔔 Full 16:9 4K episodes watching on YouTube: @MagicalTalesKidz (Link in bio!)
.
.
#DiwaliSpecial #DiwaliKahaniya #MoralStories #HindiKahaniya #3DAnimation #KidsStories #Diwali2026 #Diya #LakshmiPuja #Kahani #BalKahaniya #MagicalTalesKidz #ViralReels #ReelsIndia"""

PINNED_COMMENT = "🎬 पूरा 4K वीडियो देखने के लिए YouTube पर जाएं: @MagicalTalesKidz (Link in Bio!) 🔔✨"


def deploy_to_youtube():
    print("\n" + "=" * 70)
    print("▶️ DEPLOYING DIWALI SPECIAL TO YOUTUBE SHORTS (@MagicalTalesKidz)")
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
    try:
        youtube = get_authenticated_service()
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
        print(f"✅ Added to official YouTube playlist ({playlist_id}).")
    except Exception as pl_err:
        print(f"⚠️ Playlist update warning: {pl_err}")

    # Update tracker
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    try:
        tracker = {}
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker = json.load(f)
        if "youtube" not in tracker:
            tracker["youtube"] = {}
        tracker["youtube"]["diwali_magic_diya"] = {
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
    print("📸 DEPLOYING DIWALI SPECIAL TO INSTAGRAM REELS (@magicaltaleskid)")
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
            comment = cl.media_comment(media_id, PINNED_COMMENT)
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
            tracker["instagram"]["diwali_magic_diya"] = {
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
    print("🏁 DIWALI SPECIAL DEPLOYMENT SUMMARY")
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
