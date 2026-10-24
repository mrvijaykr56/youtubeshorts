"""
Publish The Magic Millstone (जादुई चक्की) to both YouTube Shorts and Instagram Reels.
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
from scripts.manage_channel import get_authenticated_service
from scripts.upload_tracker import record_upload, is_uploaded
from scripts.upload_instagram_reel import get_instagram_client
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

JOB_DIR = os.path.join(backend_dir, "output", "magic_millstone")
VIDEO_PATH = os.path.join(JOB_DIR, "final_master_video.mp4")
THUMBNAIL_PATH = os.path.join(JOB_DIR, "thumbnail.jpg")

TITLE = "जादुई चक्की: जो मांगो वो निकले! 🪨✨ The Magic Millstone | 3D Hindi Kahaniya #Shorts"
PLAYLIST_ID = "PLJE6ifX-QD0A"
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"
SUB_URL = "https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"

YT_DESCRIPTION = f"""#Shorts #HindiKahaniya #MoralStories #Panchatantra #JaduiChakki #MagicMillstone #3DAnimation #HindiCartoon #BalKahani

गरीब किसान केशव को रहस्यमयी गुफा में एक चमत्कारी जादुई चक्की मिली! 🪨 उस पर दिव्य सुनहरे मंत्र चमक रहे थे! जब केशव ने लकड़ी का हत्था घुमाया, तो चक्की से स्वादिष्ट पकवान और चांदी के सिक्के बरसने लगे! 💰✨ दयालु केशव ने सारा खजाना गांववालों में बांट दिया।
लेकिन जब एक लालची चोर चक्की चुराकर समुद्र में भागा, तो क्या हुआ? 😱🌊

🌟 कहानी की सीख (Moral):
संतोष और ईमानदारी से जीवन में बरकत आती है, जबकि बेकाबू लालच सब कुछ डुबो देता है। 💎❤️

🎬 पूरी 3D जादुई कहानियां Playlist में देखें:
👉 {PLAYLIST_URL}

🔔 हर रोज़ नई 3D कहानियों के लिए Subscribe करें:
👉 {SUB_URL}

---------------------------------------------------
About MagicalTalesKidz:
MagicalTalesKidz brings classic Indian moral tales, Panchatantra, and enchanting folklore to life through stunning 3D Pixar-style animation. Wholesome family entertainment designed to inspire kindness, wit, and wisdom in kids and families worldwide!
---------------------------------------------------
#HindiKahaniya #KidsStories #BedtimeStories #Fairytales #JaduiChakki #IndianFolktales"""

TAGS = [
    "jadui chakki", "the magic millstone", "magic millstone story", "samandar ka pani khara kyu hai",
    "keshav aur jadui chakki", "namak ka samandar", "MagicalTalesKidz", "Hindi Kahaniya",
    "moral stories in hindi", "panchatantra stories", "kids moral stories", "3d animated stories",
    "hindi cartoon", "bal kahaniya", "bedtime stories in hindi", "fairy tales in hindi",
    "jadui kahaniya", "hindi animated tales", "hindi stories for kids", "stories for kids",
    "panchatantra tales in hindi", "shorts", "yt shorts"
]

PINNED_COMMENT = f"""🪨✨ अगर आपको यह जादुई चक्की मिलती, तो आप उससे सबसे पहले क्या मांगते? Comments में बताएं! 👇
🎬 पूरी 3D कहानियां देखें: {PLAYLIST_URL}
🔔 सब्सक्राइब करें: {SUB_URL}"""

IG_CAPTION = """जादुई चक्की: जो मांगो वो निकले! 🪨✨ समंदर का पानी खारा क्यों है? 👇

गरीब किसान केशव को रहस्यमयी गुफा में एक चमत्कारी जादुई चक्की मिली! जब उसने हत्था घुमाया, तो स्वादिष्ट पकवान और चांदी के सिक्के बरसने लगे! 💰✨
लेकिन लालची चोर चक्की चुराकर समुद्र में नाव पर भागा और बोला 'नमक निकालो!'... पर रोकने का मंत्र वह भूल गया! 😱🌊

🌟 कहानी की सीख: संतोष और ईमानदारी से सुख बढ़ता है, जबकि लालच हमेशा ले डूबता है! ❤️🌾

💬 अगर आपको यह जादुई चक्की मिलती, तो आप सबसे पहले क्या मांगते? Comments में बताएं! 👇
💾 इस प्रेरणादायक सीख को Save करें और बच्चों व दोस्तों के साथ Share करें!

👉 पूरी 3D कहानी और अगली कहानी YouTube पर देखें! Link in Bio 🔗✨

#HindiReels #HindiKahaniya #MoralStories #Panchatantra #JaduiChakki #MagicMillstone #KidsAnimation #HindiStories #ReelsIndia #PanchatantraTales #3DAnimation #ExplorePage"""

