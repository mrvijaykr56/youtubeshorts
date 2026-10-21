"""
YouTube Channel Automation & Management Script
- Creates and organizes channel playlists
- Adds all 6 uploaded Shorts to the official playlist
- Toggles video privacy to Public
"""

import os
import sys
import json
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token_file = os.path.join(backend_dir, "token.json")

scopes = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

VIDEOS_TO_ORGANIZE = [
    {"job_key": "miku_laddoo", "video_id": "cuaCG-6B-1M", "title": "Miku & The Golden Laddoo"},
    {"job_key": "diwali_elephant", "video_id": "mR2eWSWiZoE", "title": "Golu Elephant Diwali Light"},
    {"job_key": "diwali_lion", "video_id": "OQGNGYqde3c", "title": "Sheru Lion & Deepawali Diya"},
    {"job_key": "squirrel_star", "video_id": "OHny_kUkjAw", "title": "Cheeku Squirrel & The Magic Star"},
    {"job_key": "crow_mango", "video_id": "JNMuCm6b8xg", "title": "Kalu Crow & The Sweetest Mango"},
    {"job_key": "peacock_feathers", "video_id": "cN6k6lu0-Mc", "title": "Neel Peacock & The Rainbow Feather"}
]

PLAYLIST_TITLE = "Magical Tales Hindi Shorts | हिंदी बाल कहानियाँ (3D Animation)"
PLAYLIST_DESCRIPTION = "सुंदर और प्रेरणादायक 3D हिंदी बाल कहानियाँ और पंचतंत्र कथाएँ। Best 3D Animated Hindi Moral Stories for Kids on @MagicalTalesKidz."

def get_authenticated_service():
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"Missing token.json at {token_file}")

    credentials = Credentials.from_authorized_user_file(token_file, scopes)
    if credentials.expired and credentials.refresh_token:
        print("[auth] Refreshing expired credentials...", flush=True)
        credentials.refresh(Request())
        with open(token_file, "w") as f:
            f.write(credentials.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def get_or_create_playlist(youtube):
    print(f"\n📂 Checking existing playlists...", flush=True)
    res = youtube.playlists().list(part="snippet,status", mine=True, maxResults=50).execute()
    existing_playlists = res.get("items", [])

    for pl in existing_playlists:
        if pl["snippet"]["title"].strip() == PLAYLIST_TITLE.strip():
            print(f"✅ Found existing playlist: '{PLAYLIST_TITLE}' (ID: {pl['id']})", flush=True)
            return pl["id"]

    print(f"Creating new playlist: '{PLAYLIST_TITLE}'...", flush=True)
    new_pl = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": PLAYLIST_TITLE,
                "description": PLAYLIST_DESCRIPTION
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    ).execute()
    pl_id = new_pl["id"]
    print(f"🎉 Created playlist successfully! ID: {pl_id}", flush=True)
    return pl_id

def get_playlist_video_ids(youtube, playlist_id):
    import time
    video_ids = set()
    next_page_token = None
    try:
        while True:
            res = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            for item in res.get("items", []):
                video_ids.add(item["contentDetails"]["videoId"])
            next_page_token = res.get("nextPageToken")
            if not next_page_token:
                break
    except Exception as e:
        print(f"   [info] Playlist items lookup note: {e} (treating as newly created empty playlist).", flush=True)
    return video_ids

def add_videos_to_playlist(youtube, playlist_id):
    import time
    existing_ids = get_playlist_video_ids(youtube, playlist_id)
    print(f"Currently {len(existing_ids)} videos verified in playlist.", flush=True)

    for item in VIDEOS_TO_ORGANIZE:
        vid = item["video_id"]
        title = item["title"]
        if vid in existing_ids:
            print(f"   ⏩ Video '{title}' ({vid}) already in playlist.", flush=True)
            continue

        added = False
        for attempt in range(1, 4):
            try:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": vid
                            }
                        }
                    }
                ).execute()
                print(f"   ✅ Added '{title}' ({vid}) to playlist!", flush=True)
                added = True
                break
            except Exception as e:
                if attempt < 3:
                    print(f"   [retry {attempt}/3] Adding '{title}' ({vid}): {e}, waiting 2s...", flush=True)
                    time.sleep(2)
                else:
                    print(f"   ❌ Error adding '{title}' ({vid}) after 3 attempts: {e}", flush=True)

def update_privacy_to_public(youtube):
    print(f"\n🌍 Updating privacy status to PUBLIC for all 6 Shorts...", flush=True)
    results = []
    for item in VIDEOS_TO_ORGANIZE:
        vid = item["video_id"]
        title = item["title"]
        try:
            # First fetch current snippet and status to preserve metadata
            video_res = youtube.videos().list(part="status,snippet", id=vid).execute()
            items = video_res.get("items", [])
            if not items:
                print(f"   ⚠️ Video {vid} not found on channel.", flush=True)
                continue

            current_video = items[0]
            current_status = current_video.get("status", {})
            current_snippet = current_video.get("snippet", {})
            current_privacy = current_status.get("privacyStatus", "unknown")

            if current_privacy == "public":
                print(f"   ⏩ '{title}' ({vid}) is already PUBLIC.", flush=True)
                results.append({"video_id": vid, "title": title, "status": "public", "changed": False})
                continue

            # Update privacy to public
            current_status["privacyStatus"] = "public"
            update_body = {
                "id": vid,
                "status": current_status
            }
            # Note: youtube.videos().update requires categoryId if snippet is modified; updating status only requires status
            youtube.videos().update(
                part="status",
                body=update_body
            ).execute()

            print(f"   ✅ '{title}' ({vid}) privacy changed: {current_privacy.upper()} ➡️ PUBLIC!", flush=True)
            results.append({"video_id": vid, "title": title, "status": "public", "changed": True})
        except Exception as e:
            print(f"   ❌ Failed to update '{title}' ({vid}): {e}", flush=True)
            results.append({"video_id": vid, "title": title, "status": "error", "error": str(e)})

    return results

def main():
    print("=" * 65, flush=True)
    print("🚀 YouTube Channel Automation: Playlist & Privacy Manager", flush=True)
    print("=" * 65, flush=True)

    youtube = get_authenticated_service()

    # Step 1: Playlist
    playlist_id = get_or_create_playlist(youtube)
    add_videos_to_playlist(youtube, playlist_id)

    # Step 2: Privacy Status
    privacy_results = update_privacy_to_public(youtube)

    print("\n" + "=" * 65, flush=True)
    print("🎉 ALL TASKS COMPLETE!", flush=True)
    print(f"Playlist URL: https://www.youtube.com/playlist?list={playlist_id}", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
