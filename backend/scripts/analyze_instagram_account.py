"""
Instagram Channel & Reel Analytics Script for @magicaltaleskid
Inspects profile health, bio, recent uploads, views, likes, and caption SEO.
"""

import os
import sys
import json
from datetime import datetime
from instagrapi import Client

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")

def analyze_account():
    print("=" * 70)
    print("🔍 ANALYZING INSTAGRAM CHANNEL: @magicaltaleskid")
    print("=" * 70)

    if not os.path.exists(SESSION_FILE):
        print("❌ Session file not found. Run login first.")
        return

    cl = Client()
    cl.load_settings(SESSION_FILE)
    cl.username = "magicaltaleskid"

    user_id = cl.user_id_from_username(cl.username)
    user_info = cl.user_info(user_id)

    print(f"👤 Username       : @{user_info.username}")
    print(f"📛 Full Name      : {user_info.full_name or 'Not set'}")
    print(f"👥 Followers      : {user_info.follower_count}")
    print(f"👣 Following      : {user_info.following_count}")
    print(f"🎬 Total Posts    : {user_info.media_count}")
    print(f"🌐 Bio Link (URL) : {user_info.external_url or 'None'}")
    print(f"📝 Bio Description:\n{user_info.biography or '[Empty Bio]'}\n")

    print("-" * 70)
    print("📹 RECENT REELS & POSTS ANALYSIS (Uploaded Recently):")
    print("-" * 70)

    # Fetch recent medias
    medias = cl.user_medias(user_id, amount=20)

    if not medias:
        print("No posts or reels found on this account yet.")
        return

    for i, m in enumerate(medias, 1):
        media_type = "Reel 🎬" if m.media_type == 2 and m.product_type == "clips" else f"Type {m.media_type}"
        taken_at = m.taken_at.strftime('%Y-%m-%d %H:%M:%S') if m.taken_at else "Unknown"
        views = getattr(m, 'view_count', None) or getattr(m, 'play_count', None) or 0
        likes = m.like_count or 0
        comments = m.comment_count or 0
        caption = m.caption_text or ""
        first_line = caption.split('\n')[0][:80] if caption else "[No Caption]"
        reel_url = f"https://www.instagram.com/reel/{m.code}/" if m.product_type == "clips" else f"https://www.instagram.com/p/{m.code}/"

        print(f"{i}. [{media_type}] Code: {m.code} | Date: {taken_at}")
        print(f"   🔗 Link     : {reel_url}")
        print(f"   👀 Plays    : {views} | ❤️ Likes: {likes} | 💬 Comments: {comments}")
        print(f"   ✍️ Caption  : {first_line}...")
        
        # Extract hashtags
        hashtags = [w for w in caption.split() if w.startswith('#')]
        if hashtags:
            print(f"   🏷️  Tags ({len(hashtags)}): {' '.join(hashtags[:8])}{'...' if len(hashtags) > 8 else ''}")
        print()

    print("=" * 70)
    print("💡 COMPLETED AUDIT")
    print("=" * 70)

if __name__ == "__main__":
    analyze_account()
