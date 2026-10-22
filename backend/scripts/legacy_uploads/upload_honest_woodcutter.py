"""
Upload & Publish Script for Short #11: The Honest Woodcutter & The Golden Axe
"""

import os
import sys
import sqlite3
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token_file = os.path.join(backend_dir, "token.json")
video_path = os.path.join(backend_dir, "output", "honest_woodcutter", "final_video.mp4")

scopes = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

PLAYLIST_ID = "PLJE6ifX-QD0A"
TITLE = "कुल्हाड़ी नदी में गिरी, जलपरी ने क्या दिया? 🪓✨ Honest Woodcutter | 3D Hindi Kahaniya #Shorts"

DESCRIPTION = """घने जंगल में गरीब लकड़हारे कबीर की एकमात्र लोहे की कुल्हाड़ी नदी में गिर गई। लेकिन जब दिव्य जलपरी 24K सोने और चांदी की कुल्हाड़ी लेकर आई, तो कबीर ने क्या किया? देखिए पंचतंत्र की यह अमर और प्रेरणादायक 3D कहानी! 🪓✨

🌟 कहानी की सीख (Moral of the Story):
सच्ची ईमानदारी दुनिया की सबसे बड़ी दौलत है। जो इंसान सच के रास्ते पर चलता है, उसे बिना मांगे ही सब कुछ मिल जाता है! ❤️💎

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation #3DAnimation #MagicalTales #HindiStories #HonestWoodcutter #GoldenAxe #BalKahani
"""

TAGS = [
    "MagicalTalesKidz",
    "hindi kahaniya",
    "moral stories",
    "panchatantra stories",
    "honest woodcutter story",
    "sone ki kulhadi",
    "imandar lakadhara",
    "kids animation",
    "3d animated stories",
    "hindi cartoon",
    "bal kahaniya",
    "bedtime stories in hindi",
    "shorts",
    "yt shorts"
]

PINNED_COMMENT = "🪓 क्या आपने भी कभी कबीर की तरह सच बोलकर किसी का दिल जीता है? कमेंट में 🪓 लिखें और ऐसी जादुई 3D कहानियों के लिए @MagicalTalesKidz को Subscribe करें! ❤️🔔"

def get_service():
    creds = Credentials.from_authorized_user_file(token_file, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def main():
    print("=" * 65)
    print("🚀 Uploading Short #11: The Honest Woodcutter & The Golden Axe!")
    print(f"   Video: {video_path}")
    print(f"   Title: {TITLE}")
    print(f"   Privacy: PUBLIC")
    print(f"   Audio: Pure Clean hi-IN-SwaraNeural Voiceover")
    print("=" * 65)

    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    yt = get_service()

    # 1. Upload Video
    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "1"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Upload progress: {int(status.progress() * 100)}%", flush=True)

    video_id = response.get("id")
    print(f"\n🎉 UPLOAD SUCCESSFUL! Video ID: {video_id}")
    print(f"   Direct Short URL: https://www.youtube.com/shorts/{video_id}")
    print(f"   Studio URL: https://studio.youtube.com/video/{video_id}/edit")

    # 2. Add to Official Playlist
    try:
        yt.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": PLAYLIST_ID,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"   ✅ Added {video_id} to official playlist ({PLAYLIST_ID})!")
    except Exception as e:
        print(f"   ⚠️ Note on adding to playlist: {e}")

    # 3. Post Pinned Engagement Comment
    try:
        yt.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": PINNED_COMMENT
                        }
                    }
                }
            }
        ).execute()
        print("   ✅ Pinned engagement question comment posted successfully!")
    except Exception as e:
        print(f"   ⚠️ Note on posting comment: {e}")

    # 4. Save to jobs.db
    try:
        db_path = os.path.join(backend_dir, "jobs.db")
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT OR REPLACE INTO jobs (job_id, state, message, created_at, updated_at) VALUES (?, ?, ?, datetime('now'), datetime('now'))",
            ("honest_woodcutter", "completed", f"Uploaded to @MagicalTalesKidz (ID: {video_id})")
        )
        conn.commit()
        conn.close()
        print("   ✅ Recorded job in jobs.db")
    except Exception as e:
        print(f"   ⚠️ Database log note: {e}")

if __name__ == "__main__":
    main()
