"""
Deploy Diwali Special (जादुई दिवाली और सोने की रंगोली - The Magic Rangoli) 3D Special to YouTube Shorts & Instagram Reels
- Video: backend/output/diwali_magic_rangoli/final_video.mp4
- Cover: backend/output/diwali_magic_rangoli/scene_1.jpg
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

VIDEO_PATH = os.path.join(BASE_DIR, "output", "diwali_magic_rangoli", "final_video.mp4")
COVER_PATH = os.path.join(BASE_DIR, "output", "diwali_magic_rangoli", "scene_1.jpg")

TITLE = "जादुई दिवाली और सोने की रंगोली! 🪔🌸 The Magic Rangoli | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """#Shorts #DiwaliSpecial #DiwaliStory #HindiKahaniya #MoralStories #3DAnimation #MagicalTalesKidz #KidsStories

दिवाली की अंधेरी रात में जब नन्ही पिंकी और चिंटू बंदर ने प्यार से फूलों की रंगोली बनाई, तो घमंडी पड़ोसी ने पटाखे फोड़कर सब कुछ बिखेर दिया! 💥🥺 लेकिन जैसे ही पिंकी ने श्रद्धा से अंतिम मिट्टी का दीया जलाया, साक्षात मां लक्ष्मी ने क्या दिव्य चमत्कार किया? देखिए कैसे साधारण रंगोली बन गई सोने की जगमगाती झील! 🪔🌸✨🪙

🌟 कहानी की सीख (Moral of the Story):
सच्ची दिवाली पटाखों के शोर में नहीं, बल्कि मन की पवित्रता और दूसरों के जीवन में खुशियां बांटने में है! 🌟🪔❤️

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Diwali2026 #DiwaliKahaniya #HindiStories #BalKahaniya #Panchatantra #KidsAnimation #YtShorts #ViralShorts #LakshmiPuja
"""

TAGS = [
    "Diwali Special Story", "Diwali Hindi Kahani", "जादुई दिवाली", "3D Diwali Cartoon",
    "Diwali Kahaniya", "Maa Lakshmi Story", "Moral Stories in Hindi", "Kids Moral Stories",
    "Hindi Cartoon", "Bal Kahaniya", "Rangoli Magic Story", "दीपावली की कहानी",
    "MagicalTalesKidz", "shorts", "yt shorts", "हिंदी कहानियां", "पंचतंत्र की कहानियां",
    "Diwali Stories for Kids", "Chintu Monkey"
]

YT_PINNED_COMMENT = "🪔 आपकी सबसे पसंदीदा दिवाली की मिठाई कौन सी है? काजू कतली या मोतीचूर के लड्डू? Comments में बताएं! 👇✨"

IG_CAPTION = """दिवाली की रात जब घमंडी पड़ोसी ने बिखेर दी नन्ही पिंकी की रंगोली, तब साक्षात मां लक्ष्मी ने क्या जादुई चमत्कार किया? 🪔🌸✨

सच्ची दिवाली पटाखों के शोर में नहीं, बल्कि दूसरों के चेहरे पर मुस्कान लाने में है! 🌟❤️

🔔 Full 16:9 4K episodes on YouTube: @MagicalTalesKidz (Link in bio!)
.
.
#DiwaliSpecial #DiwaliStory #HindiKahaniya #MoralStories #KidsAnimation #3DAnimation #MagicalTalesKidz #ViralReels #ReelsIndia #Diwali2026 #LakshmiPuja #HindiStories"""

IG_PINNED_COMMENT = "🎬 पूरा 4K वीडियो देखने के लिए YouTube पर जाएं: @MagicalTalesKidz (Link in Bio!) 🔔✨"


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
        res = youtube.commentThreads().insert(
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
        print(f"✅ Pinned comment posted (ID: {res.get('id')}).")
    except Exception as comm_err:
        print(f"⚠️ Pinned comment notice: {comm_err}")

    return video_id


def deploy_to_instagram():
    print("\n" + "=" * 70)
    print("▶️ DEPLOYING DIWALI SPECIAL TO INSTAGRAM REELS (@magicaltaleskid)")
    print("=" * 70)

    try:
        from scripts.upload_instagram_reel import get_instagram_client
        cl = get_instagram_client()
        if not cl:
            print("❌ Could not obtain authenticated Instagram client.")
            return None

        print(f"📁 Video Path : {VIDEO_PATH}")
        print(f"🖼️ Cover Path : {COVER_PATH}")
        print("⚡ Uploading Reel to Instagram (this takes ~15-30s)...")

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

        try:
            time.sleep(3)
            comment = cl.media_comment(media_id, IG_PINNED_COMMENT)
            cl.comment_pin(media_id, comment.pk)
            print("📌 Pinned YouTube subscriber funnel comment successfully!")
        except Exception as pin_err:
            print(f"⚠️ Comment pin warning: {pin_err}")

        return {"media_id": str(media_id), "code": media_code, "url": reel_url}
    except Exception as e:
        print(f"⚠️ Instagram deployment error: {e}")
        return None


def update_tracker(yt_video_id, ig_result):
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    if not os.path.exists(tracker_file):
        return

    try:
        with open(tracker_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if yt_video_id:
            data.setdefault("youtube", {})["diwali_magic_rangoli"] = {
                "title": TITLE,
                "video_id": yt_video_id,
                "url": f"https://www.youtube.com/shorts/{yt_video_id}",
                "uploaded_at": now_str,
                "status": "published"
            }

        if ig_result and ig_result.get("media_id"):
            data.setdefault("instagram", {})["diwali_magic_rangoli"] = {
                "title": TITLE,
                "media_id": ig_result.get("media_id"),
                "code": ig_result.get("code", ""),
                "url": f"https://www.instagram.com/reel/{ig_result.get('code', '')}/",
                "uploaded_at": now_str,
                "status": "published"
            }

        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Updated uploads_tracker.json persistent record.")
    except Exception as e:
        print(f"⚠️ Tracker update failed: {e}")


def main():
    print(f"🚀 INITIATING DEPLOYMENT FOR: {TITLE}")
    # YouTube is already deployed (video_id: gbVpfJPFTKk)
    yt_id = "gbVpfJPFTKk"
    ig_res = deploy_to_instagram()
    update_tracker(yt_id, ig_res)
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT RUN COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