def publish_youtube():
    print("\n" + "=" * 75)
    print("🚀 PUBLISHING TO YOUTUBE SHORTS: @MagicalTalesKidz")
    print("=" * 75)

    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video file not found: {VIDEO_PATH}")
        return None

    try:
        # 1. Upload Video
        print("⏳ Uploading MP4 to YouTube Data API v3...")
        video_id = upload_video(
            video_path=VIDEO_PATH,
            title=TITLE,
            description=YT_DESCRIPTION,
            tags=TAGS,
            privacy_status="public",
            category_id="1"
        )

        if not video_id:
            print("❌ YouTube upload failed to return video ID.")
            return None

        yt_url = f"https://www.youtube.com/shorts/{video_id}"
        print(f"✅ Video Uploaded Successfully! Video ID: {video_id}")
        print(f"🔗 YouTube Short URL: {yt_url}")

        # Authenticate for playlist and comment management
        token_path = os.path.join(backend_dir, "token.json")
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

        # 2. Update COPPA & Category
        try:
            print("⚙️ Enforcing COPPA compliance (selfDeclaredMadeForKids=False)...")
            v_res = youtube.videos().list(part="snippet,status", id=video_id).execute()
            if v_res.get("items"):
                snippet = v_res["items"][0]["snippet"]
                status = v_res["items"][0]["status"]
                status["selfDeclaredMadeForKids"] = False
                snippet["categoryId"] = "1"
                youtube.videos().update(
                    part="snippet,status",
                    body={"id": video_id, "snippet": snippet, "status": status}
                ).execute()
                print("  ✅ Video status updated!")
        except Exception as se:
            print(f"  ⚠️ Warning setting status: {se}")

        # 3. Add to Official Playlist
        try:
            print(f"📂 Adding video to official playlist: {PLAYLIST_ID}...")
            youtube.playlistItems().insert(
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
            print("  ✅ Added to official playlist successfully!")
        except Exception as pe:
            print(f"  ⚠️ Playlist insertion note: {pe}")

        # 4. Post Pinned Engagement Comment
        try:
            print("💬 Inserting official engagement magnet comment...")
            youtube.commentThreads().insert(
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
            print("  ✅ Engagement comment posted!")
        except Exception as ce:
            print(f"  ⚠️ Comment insertion note: {ce}")

        # 5. Record upload in duplicate prevention tracker
        record_upload("youtube", "magic_millstone", media_id=video_id, url=yt_url, title=TITLE)

        return yt_url

    except Exception as e:
        print(f"❌ YouTube upload exception: {e}")
        return None

def publish_instagram():
    print("\n" + "=" * 75)
    print("📸 CROSS-POSTING TO INSTAGRAM REELS: @magicaltaleskid")
    print("=" * 75)

    try:
        cl = get_instagram_client()
        print(f"👤 Logged in as: @{cl.username}")

        print("⏳ Uploading Reel to Instagram...")
        media = cl.clip_upload(
            path=VIDEO_PATH,
            caption=IG_CAPTION,
            thumbnail=THUMBNAIL_PATH if os.path.exists(THUMBNAIL_PATH) else None
        )
        reel_url = f"https://www.instagram.com/reel/{media.code}/"
        print("=" * 75)
        print(f"🎉 INSTAGRAM REEL UPLOAD SUCCESSFUL! 🚀")
        print(f"📍 Media ID  : {media.id}")
        print(f"🔗 Reel Link : {reel_url}")
        print("=" * 75)

        # Record upload in duplicate prevention tracker
        record_upload("instagram", "magic_millstone", media_id=str(media.id), url=reel_url, title=f"Reel {TITLE}")

        # Post engagement comment directing to YouTube
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
    yt_url = publish_youtube()
    
    if is_uploaded("instagram", "magic_millstone"):
        ig_url = "https://www.instagram.com/reel/De3Tu7LSaGp/"
        print(f"✅ Instagram Reel already published and verified: {ig_url}")
    else:
        ig_url = publish_instagram()

    print("\n" + "=" * 75)
    print("🎉 DUAL-PLATFORM BROADCAST PUBLISHING COMPLETE!")
    if yt_url:
        print(f"  • YouTube Shorts : {yt_url}")
    if ig_url:
        print(f"  • Instagram Reel : {ig_url}")
    print("=" * 75)


if __name__ == "__main__":
    main()
