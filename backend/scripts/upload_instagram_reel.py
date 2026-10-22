"""
Automated Instagram Reel Publisher for @magicaltaleskid
Powered by instagrapi

Features:
1. Persistent Session Management (saves session cookies to avoid repeated logins).
2. Supports 2FA (Two-Factor Authentication) and Challenge Resolution.
3. Automatically publishes 1080x1920 MP4, cover thumbnail, and SEO captions.
4. Auto-pins comment with YouTube link for subscriber cross-funneling.
5. Works seamlessly with packaged reels in backend/output/instagram_reels_packages/.
"""

import os
import sys
import time
import json
import argparse
import getpass
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    TwoFactorRequired,
    ChallengeRequired,
    LoginRequired
)

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(BASE_DIR, "output", "instagram_reels_packages")
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")
BRAND_CONFIG_FILE = os.path.join(BASE_DIR, "brand_config.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

def load_brand_config():
    if os.path.exists(BRAND_CONFIG_FILE):
        try:
            with open(BRAND_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                brand = data.get("brands", {}).get("MagicalTalesKidz", {})
                return brand
        except Exception:
            pass
    return {}

def load_env_credentials():
    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("INSTAGRAM_USERNAME="):
                    username = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("INSTAGRAM_PASSWORD="):
                    password = line.split("=", 1)[1].strip().strip('"').strip("'")
    return username, password

def get_instagram_client(code=None):
    cl = Client()
    cl.delay_range = [2, 5]  # Human-like delay between requests

    brand = load_brand_config()
    default_user = brand.get("instagram_handle", "magicaltaleskid").replace("@", "")
    env_user, env_pass = load_env_credentials()
    username = env_user or default_user
    password = env_pass

    # 1. Try loading existing session
    if os.path.exists(SESSION_FILE):
        try:
            print("🔑 Loading existing Instagram session...")
            cl.load_settings(SESSION_FILE)
            if not cl.username:
                cl.username = username
            # Verify session is still active
            cl.get_timeline_feed()
            print("✅ Session validated successfully! Logged in as: @" + cl.username)
            return cl
        except Exception as e:
            print(f"⚠️ Existing session expired or invalid ({e}). Relogging in...")

    # 2. Perform Fresh Login

    if not password:
        print(f"\n🔐 Instagram Login for @{username}")
        password = getpass.getpass("Enter Instagram Password: ")

    try:
        print(f"📡 Logging into Instagram as @{username}...")
        if code:
            cl.login(username, password, verification_code=code)
        else:
            cl.login(username, password)
        cl.dump_settings(SESSION_FILE)
        print("✅ Logged in successfully and saved session to instagram_session.json!")
        return cl
    except TwoFactorRequired:
        print("🔒 Two-Factor Authentication (2FA) is required.")
        c = code or input("Enter 2FA Security Code (SMS / Authenticator app): ").strip()
        cl.login(username, password, verification_code=c)
        cl.dump_settings(SESSION_FILE)
        print("✅ 2FA Verified! Saved session.")
        return cl
    except ChallengeRequired:
        print("⚠️ Instagram requested security verification challenge.")
        try:
            cl.challenge_resolve(cl.last_json)
            cl.dump_settings(SESSION_FILE)
            print("✅ Challenge resolved and session saved!")
            return cl
        except Exception as ce:
            print(f"❌ Could not resolve challenge automatically: {ce}")
            print("Please log into https://instagram.com in your browser once to verify, then rerun.")
            sys.exit(1)
    except BadPassword:
        print("❌ Incorrect password for Instagram account.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Login error: {e}")
        sys.exit(1)

try:
    from upload_tracker import is_uploaded, record_upload
except ImportError:
    from scripts.upload_tracker import is_uploaded, record_upload

def list_available_reels():
    print("=" * 75)
    print("📦 PACKAGED REELS STATUS & DUPLICATE TRACKER")
    print("=" * 75)
    if not os.path.exists(PKG_DIR):
        print("No packaged reels found. Run: python backend/scripts/prepare_instagram_reels.py first.")
        return []

    stories = [d for d in os.listdir(PKG_DIR) if os.path.isdir(os.path.join(PKG_DIR, d))]
    for i, s in enumerate(stories, 1):
        s_dir = os.path.join(PKG_DIR, s)
        video = next((f for f in os.listdir(s_dir) if f.endswith(".mp4")), "Missing video")
        has_cover = os.path.exists(os.path.join(s_dir, "cover_thumbnail.jpg"))
        has_caption = os.path.exists(os.path.join(s_dir, "caption.txt"))
        already_up, up_info = is_uploaded("instagram", s)

        if already_up:
            status = f"ALREADY PUBLISHED ✅ ({up_info.get('uploaded_at', '')[:10]})"
        elif video != "Missing video" and has_caption:
            status = "READY TO POST 🆕 (Unpublished)"
        else:
            status = "INCOMPLETE ⚠️"

        print(f" {i:2d}. [{s:<22}] -> {status}")
        if already_up:
            print(f"      🔗 Reel: {up_info.get('url', '')}")
    print("=" * 75)
    return stories

def upload_story_reel(cl, story_name, force=False):
    # 0. Duplicate Upload Prevention Check
    if not force:
        already_up, up_info = is_uploaded("instagram", story_name)
        if already_up:
            print("\n" + "=" * 75)
            print(f"⚠️  DUPLICATE PREVENTED: Story [{story_name}] is ALREADY published on Instagram!")
            print(f"   🔗 Reel URL   : {up_info.get('url')}")
            print(f"   📅 Uploaded At: {up_info.get('uploaded_at')}")
            print("   💡 If you intentionally want to re-upload, pass the --force flag.")
            print("=" * 75 + "\n")
            return False

    story_dir = os.path.join(PKG_DIR, story_name)
    if not os.path.exists(story_dir):
        print(f"❌ Story package not found: {story_dir}")
        return False

    # Find video
    video_path = None
    for f in os.listdir(story_dir):
        if f.endswith(".mp4"):
            video_path = os.path.join(story_dir, f)
            break

    if not video_path:
        print(f"❌ No MP4 video found in {story_dir}")
        return False

    # Find caption
    caption_path = os.path.join(story_dir, "caption.txt")
    caption = ""
    if os.path.exists(caption_path):
        with open(caption_path, "r", encoding="utf-8") as f:
            caption = f.read()

    # Find cover
    cover_path = os.path.join(story_dir, "cover_thumbnail.jpg")
    if not os.path.exists(cover_path):
        cover_path = None

    print("\n" + "=" * 70)
    print(f"🚀 UPLOADING REEL: [{story_name}] to @{cl.username}")
    print("=" * 70)
    print(f"🎥 Video   : {video_path}")
    print(f"🖼️  Cover   : {cover_path or 'Default from video'}")
    print(f"📝 Caption : {len(caption)} characters")
    print("⏳ Uploading to Instagram Reels server... (please wait)")

    try:
        media = cl.clip_upload(
            path=video_path,
            caption=caption,
            thumbnail=cover_path
        )
        reel_url = f"https://www.instagram.com/reel/{media.code}/"
        print("=" * 70)
        print(f"🎉 REEL UPLOAD SUCCESSFUL! 🚀")
        print(f"📍 Media ID  : {media.id}")
        print(f"🔗 Reel Link : {reel_url}")
        print("=" * 70)

        # Record in unified duplicate prevention tracker
        record_upload("instagram", story_name, media_id=str(media.id), url=reel_url, title=f"Reel {story_name}")

        # Optional: Post pinned comment with YouTube link
        try:
            yt_comment = "🎬 इस कहानी का पूरा 3D अनुभव हमारे YouTube चैनल पर देखें! Link bio में उपलब्ध है 👉 @magicaltaleskid ✨"
            cl.media_comment(media.id, yt_comment)
            print("💬 Automatically posted engagement comment directing traffic to YouTube bio link!")
        except Exception as ce:
            print(f"Note: Could not post first comment ({ce})")

        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automated Instagram Reel Publisher")
    parser.add_argument("--story", type=str, help="Name of story package (e.g. golden_goose, blue_jackal) or 'all'")
    parser.add_argument("--list", action="store_true", help="List all available packaged reels")
    parser.add_argument("--login", action="store_true", help="Authenticate and save session only")
    parser.add_argument("--code", type=str, help="2FA security verification code")
    parser.add_argument("--force", action="store_true", help="Force upload even if already published in tracker")
    args = parser.parse_args()

    if args.list:
        list_available_reels()
        return

    cl = get_instagram_client(code=args.code)

    if args.login:
        print("✅ Authentication complete. Session stored.")
        return

    if args.story:
        if args.story.lower() == "all":
            stories = [d for d in os.listdir(PKG_DIR) if os.path.isdir(os.path.join(PKG_DIR, d))]
            print(f"Starting batch upload for {len(stories)} reels...")
            for s in stories:
                upload_story_reel(cl, s, force=args.force)
                print("Sleeping 30s to respect rate limits...")
                time.sleep(30)
        else:
            upload_story_reel(cl, args.story, force=args.force)
    else:
        stories = list_available_reels()
        if stories:
            print(f"\nUsage:")
            print(f"  .\\backend\\venv\\Scripts\\python.exe backend\\scripts\\upload_instagram_reel.py --story {stories[0]}")
            print(f"  .\\backend\\venv\\Scripts\\python.exe backend\\scripts\\upload_instagram_reel.py --story all")

if __name__ == "__main__":
    main()
