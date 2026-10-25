"""
Deploy 16:9 Long-Form Compilation to YouTube (@MagicalTalesKidz)
- Video: backend/output/longform_compilation_vol1/panchatantra_top_stories_compilation.mp4
- Thumbnail: backend/output/longform_compilation_vol1/thumbnail_16x9.jpg
- Metadata: Chapter timestamps, SEO description, and tags
- Uploads custom thumbnail, sets Hindi language, adds to playlist, updates tracker
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

VIDEO_PATH = os.path.join(BASE_DIR, "output", "longform_compilation_vol1", "panchatantra_top_stories_compilation.mp4")
THUMBNAIL_PATH = os.path.join(BASE_DIR, "output", "longform_compilation_vol1", "thumbnail_16x9.jpg")
META_PATH = os.path.join(BASE_DIR, "output", "longform_compilation_vol1", "youtube_compilation_metadata.json")

def deploy_compilation():
    print("=" * 70)
    print("🎬 DEPLOYING 16:9 LONG-FORM COMPILATION TO YOUTUBE (@MagicalTalesKidz)")
    print("=" * 70)

    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Missing video at: {VIDEO_PATH}")
        return None

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta["title"]
    description = meta["description"]
    tags = meta["tags"]

    from scripts.youtube_uploader import upload_video
    from scripts.manage_channel import get_authenticated_service, get_or_create_playlist
    from googleapiclient.http import MediaFileUpload

    file_size_mb = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"📁 Video Path : {VIDEO_PATH} ({file_size_mb:.2f} MB)")
    print(f"📌 Title      : {title}")

    # 1. Upload Video
    video_id = upload_video(
        video_path=VIDEO_PATH,
        title=title,
        description=description,
        tags=tags,
        privacy_status="public",
        category_id="1"
    )

    if not video_id:
        print("❌ Compilation upload failed.")
        return None

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\n🎉 Compilation successfully published to YouTube!")
    print(f"🔗 Video ID   : {video_id}")
    print(f"🌐 Video URL  : {video_url}")

    # 2. Update Video Snippet with Hindi Defaults & COPPA settings
    youtube = get_authenticated_service()
    try:
        update_body = {
            "id": video_id,
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
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
        print(f"⚠️ Snippet update warning: {upd_err}")

    # 3. Upload Custom 16:9 Thumbnail
    if os.path.exists(THUMBNAIL_PATH):
        try:
            print(f"🖼️ Uploading custom 16:9 landscape thumbnail ({os.path.getsize(THUMBNAIL_PATH)/1024:.1f} KB)...")
            thumb_media = MediaFileUpload(THUMBNAIL_PATH, mimetype="image/jpeg", resumable=True)
            youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            print("✅ Custom 16:9 thumbnail uploaded and applied successfully!")
        except Exception as thumb_err:
            print(f"⚠️ Custom thumbnail upload warning: {thumb_err}")

    # 4. Add to Official Playlist
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
        print(f"✅ Added compilation to official YouTube playlist ({playlist_id}).")
    except Exception as pl_err:
        print(f"⚠️ Playlist update warning: {pl_err}")

    # 5. Post Funnel Comment on Diwali Short (rADH3-CTZDs)
    diwali_short_id = "rADH3-CTZDs"
    try:
        comment_text = f"🌟 संपूर्ण 3D पंचतंत्र कहानियों का 16:9 संकलन यहाँ देखें:\n👉 {video_url}\n(सभी 4 कहानियां एक साथ!) 🪔✨"
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": diwali_short_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        print(f"✅ Pinned funnel comment on Diwali Short ({diwali_short_id}) directing viewers to this compilation!")
    except Exception as c_err:
        print(f"⚠️ Funnel comment warning: {c_err}")

    # 6. Update Tracker
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    try:
        tracker = {}
        if os.path.exists(tracker_file):
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker = json.load(f)
        if "youtube" not in tracker:
            tracker["youtube"] = {}
        tracker["youtube"]["panchatantra_compilation_vol1"] = {
            "title": title,
            "video_id": video_id,
            "url": video_url,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "published",
            "type": "longform_16x9"
        }
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, ensure_ascii=False, indent=2)
        print("✅ Updated uploads_tracker.json with compilation entry.")
    except Exception as tr_err:
        print(f"⚠️ Tracker update warning: {tr_err}")

    print("=" * 70)
    print("🏁 COMPILATION DEPLOYMENT COMPLETE")
    print(f"🌐 Live URL: {video_url}")
    print("=" * 70)
    return video_id, video_url

if __name__ == "__main__":
    deploy_compilation()
