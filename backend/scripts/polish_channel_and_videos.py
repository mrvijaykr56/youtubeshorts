"""
Channel Polish & SEO Optimization Script
- Upgrades Channel Description & Search Keywords via YouTube Data API
- Enriches Descriptions & Tags for all 6 active Shorts with Playlist links and CTA
- Posts top engagement comment on each Short to maximize algorithmic comment velocity
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

CHANNEL_ID = "UCL3Xsads7oyNr70erqz8vPQ"
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLJE6ifX-QD0A"
SUBSCRIBE_URL = "https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1"

CHANNEL_DESCRIPTION = """✨ Welcome to MagicalTales Kidz (@MagicalTalesKidz) – The Home of 3D Pixar-Style Animated Hindi Moral Stories! 🌟

यहाँ आपको मिलेंगी पंचतंत्र और भारतीय लोककथाओं पर आधारित सुंदर, जादुई और ज्ञानवर्धक 3D एनिमेशन कहानियाँ। हर कहानी में बच्चों के लिए एक अनमोल सीख (Moral) छिपी है।

🎯 What we bring for you:
🌟 3D Pixar Animation Hindi Stories
📚 Panchatantra & Jataka Tales (पंचतंत्र की कहानियाँ)
💖 Moral Values & Kindness for Kids (नैतिक शिक्षा)
🎉 Daily New Shorts & Fun Adventures!

🔔 Subscribe to @MagicalTalesKidz today and join our magical story world!
Watch our complete playlist: https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

#HindiKahaniya #MoralStories #Panchatantra #KidsAnimation #3DAnimation #MagicalTales #HindiStories"""

CHANNEL_KEYWORDS = '"Hindi Kahaniya" "Moral Stories in Hindi" "Panchatantra Stories" "Kids Moral Stories" "Panchatantra Tales in Hindi" "3D Cartoon Stories" "Bal Kahaniya" "Magical Tales" "Hindi Fairy Tales" "Bedtime Stories in Hindi" "Hindi Animation" "MagicalTales Kidz" "Kids Stories"'

VIDEOS = [
    {
        "id": "cuaCG-6B-1M",
        "title": "Miku Monkey & The Golden Laddoo 🐒✨ | 3D Hindi Kahaniya",
        "story_moral": "सच्ची खुशी अकेले खाने में नहीं, बल्कि दोस्तों के साथ बांटने में है। (Sharing brings true joy!)",
        "comment": "✨ क्या मीकू ने लड्डू बांटकर सही काम किया? कमेंट में बताएं और ऐसी और जादुई कहानियों के लिए @MagicalTalesKidz को Subscribe करें! ❤️🔔"
    },
    {
        "id": "mR2eWSWiZoE",
        "title": "Golu Elephant & The Diwali Light 🐘🪔 | 3D Hindi Moral Stories",
        "story_moral": "मुस्कान और एकता ही सबसे बड़ा प्रकाश है। (Togetherness and kindness light up every heart!)",
        "comment": "🪔 गोलू हाथी की यह दिवाली कहानी आपको कैसी लगी? अपने विचार कमेंट्स में लिखें और चैनल को Subscribe करें! 🌟🐘"
    },
    {
        "id": "OQGNGYqde3c",
        "title": "Sheru Lion & The Deepawali Diya 🦁✨ | Hindi Animated Kahani",
        "story_moral": "सच्चा राजा ताकत से नहीं, प्रेम और देखभाल से बनता है। (A true leader protects with love, not roar!)",
        "comment": "🦁 जंगल के राजा शेरू की सीख आपको कैसी लगी? अपनी राय कमेंट में बताएं और नए एपिसोड्स के लिए Subscribe करें! 👑🔥"
    },
    {
        "id": "OHny_kUkjAw",
        "title": "Cheeku Squirrel & The Magic Star 🐿️⭐ | Hindi Kids Story",
        "story_moral": "रोशनी अपने पास रखने से नहीं, अंधेरे में दूसरों का रास्ता दिखाने से चमकती है। (True stars shine by helping others!)",
        "comment": "⭐ चीकू गिलहरी का जादू आपको कैसा लगा? कमेंट करें और रोज़ाना नई 3D कहानियों के लिए Subscribe करें! 🐿️💖"
    },
    {
        "id": "JNMuCm6b8xg",
        "title": "Kalu Crow & The Sweetest Mango 🐦🥭 | 3D Panchatantra Kahaniya",
        "story_moral": "गुस्से में चिल्लाने से नहीं, मिलकर बांटने से ही मिठास मिलती है। (Kindness turns enemies into friends!)",
        "comment": "🥭 कालू कौवे और मीकू की दोस्ती कैसी लगी? कमेंट में बताएं और ऐसी प्रेरणादायक कहानियों के लिए Subscribe करें! 🐦✨"
    },
    {
        "id": "cN6k6lu0-Mc",
        "title": "Neel Peacock & The Rainbow Feather 🦚🌈 | 3D Moral Tales",
        "story_moral": "सच्ची सुंदरता पंखों के रंग में नहीं, दूसरों की मदद करने वाले दिल में है। (Inner kindness is true beauty!)",
        "comment": "🦚 नील मोर के इंद्रधनुषी पंख आपको कैसे लगे? कमेंट बॉक्स में जरूर बताएं और चैनल को Subscribe करें! 🌈✨"
    }
]

