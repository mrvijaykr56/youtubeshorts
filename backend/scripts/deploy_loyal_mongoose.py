# -*- coding: utf-8 -*-
"""
Deploy / Schedule The Loyal Mongoose (वफादार नेवला) to YouTube Shorts & Instagram Reels
- Video: backend/output/loyal_mongoose/final_video.mp4
- Cover: backend/output/loyal_mongoose/scene_1.jpg
- YouTube: Scheduled for 18:30 IST, language=hi, madeForKids=False, official playlist, pinned comment
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

VIDEO_PATH = os.path.join(BASE_DIR, "output", "loyal_mongoose", "final_video.mp4")
COVER_PATH = os.path.join(BASE_DIR, "output", "loyal_mongoose", "scene_1.jpg")

TITLE = "वफादार नेवला: जल्दबाज़ी का पछतावा! 🐾💔 The Loyal Mongoose | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """#Shorts #Panchatantra #HindiKahaniya #MoralStories #LoyalMongoose #3DAnimation #MagicalTalesKidz #KidsStories

एक वफादार नेवले ने अपनी जान पर खेलकर बच्चे को खूंखार सांप से बचाया — पर मां की एक जल्दबाज़ी ने सब छीन लिया! 🐾💔 क्या मां को अपनी भूल का एहसास हुआ? देखो इस दिल को छू लेने वाली 3D पंचतंत्र कहानी में! 🌟

🎯 कहानी का सार (Moral of the Story):
जल्दबाज़ी में बिना सच जाने लिया गया फैसला सिर्फ पछतावा लाता है। कभी भी क्रोध या हड़बड़ी में निर्णय न लें! 🌺🙏

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

💖 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#HindiStories #BalKahaniya #PanchatantraStories #HindiMoralStories #KidsAnimation #YtShorts #ViralShorts #NevlaAurSaanp
"""

TAGS = [
    "वफादार नेवला", "Loyal Mongoose Story Hindi", "Panchatantra Stories in Hindi",
    "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "Bal Kahaniya",
    "Chintu Monkey", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां",
    "पंचतंत्र की कहानियां", "Kids Animation Hindi", "नेवला और सांप की कहानी"
]

YT_PINNED_COMMENT = "🐾 क्या मां को नेवले पर शक करने से पहले अंदर जाकर देखना चाहिए था? Comments में बताओ! 💬👇"

IG_CAPTION = """वफादार नेवले की कहानी — जल्दबाज़ी का फैसला सिर्फ पछतावा लाता है! 🐾💔

इस 3D पंचतंत्र कहानी में सीखो कि बिना सच जाने कभी भी कोई कठोर कदम नहीं उठाना चाहिए। 🌟

💖 Full 16:9 4K episodes on YouTube: @MagicalTalesKidz (Link in bio!)
.
.
#Panchatantra #HindiKahaniya #MoralStories #LoyalMongoose #KidsAnimation #3DAnimation #HindiCartoon #BalKahaniya #MagicalTalesKidz #Shorts #IndianKidsContent #NevlaAurSaanp"""

IG_PINNED_COMMENT = "🎬 Full stories on YouTube! Link in bio 👆 Subscribe करो @MagicalTalesKidz 💖"


def deploy_to_youtube(schedule_iso_utc=None):
    print("\n" + "=" * 70)
    print("▶️ DEPLOYING / SCHEDULING LOYAL MONGOOSE TO YOUTUBE SHORTS (@MagicalTalesKidz)")
    print("=" * 70)

    from googleapiclient.http import MediaFileUpload
    from scripts.manage_channel import get_authenticated_service, get_or_create_playlist

    print(f"📁 Video Path : {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH) / (1024*1024):.2f} MB)")
    print(f"📌 Title      : {TITLE}")

    youtube = get_authenticated_service()

    status_body = {
        "selfDeclaredMadeForKids": False
    }

    if schedule_iso_utc:
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = schedule_iso_utc
        print(f"⏰ Scheduling video to go Public at: {schedule_iso_utc} (18:30 IST)")
    else:
        status_body["privacyStatus"] = "public"
        print("🌐 Setting video status to PUBLIC immediately")

    request_body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "1",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": status_body
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=MediaFileUpload(VIDEO_PATH, chunksize=-1, resumable=True)
    )

    response = request.execute()
    video_id = response.get("id")
    if not video_id:
        print("❌ YouTube upload failed.")
        return None

    short_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"\n✅ Video successfully uploaded to YouTube!")
    print(f"🔗 Video ID   : {video_id}")
    print(f"🌐 Shorts URL : {short_url}")

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

    # Post Pinned Comment if Public
    if not schedule_iso_utc:
        try:
            time.sleep(5)
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
    else:
        print("⏭️ Skipping pinned comment for scheduled/private video.")

    return video_id


def deploy_to_instagram():
    print("\n" + "=" * 70)
    print("📸 DEPLOYING LOYAL MONGOOSE TO INSTAGRAM REELS (@magicaltaleskid)")
    print("=" * 70)

    try:
        from scripts.upload_instagram_reel import get_instagram_client
        cl = get_instagram_client()
        if not cl:
            print("❌ Could not obtain authenticated Instagram client.")
            return None

        print(f"📁 Video Path : {VIDEO_PATH}")
        print(f"🖼️ Cover Path : {COVER_PATH}")
        print("⏳ Uploading Reel to Instagram...")

        media = cl.clip_upload(
            path=VIDEO_PATH,
            caption=IG_CAPTION,
            thumbnail=COVER_PATH
        )
        media_id = media.id
        media_code = media.code
        reel_url = f"https://www.instagram.com/reel/{media_code}/"
        print(f"\n🎉 REEL PUBLISHED TO INSTAGRAM SUCCESSFULLY!")
        print(f"🆔 Media ID   : {media_id}")
        print(f"🔖 Reel Code  : {media_code}")
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
            data.setdefault("youtube", {})["loyal_mongoose"] = {
                "title": TITLE,
                "video_id": yt_video_id,
                "url": f"https://www.youtube.com/shorts/{yt_video_id}",
                "uploaded_at": now_str,
                "status": "scheduled_or_published"
            }

        if ig_result and ig_result.get("media_id"):
            data.setdefault("instagram", {})["loyal_mongoose"] = {
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", action="store_true", help="Schedule for 2026-11-07 18:30 IST")
    args = parser.parse_args()

    # 18:30 IST Nov 7 = 13:00:00Z UTC
    schedule_utc = "2026-11-07T13:00:00.000Z" if args.schedule else None

    print(f"🚀 INITIATING DEPLOYMENT FOR: {TITLE}")
    yt_id = deploy_to_youtube(schedule_iso_utc=schedule_utc)
    ig_res = None
    if not args.schedule:
        ig_res = deploy_to_instagram()
    update_tracker(yt_id, ig_res)
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT / SCHEDULING COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
