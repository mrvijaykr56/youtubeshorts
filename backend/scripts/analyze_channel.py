import sys
import os
import json
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
creds = Credentials.from_authorized_user_file(token_path)
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

# 1. Channel Details
ch_res = youtube.channels().list(part='snippet,statistics,contentDetails', mine=True).execute()
channel = ch_res['items'][0]
stats = channel['statistics']
snippet = channel['snippet']

print("=================================================================")
print("📊 YOUTUBE CHANNEL AUDIT & ANALYTICS: @MagicalTalesKidz")
print("=================================================================")
print(f"Title            : {snippet.get('title')}")
print(f"Custom URL       : {snippet.get('customUrl', 'N/A')}")
print(f"Subscribers      : {stats.get('subscriberCount')}")
print(f"Total Views      : {stats.get('viewCount')}")
print(f"Total Videos     : {stats.get('videoCount')}")
print(f"Hidden Subs      : {stats.get('hiddenSubscriberCount', False)}")
print("=================================================================")

# 2. Uploads Playlist
uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']

playlist_items = []
next_page = None
while True:
    pl_res = youtube.playlistItems().list(part='snippet,contentDetails', playlistId=uploads_id, maxResults=50, pageToken=next_page).execute()
    playlist_items.extend(pl_res.get('items', []))
    next_page = pl_res.get('nextPageToken')
    if not next_page:
        break

video_ids = [item['contentDetails']['videoId'] for item in playlist_items]

# 3. Video Statistics in batch
video_data = []
for i in range(0, len(video_ids), 50):
    batch_ids = video_ids[i:i+50]
    v_res = youtube.videos().list(part='snippet,statistics,status', id=','.join(batch_ids)).execute()
    for v in v_res.get('items', []):
        v_stat = v.get('statistics', {})
        v_snip = v.get('snippet', {})
        v_status = v.get('status', {})
        video_data.append({
            'id': v['id'],
            'title': v_snip.get('title'),
            'publishedAt': v_snip.get('publishedAt'),
            'views': int(v_stat.get('viewCount', 0)),
            'likes': int(v_stat.get('likeCount', 0)),
            'comments': int(v_stat.get('commentCount', 0)),
            'privacy': v_status.get('privacyStatus'),
            'madeForKids': v_status.get('madeForKids')
        })

# Sort by publishedAt descending
video_data.sort(key=lambda x: x['publishedAt'], reverse=True)

print("\n📹 ALL VIDEO PERFORMANCE METRICS (Newest to Oldest):")
print("-" * 105)
print(f"{'#':<3} | {'Video ID':<12} | {'Published':<20} | {'Views':<6} | {'Likes':<5} | {'Comments':<8} | {'Title'}")
print("-" * 105)
for idx, v in enumerate(video_data, 1):
    pub = v['publishedAt'][:19].replace('T', ' ')
    print(f"{idx:<3} | {v['id']:<12} | {pub:<20} | {v['views']:<6} | {v['likes']:<5} | {v['comments']:<8} | {v['title'][:45]}")
print("-" * 105)

# Breakdown by era
old_era = [v for v in video_data if "2026-06" in v['publishedAt']]
new_era = [v for v in video_data if "2026-10" in v['publishedAt']]

print(f"\n📈 COLD-START RECOVERY PROGRESSION:")
print(f"  • Legacy Videos (June 2026): {len(old_era)} videos, {sum(v['views'] for v in old_era)} views total")
print(f"  • New 3D Panchatantra Era (Oct 2026): {len(new_era)} videos, {sum(v['views'] for v in new_era)} views total")
print(f"  • Engagement (Likes + Comments): {sum(v['likes'] + v['comments'] for v in new_era)} interactions on new shorts")
