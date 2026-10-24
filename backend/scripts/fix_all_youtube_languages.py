"""
Fix all YouTube Videos Default Language and Audio Language to Hindi (hi)
Ensures YouTube routes all Shorts strictly to Hindi-speaking audiences and uses
Hindi speech-to-text acoustic models for automatic captioning and search indexing.
"""

import os
import sys
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

def fix_all_languages():
    print("=" * 70)
    print("🚀 FIXING YOUTUBE VIDEO LANGUAGES & AUDIO ROUTING TO HINDI (hi)")
    print("=" * 70)

    if not os.path.exists(TOKEN_PATH):
        print(f"❌ Token file not found at {TOKEN_PATH}")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

    # 1. Fetch all video IDs from Uploads playlist
    ch_res = youtube.channels().list(part='contentDetails', mine=True).execute()
    uploads_id = ch_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    playlist_items = []
    next_page = None
    while True:
        pl_res = youtube.playlistItems().list(part='contentDetails', playlistId=uploads_id, maxResults=50, pageToken=next_page).execute()
        playlist_items.extend(pl_res.get('items', []))
        next_page = pl_res.get('nextPageToken')
        if not next_page:
            break

    video_ids = [item['contentDetails']['videoId'] for item in playlist_items]
    print(f"📡 Found {len(video_ids)} total videos to audit and fix.\n")

    updated_count = 0
    for vid in video_ids:
        # Fetch current snippet
        v_res = youtube.videos().list(part='snippet', id=vid).execute()
        items = v_res.get('items', [])
        if not items:
            continue

        item = items[0]
        snippet = item['snippet']
        title = snippet.get('title', '')
        cur_def_lang = snippet.get('defaultLanguage')
        cur_audio_lang = snippet.get('defaultAudioLanguage')

        # Check if already hi and hi
        if cur_def_lang == 'hi' and cur_audio_lang == 'hi':
            print(f"⏩ [Video {vid}] Already Hindi (hi / hi): {title[:40]}... Skipping.")
            continue

        print(f"⚡ Fixing [Video {vid}] - Title: {title[:40]}...")
        print(f"   Before: defaultLang='{cur_def_lang}', audioLang='{cur_audio_lang}'")

        snippet['defaultLanguage'] = 'hi'
        snippet['defaultAudioLanguage'] = 'hi'

        body = {
            'id': vid,
            'snippet': snippet
        }

        try:
            youtube.videos().update(part='snippet', body=body).execute()
            print(f"   ✅ Successfully updated to: defaultLang='hi', audioLang='hi'!")
            updated_count += 1
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ Error updating video {vid}: {e}")

    print("\n" + "=" * 70)
    print(f"🎉 COMPLETE: {updated_count} videos corrected to pure Hindi (hi / hi)!")
    print("=" * 70)

if __name__ == "__main__":
    fix_all_languages()
