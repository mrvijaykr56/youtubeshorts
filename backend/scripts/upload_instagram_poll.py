"""
Automated Instagram Poll / Carousel Publisher for @magicaltaleskid
Powered by instagrapi

Supports:
1. Multi-slide Carousel Feed Post (album_upload)
2. 9:16 Instagram Story Poll Template (photo_upload_to_story)
"""

import os
import sys
import argparse
from instagrapi import Client

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLL_DIR = os.path.join(BASE_DIR, "output", "community_poll_assets", "instagram_poll")
CAROUSEL_DIR = os.path.join(POLL_DIR, "carousel_slides")
STORY_PATH = os.path.join(POLL_DIR, "instagram_story_poll_1080x1920.jpg")
CAPTION_FILE = os.path.join(POLL_DIR, "caption_instagram.txt")
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")

def get_client():
    cl = Client()
    cl.delay_range = [2, 5]
    if os.path.exists(SESSION_FILE):
        try:
            print("🔑 Loading existing Instagram session...")
            cl.load_settings(SESSION_FILE)
            cl.get_timeline_feed()
            print(f"✅ Session active! Logged in as: @{cl.username}")
            return cl
        except Exception as e:
            print(f"⚠️ Session expired or invalid: {e}")
    print("❌ Active session not found. Please run: python backend/scripts/upload_instagram_reel.py --login first.")
    sys.exit(1)

def upload_carousel(cl):
    if not os.path.exists(CAROUSEL_DIR):
        print(f"❌ Carousel slides folder not found: {CAROUSEL_DIR}")
        return False

    slide_files = [
        "poll_option_1_thirsty_crow.jpg",
        "poll_option_2_tortoise_hare.jpg",
        "poll_option_3_greedy_dog.jpg",
        "poll_option_4_friends_bear.jpg"
    ]
    paths = [os.path.join(CAROUSEL_DIR, f) for f in slide_files if os.path.exists(os.path.join(CAROUSEL_DIR, f))]
    
    if len(paths) < 2:
        print(f"❌ Need at least 2 slides for carousel. Found: {len(paths)}")
        return False

    caption = ""
    if os.path.exists(CAPTION_FILE):
        with open(CAPTION_FILE, "r", encoding="utf-8") as f:
            caption = f.read()

    print("\n" + "=" * 70)
    print("🚀 PUBLISHING 4-SLIDE CAROUSEL POLL TO INSTAGRAM FEED")
    print("=" * 70)
    for i, p in enumerate(paths, 1):
        print(f"   Slide {i}: {os.path.basename(p)}")
    print(f"   Caption Length: {len(caption)} characters")
    print("⏳ Uploading album to Instagram...")

    try:
        media = cl.album_upload(paths=paths, caption=caption)
        post_url = f"https://www.instagram.com/p/{media.code}/"
        print("=" * 70)
        print("🎉 CAROUSEL POLL PUBLISHED SUCCESSFULLY! 🚀")
        print(f"📍 Media ID : {media.id}")
        print(f"🔗 Post URL : {post_url}")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"❌ Failed to upload carousel: {e}")
        return False

def upload_story(cl):
    if not os.path.exists(STORY_PATH):
        print(f"❌ Story image not found: {STORY_PATH}")
        return False

    print("\n" + "=" * 70)
    print("🚀 PUBLISHING 9:16 POLL TEMPLATE TO INSTAGRAM STORIES")
    print("=" * 70)
    print(f"🖼️  Image: {STORY_PATH}")
    print("⏳ Uploading to Instagram Stories...")

    try:
        media = cl.photo_upload_to_story(path=STORY_PATH)
        print("=" * 70)
        print("🎉 STORY POLL TEMPLATE PUBLISHED SUCCESSFULLY! 🚀")
        print(f"📍 Story Media ID: {media.id}")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"❌ Failed to upload story: {e}")
        return False

SQUARE_PATH = os.path.join(POLL_DIR, "instagram_poll_1080x1080.jpg")

def upload_square(cl):
    if not os.path.exists(SQUARE_PATH):
        print(f"❌ Square 1:1 image not found: {SQUARE_PATH}")
        return False

    caption = ""
    if os.path.exists(CAPTION_FILE):
        with open(CAPTION_FILE, "r", encoding="utf-8") as f:
            caption = f.read()

    print("\n" + "=" * 70)
    print("🚀 PUBLISHING 1:1 SQUARE POLL GRAPHIC TO INSTAGRAM FEED")
    print("=" * 70)
    print(f"🖼️  Image: {SQUARE_PATH}")
    print(f"📝 Caption: {len(caption)} characters")
    print("⏳ Uploading photo to Instagram...")

    try:
        media = cl.photo_upload(path=SQUARE_PATH, caption=caption)
        post_url = f"https://www.instagram.com/p/{media.code}/"
        print("=" * 70)
        print("🎉 1:1 SQUARE POLL PUBLISHED SUCCESSFULLY! 🚀")
        print(f"📍 Media ID : {media.id}")
        print(f"🔗 Post URL : {post_url}")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"❌ Failed to upload square photo: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Instagram Poll Publisher")
    parser.add_argument("--type", choices=["square", "carousel", "story", "all"], default="square",
                        help="Upload format: 'square' (1:1 feed post), 'carousel' (4-slide album), 'story' (9:16 story), or 'all'")
    args = parser.parse_args()

    cl = get_client()

    if args.type == "square":
        upload_square(cl)
    elif args.type == "carousel":
        upload_carousel(cl)
    elif args.type == "story":
        upload_story(cl)
    elif args.type == "all":
        upload_square(cl)
        upload_story(cl)

if __name__ == "__main__":
    main()

