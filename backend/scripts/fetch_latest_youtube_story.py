"""
Fetch the most recently published video directly from the YouTube channel
using the YouTube Data API v3 and token.json credentials.
Works completely independently of uploads_tracker.json.
"""

import sys
import os
import json
from datetime import datetime

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token_file = os.path.join(backend_dir, "token.json")

def get_latest_youtube_video(limit=5):
    if not os.path.exists(token_file):
        print(f"[error] token.json not found at {token_file}")
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import googleapiclient.discovery

        scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

        creds = Credentials.from_authorized_user_file(token_file, scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, "w") as f:
                f.write(creds.to_json())

        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        # 1. Fetch channel's uploads playlist
        ch_res = youtube.channels().list(mine=True, part="snippet,contentDetails").execute()
        if not ch_res.get("items"):
            print("[error] No channel found for authenticated account.")
            return None

        channel = ch_res["items"][0]
        channel_title = channel["snippet"].get("title", "")
        custom_url = channel["snippet"].get("customUrl", "")
        uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

        # 2. Fetch the most recent items from the uploads playlist
        pl_res = youtube.playlistItems().list(
            playlistId=uploads_id,
            part="snippet,contentDetails",
            maxResults=limit
        ).execute()

        items = pl_res.get("items", [])
        if not items:
            print("[info] No videos found in uploads playlist.")
            return None

        # 3. Fetch detailed stats & tags for these items
        video_ids = [it["contentDetails"]["videoId"] for it in items]
        v_res = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics,status"
        ).execute()

        videos = []
        for v in v_res.get("items", []):
            snip = v.get("snippet", {})
            stat = v.get("statistics", {})
            stat_status = v.get("status", {})
            videos.append({
                "video_id": v["id"],
                "url": f"https://www.youtube.com/shorts/{v['id']}",
                "title": snip.get("title"),
                "description": snip.get("description", "")[:200] + "...",
                "tags": snip.get("tags", [])[:5],
                "published_at": snip.get("publishedAt"),
                "privacy_status": stat_status.get("privacyStatus"),
                "views": int(stat.get("viewCount", 0)),
                "likes": int(stat.get("likeCount", 0)),
                "comments": int(stat.get("commentCount", 0))
            })

        # Sort by publishedAt descending
        videos.sort(key=lambda x: x["published_at"], reverse=True)

        return {
            "channel_title": channel_title,
            "custom_url": custom_url,
            "latest_video": videos[0] if videos else None,
            "recent_videos": videos
        }

    except Exception as e:
        print(f"[error] Failed to fetch latest YouTube video: {e}")
        return None

if __name__ == "__main__":
    data = get_latest_youtube_video(limit=5)
    if data and data.get("latest_video"):
        lv = data["latest_video"]
        print("\n" + "="*70)
        print(f"🎬 LATEST VIDEO PUBLISHED ON YOUTUBE ({data.get('channel_title')} / {data.get('custom_url')})")
        print("="*70)
        print(f"📌 Title        : {lv['title']}")
        print(f"🔗 Video ID     : {lv['video_id']}")
        print(f"🌐 URL          : {lv['url']}")
        print(f"📅 Published At : {lv['published_at']}")
        print(f"🔒 Privacy      : {lv['privacy_status']}")
        print(f"👁️ Views        : {lv['views']}")
        print(f"👍 Likes        : {lv['likes']}")
        print(f"💬 Comments     : {lv['comments']}")
        print("="*70)
        print("\n📜 Top 5 Most Recent Uploads on Channel:")
        for idx, vid in enumerate(data.get("recent_videos", []), 1):
            print(f"{idx}. [{vid['published_at'][:10]}] {vid['title']} ({vid['url']})")
        print("="*70)
