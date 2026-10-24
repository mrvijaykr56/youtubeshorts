"""
Festive Market & Viewer Preference Analyzer for Diwali & Chhath Puja
Analyzes YouTube Search API for top-performing animated stories:
1. View counts and velocity
2. Title formulas and emotional angles
3. Recurring story tropes (Magic diya, poor vs rich, mythological origins, family celebration)
4. Chhath Puja demand analysis
"""

import os
import sys
import json
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

def analyze_festive():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

    queries = [
        "Diwali Hindi Kahaniya",
        "Diwali cartoon Hindi story",
        "Chhath Puja cartoon Hindi Kahaniya",
        "Chhath Maiya ki Kahani 3D"
    ]

    for q in queries:
        print("=" * 80)
        print(f"🔍 ANALYZING TOP-PERFORMING MARKET DEMAND FOR: '{q}'")
        print("=" * 80)

        res = youtube.search().list(part='snippet', q=q, type='video', order='viewCount', maxResults=5).execute()
        items = res.get('items', [])
        if not items:
            print("No items found.")
            continue

        v_ids = [it['id']['videoId'] for it in items]
        v_details = youtube.videos().list(part='snippet,statistics,contentDetails', id=','.join(v_ids)).execute().get('items', [])

        for idx, v in enumerate(v_details, 1):
            snip = v['snippet']
            stats = v['statistics']
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            dur = v['contentDetails'].get('duration', 'N/A')
            tags = snip.get('tags', [])[:8]

            print(f"#{idx} | Title   : {snip['title']}")
            print(f"   Channel : {snip['channelTitle']}")
            print(f"   Views   : {views:,} | Likes: {likes:,} | Comments: {comments:,} | Dur: {dur}")
            print(f"   Tags    : {tags}")
            print()

if __name__ == "__main__":
    analyze_festive()