def get_service():
    creds = Credentials.from_authorized_user_file(token_file, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

BANNER_URL = "https://yt3.googleusercontent.com/d_xTqrkeqE8fn3U1shB6GT5U5G0ezDMFuqHlqg0dRVqXNSPkzlPDmlQ5lLVQ_zc8kLZcZf9-"

def update_channel_branding(yt):
    print("🌟 Step 1: Upgrading Channel Description, Banner & Keywords...", flush=True)
    body = {
        "id": CHANNEL_ID,
        "brandingSettings": {
            "channel": {
                "title": "MagicalTales",
                "description": CHANNEL_DESCRIPTION,
                "keywords": CHANNEL_KEYWORDS
            },
            "image": {
                "bannerExternalUrl": BANNER_URL
            }
        }
    }
    res = yt.channels().update(part="brandingSettings", body=body).execute()
    print("   ✅ Channel description, banner & keywords updated successfully!", flush=True)

def update_videos_seo(yt):
    print("\n🚀 Step 2: Enriching Video SEO & High-Retention Descriptions...", flush=True)
    for v in VIDEOS:
        vid = v["id"]
        v_title = v["title"]
        try:
            # Get existing video details
            res = yt.videos().list(part="snippet,status", id=vid).execute()
            items = res.get("items", [])
            if not items:
                continue
            snippet = items[0]["snippet"]
            
            # Construct rich SEO description
            rich_desc = f"""{snippet.get('description', '')}

🌟 कहानी की सीख (Moral of the Story):
{v['story_moral']}

🎬 Watch All 3D Hindi Stories in Official Playlist:
{PLAYLIST_URL}

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
{SUBSCRIBE_URL}

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation #3DAnimation #MagicalTales #HindiStories #BalKahani"""

            snippet["description"] = rich_desc.strip()
            snippet["tags"] = [
                "hindi kahaniya", "moral stories", "panchatantra stories", "kids animation",
                "3d animated stories", "hindi cartoon", "magical tales", "shorts", "ytshorts",
                "bal kahaniya", "bedtime stories in hindi", "hindi moral stories"
            ]

            yt.videos().update(
                part="snippet",
                body={
                    "id": vid,
                    "snippet": snippet
                }
            ).execute()
            print(f"   ✅ Updated SEO & tags for: {v_title[:40]}... ({vid})", flush=True)
        except Exception as e:
            print(f"   ❌ Error updating {vid}: {e}", flush=True)

def post_engagement_comments(yt):
    print("\n💬 Step 3: Posting High-Engagement Questions on all 6 Shorts...", flush=True)
    for v in VIDEOS:
        vid = v["id"]
        comment_text = v["comment"]
        try:
            body = {
                "snippet": {
                    "videoId": vid,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            yt.commentThreads().insert(part="snippet", body=body).execute()
            print(f"   ✅ Posted engagement comment on {vid}", flush=True)
        except Exception as e:
            print(f"   [note] Comment on {vid}: {e}", flush=True)

def main():
    print("=" * 65, flush=True)
    print("🚀 Channel & Video Polish Engine for @MagicalTalesKidz", flush=True)
    print("=" * 65, flush=True)
    yt = get_service()
    update_channel_branding(yt)
    update_videos_seo(yt)
    post_engagement_comments(yt)
    print("\n" + "=" * 65, flush=True)
    print("🎉 CHANNEL & VIDEO POLISH COMPLETED!", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
