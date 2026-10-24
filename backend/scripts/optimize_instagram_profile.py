"""
Optimize Instagram Profile Bio and Clickable External Link for @magicaltaleskid
"""

import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from instagrapi import Client

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")

def optimize_profile():
    print("=" * 70)
    print("✨ OPTIMIZING INSTAGRAM PROFILE SEO: @magicaltaleskid")
    print("=" * 70)

    cl = Client()
    cl.load_settings(SESSION_FILE)
    cl.username = "magicaltaleskid"

    new_full_name = "Magical Tales | Hindi Kahaniya"
    new_bio = (
        "✨ 3D जादुई कहानियां & पंचतंत्र सीख 🌟\n"
        "👶 बच्चों के लिए सुरक्षित & ज्ञानवर्धक मनोरंजन\n"
        "🎬 नए 3D एपिसोड्स YouTube पर देखें 👇"
    )
    yt_url = "https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"

    try:
        # Edit full name, biography and website
        cl.account_edit(
            full_name=new_full_name,
            biography=new_bio,
            external_url=yt_url
        )
        print("✅ Successfully updated Display Name, Bio & Clickable External Link to YouTube!")
    except Exception as e:
        print(f"⚠️ Account edit note: {e}")
        try:
            # Fallback direct bio update
            cl.set_biography(new_bio)
            print("✅ Set new high-conversion Bio text!")
        except Exception as be:
            print(f"Bio fallback note: {be}")

if __name__ == "__main__":
    optimize_profile()
