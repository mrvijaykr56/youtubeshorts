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

competitors = ['Koo Koo TV Hindi', 'Infobells Hindi', 'PunToon Kids']

for comp in competitors:
    print('=' * 75)
    print(f"🔍 ANALYZING TOP COMPETITOR: {comp}")
    print('=' * 75)
    res = youtube.search().list(part='snippet', q=comp, type='channel', maxResults=1).execute()
    if not res.get('items'):
        print('No channel found')
        continue
    ch_item = res['items'][0]
    ch_id = ch_item['snippet']['channelId']
    ch_title = ch_item['snippet']['title']

    # Get Channel details
    ch_det = youtube.channels().list(part='snippet,brandingSettings,statistics,contentDetails', id=ch_id).execute()['items'][0]
    ch_stats = ch_det['statistics']
    ch_b = ch_det.get('brandingSettings', {}).get('channel', {})
    
    subs = ch_stats.get('subscriberCount', 'N/A')
    total_views = ch_stats.get('viewCount', 'N/A')
    keywords = ch_b.get('keywords', 'N/A')

    print(f"Title            : {ch_title}")
    print(f"Channel ID       : {ch_id}")
    print(f"Subscribers      : {subs}")
    print(f"Total Views      : {total_views}")
    print(f"Channel Keywords : {keywords}")

    # Get uploads
    uploads_id = ch_det['contentDetails']['relatedPlaylists']['uploads']
    v_res = youtube.playlistItems().list(part='snippet,contentDetails', playlistId=uploads_id, maxResults=4).execute()
    v_ids = [it['contentDetails']['videoId'] for it in v_res['items']]
    
    videos = youtube.videos().list(part='snippet,statistics', id=','.join(v_ids)).execute().get('items', [])
    print('\n📹 Top / Recent Video SEO Patterns:')
    for v in videos:
        v_title = v['snippet']['title']
        v_tags = v['snippet'].get('tags', [])
        v_views = v['statistics'].get('viewCount', '0')
        v_desc = v['snippet']['description'][:160].replace('\n', ' ')
        print(f"  • Video: {v_title}")
        print(f"    Views: {v_views} | Tags Count: {len(v_tags)}")
        print(f"    Tags : {v_tags[:12]}")
        print(f"    Desc : {v_desc}...\n")
