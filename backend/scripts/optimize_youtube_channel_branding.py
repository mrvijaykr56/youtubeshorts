"""
Automated YouTube Channel SEO & Branding Optimizer for @MagicalTalesKidz
Updates:
1. Channel Title -> MagicalTales Kidz - 3D Hindi Kahaniya 🌟
2. Country -> IN (India)
3. Default Language -> hi (Hindi)
4. Comprehensive Channel Keyword Cluster (English & Devanagari)
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

def optimize_channel():
    print("=" * 70)
    print("🚀 OPTIMIZING YOUTUBE CHANNEL BRANDING & SEO: @MagicalTalesKidz")
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

    # Fetch current channel
    ch_res = youtube.channels().list(part='id,snippet,brandingSettings', mine=True).execute()
    if not ch_res.get('items'):
        print("❌ No channel found for current credentials.")
        return

    channel = ch_res['items'][0]
    ch_id = channel['id']
    old_branding = channel.get('brandingSettings', {})
    channel_branding = old_branding.get('channel', {})

    print(f"📡 Current Channel ID : {ch_id}")
    print(f"📛 Current Title      : {channel_branding.get('title')}")
    print(f"🌐 Current Language   : {channel_branding.get('defaultLanguage')}")
    print(f"📍 Current Country    : {channel_branding.get('country')}")

    # Build updated branding settings
    new_title = "MagicalTales Kidz - 3D Hindi Kahaniya 🌟"
    new_keywords = (
        '"Hindi Kahaniya" "Moral Stories in Hindi" "Panchatantra Stories" '
        '"Kids Stories in Hindi" "3D Animated Stories" "Hindi Cartoon" '
        '"Jadui Kahaniya" "Stories for kids" "Bal Kahaniya" "Bedtime Stories Hindi" '
        '"Hindi Fairy Tales" "MagicalTalesKidz" "हिंदी कहानियां" '
        '"पंचतंत्र की कहानियां" "बाल कहानियां" "नैतिक कहानियां" "3D कार्टून"'
    )

    channel_branding['title'] = new_title
    channel_branding['defaultLanguage'] = 'hi'
    channel_branding['country'] = 'IN'
    channel_branding['keywords'] = new_keywords

    update_body = {
        'id': ch_id,
        'brandingSettings': {
            'channel': channel_branding
        }
    }

    try:
        updated_res = youtube.channels().update(part='brandingSettings', body=update_body).execute()
        updated_ch = updated_res.get('brandingSettings', {}).get('channel', {})
        print("\n✅ SUCCESS: Channel Branding & SEO Successfully Updated!")
        print(f"  • Title            : {updated_ch.get('title')}")
        print(f"  • Default Language : {updated_ch.get('defaultLanguage')}")
        print(f"  • Country          : {updated_ch.get('country')}")
        print(f"  • Keywords Count   : {len(updated_ch.get('keywords', '').split())} tags indexed")
    except Exception as e:
        print(f"\n⚠️ Update note: {e}")
        # Try fallback without country if country is restricted via API
        try:
            print("Trying fallback without country field...")
            channel_branding.pop('country', None)
            update_body['brandingSettings']['channel'] = channel_branding
            fallback_res = youtube.channels().update(part='brandingSettings', body=update_body).execute()
            updated_ch = fallback_res.get('brandingSettings', {}).get('channel', {})
            print("✅ SUCCESS via Fallback:")
            print(f"  • Title            : {updated_ch.get('title')}")
            print(f"  • Default Language : {updated_ch.get('defaultLanguage')}")
        except Exception as fe:
            print(f"❌ Fallback failed: {fe}")

    print("=" * 70)

if __name__ == "__main__":
    optimize_channel()
