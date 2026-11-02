# -*- coding: utf-8 -*-
"""
SEO Optimizer — MagicalTalesKidz
Batch-updates metadata (title, description, tags, language) for all YouTube videos
and scores each video's SEO health against target keyword clusters.

Usage:
  python backend/scripts/seo_optimizer.py --audit          # Score all videos
  python backend/scripts/seo_optimizer.py --update KEY     # Update single story's metadata
  python backend/scripts/seo_optimizer.py --update-all     # Batch update all videos
  python backend/scripts/seo_optimizer.py --report         # Print full SEO report
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ──────────────────────────────────────────────────────────────────────────────
# SEO CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

CHANNEL_HANDLE = "@MagicalTalesKidz"
CHANNEL_ID = "UCL3Xsads7oyNr70erqz8vPQ"
PLAYLIST_ID = "PLJE6ifX-QD0A"

# Core keyword clusters (Primary → Secondary → Long-tail)
KEYWORD_CLUSTERS = {
    "primary": [
        "Hindi Kahaniya", "Moral Stories", "3D Animation Hindi",
        "Panchatantra Stories", "Bal Kahaniya", "Kids Stories Hindi"
    ],
    "secondary": [
        "Hindi Cartoon", "3D Hindi Stories", "Kids Animation",
        "Moral Stories for Kids", "बाल कहानियां", "पंचतंत्र"
    ],
    "longtail": [
        "3D Hindi Kahaniya for kids", "Panchatantra stories in Hindi 2024",
        "Moral stories Hindi animation", "बच्चों की कहानियां 3D",
        "Hindi stories for children", "3D animated Hindi stories"
    ],
    "trending_hindi": [
        "MagicalTalesKidz", "Hindi shorts", "yt shorts Hindi",
        "viral Hindi shorts", "Hindi kids content"
    ]
}

# Optimal description template
DESCRIPTION_FOOTER = """
🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list={playlist_id}

💖 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

📱 Follow us on Instagram: https://www.instagram.com/magicaltaleskid/

#HindiStories #BalKahaniya #PanchatantraStories #HindiMoralStories #KidsAnimation #YtShorts #3DAnimation #MagicalTalesKidz #HindiKahaniya #MoralStories #ViralShorts #shorts
""".format(playlist_id=PLAYLIST_ID)

# Per-video metadata upgrades
VIDEO_SEO_UPGRADES = {
    "thirsty_crow": {
        "title": "प्यासे कौए की होशियारी: पानी कैसे मिला? 🐦💧 The Thirsty Crow | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #ThirstyCrow #MoralStories #3DAnimation\n\nप्यासे कौए ने अपनी चतुराई से पानी पाया! 🐦💧 यह 3D पंचतंत्र कहानी सिखाती है — हार मत मानो, उपाय ढूंढो! 💪✨\n\n🎯 कहानी का सार: कठिन समय में धैर्य और बुद्धि से काम लो!" + DESCRIPTION_FOOTER,
        "tags": ["प्यासा कौआ", "Thirsty Crow Story Hindi", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "Bal Kahaniya", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "पंचतंत्र की कहानियां", "Kids Animation Hindi", "Chintu Monkey", "Never Give Up Story"]
    },
    "magic_pot": {
        "title": "जादुई हांडी: गरीब किसान की किस्मत बदली! 🪄✨ The Magic Pot | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #MagicPot #MoralStories #3DAnimation\n\nएक गरीब किसान को मिली जादुई हांडी — पर क्या लालच ने सब बर्बाद किया? 🪄✨ देखो इस शानदार 3D जादुई कहानी में!\n\n🎯 कहानी का सार: मेहनत और संतोष में ही सच्चा सुख है!" + DESCRIPTION_FOOTER,
        "tags": ["जादुई हांडी", "Magic Pot Story Hindi", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "Bal Kahaniya", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "Kids Animation Hindi", "Chintu Monkey", "Greedy Story Hindi"]
    },
    "magic_millstone": {
        "title": "जादुई चक्की: नमक ही नमक! समंदर नमकीन क्यों? 🌊 The Magic Millstone | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #MagicMillstone #MoralStories #3DAnimation\n\nजादुई चक्की ने बंद होना नहीं जाना — इसीलिए समंदर नमकीन है! 🌊✨ यह रोचक 3D कहानी बच्चों को हंसाएगी और सिखाएगी!\n\n🎯 कहानी का सार: लालच बुरी बला है — संतोष में ही खुशी है!" + DESCRIPTION_FOOTER,
        "tags": ["जादुई चक्की", "Magic Millstone Story", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "Kids Animation Hindi", "Why is Sea Salty Story", "Chintu Monkey"]
    },
    "diwali_magic_diya": {
        "title": "दिवाली की जादुई दिया: अँधेरे में रोशनी! 🪔✨ The Magic Diya | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #Diwali #HindiKahaniya #MagicDiya #MoralStories #3DAnimation\n\nदिवाली की रात एक जादुई दिया ने गरीब बच्चे की मदद की! 🪔✨ यह दिल छू लेने वाली 3D कहानी देखो!\n\n🎯 कहानी का सार: दयालुता का प्रकाश सदा जीतता है!" + DESCRIPTION_FOOTER,
        "tags": ["दिवाली कहानी", "Diwali Magic Diya Story", "Diwali Special Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Diwali Animation", "MagicalTalesKidz", "shorts", "yt shorts", "दीपावली कहानी", "Kids Animation Hindi", "Festival Stories Hindi", "Chintu Monkey"]
    },
    "chhath_puja_miracle": {
        "title": "छठ पूजा का चमत्कार: सूर्य देव का आशीर्वाद! 🌅 Chhath Puja 3D Special #Shorts",
        "description": "#Shorts #ChhathPuja #HindiKahaniya #SunGod #MoralStories #3DAnimation\n\nछठ पूजा की रात एक बच्ची की सच्ची आस्था ने चमत्कार किया! 🌅🙏 यह भावनात्मक 3D कहानी ज़रूर देखो!\n\n🎯 कहानी का सार: सच्ची श्रद्धा और माँ का प्यार — दुनिया की सबसे बड़ी शक्ति!" + DESCRIPTION_FOOTER,
        "tags": ["छठ पूजा कहानी", "Chhath Puja Special Hindi", "Chhath Puja Story", "3D Hindi Kahaniya", "Moral Stories for Kids", "Festival Stories", "MagicalTalesKidz", "shorts", "yt shorts", "छठ पूजा", "Kids Animation Hindi", "Sun God Story Hindi"]
    },
    "hunter_and_pigeons": {
        "title": "शिकारी और कबूतर: एकता में बल है! 🕊️💪 Unity is Strength | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #HunterAndPigeons #UnityIsStrength #MoralStories #3DAnimation\n\nशिकारी के जाल में फंसे कबूतरों ने एकजुट होकर आज़ादी पाई! 🕊️💪 यह शानदार 3D पंचतंत्र कहानी देखो!\n\n🎯 कहानी का सार: एकता में शक्ति है — मिलकर हर मुश्किल पार की जा सकती है!" + DESCRIPTION_FOOTER,
        "tags": ["शिकारी और कबूतर", "Hunter Pigeons Story Hindi", "Unity is Strength", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "Ekta Mein Bal Hai", "Kids Animation Hindi"]
    },
    "diwali_magic_rangoli": {
        "title": "जादुई रंगोली: दिवाली की रात चमत्कार! 🎨🪔 The Magic Rangoli | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #Diwali #HindiKahaniya #MagicRangoli #MoralStories #3DAnimation\n\nपिंकी की रंगोली में छुपा था दिवाली का असली जादू! 🎨🪔 यह दिल छू लेने वाली 3D दिवाली कहानी देखो!\n\n🎯 कहानी का सार: सच्चे दिल से बनाई हर कला में जादू होता है!" + DESCRIPTION_FOOTER,
        "tags": ["जादुई रंगोली", "Magic Rangoli Diwali Story", "Diwali Special Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Rangoli Festival", "MagicalTalesKidz", "shorts", "yt shorts", "दिवाली रंगोली", "Kids Animation Hindi", "Chintu Monkey", "Pinki Elephant"]
    },
    "clever_crow_necklace": {
        "title": "चालाक कौए ने हार कैसे पाया? 🐦💎 The Clever Crow | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #CleverCrow #Panchatantra #MoralStories #3DAnimation\n\nकाल कौए ने अपनी चतुराई से राजकुमारी का हार वापस दिलाया! 🐦💎 यह रोचक 3D पंचतंत्र कहानी ज़रूर देखो!\n\n🎯 कहानी का सार: बुद्धि और धैर्य से हर मुश्किल हल हो जाती है!" + DESCRIPTION_FOOTER,
        "tags": ["चालाक कौआ", "Clever Crow Necklace Story", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "Kalu Crow", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "Kids Animation Hindi", "Crow Smartness Story"]
    },
    "magic_wishing_tree": {
        "title": "जादुई कल्पवृक्ष: सच्ची इच्छा पूरी होती है! 🌳✨ The Magic Wishing Tree | 3D Hindi Kahaniya #Shorts",
        "description": "#Shorts #HindiKahaniya #MagicWishingTree #Kalpavriksha #MoralStories #3DAnimation\n\nएक सच्चे दिल वाले बच्चे को मिला जादुई कल्पवृक्ष — पर क्या उसकी इच्छा पूरी हुई? 🌳✨ देखो इस शानदार 3D कहानी में!\n\n🎯 कहानी का सार: लालच नहीं, सच्चाई और दयालुता से मिलती है मन की शांति!" + DESCRIPTION_FOOTER,
        "tags": ["जादुई कल्पवृक्ष", "Kalpavriksha Story in Hindi", "Magic Wishing Tree", "Panchatantra Stories in Hindi", "3D Hindi Kahaniya", "Moral Stories for Kids", "Hindi Cartoon", "Chintu Monkey", "MagicalTalesKidz", "shorts", "yt shorts", "बाल कहानियां", "Kids Animation Hindi"]
    }
}


# ──────────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────────

def get_youtube_client():
    """Returns authenticated YouTube API client."""
    try:
        import googleapiclient.discovery
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        token_file = os.path.join(BASE_DIR, "token.json")
        scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

        if not os.path.exists(token_file):
            raise FileNotFoundError(f"token.json not found at {token_file}")

        credentials = Credentials.from_authorized_user_file(token_file, scopes)
        if credentials.expired and credentials.refresh_token:
            print("[auth] Refreshing expired credentials...", flush=True)
            credentials.refresh(Request())
            with open(token_file, "w") as f:
                f.write(credentials.to_json())

        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    except Exception as e:
        print(f"[auth] Error: {e}", flush=True)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# SEO SCORING
# ──────────────────────────────────────────────────────────────────────────────

def score_seo(title: str, description: str, tags: list) -> dict:
    """Score SEO health of a video's metadata. Returns score 0-100."""
    score = 0
    issues = []
    suggestions = []

    # Title scoring (max 30 pts)
    if title:
        t_len = len(title)
        if 50 <= t_len <= 70:
            score += 30
        elif 40 <= t_len < 50:
            score += 20
            suggestions.append(f"Title length {t_len} chars — optimal is 50-70")
        elif t_len > 70:
            score += 15
            issues.append(f"Title too long ({t_len} chars) — YouTube truncates at ~70")
        else:
            score += 10
            issues.append(f"Title too short ({t_len} chars)")

        # Check Hindi keyword in title
        if any(k in title for k in ["कहानी", "Kahaniya", "Hindi", "Shorts"]):
            score += 5
        else:
            suggestions.append("Add 'Hindi Kahaniya' or 'Shorts' to title")

        # Check emoji in title
        if any(ord(c) > 127 and ord(c) > 9999 for c in title):
            score += 5

    # Description scoring (max 30 pts)
    if description:
        d_len = len(description)
        if d_len >= 500:
            score += 20
        elif d_len >= 200:
            score += 12
            suggestions.append(f"Description only {d_len} chars — aim for 500+")
        else:
            score += 5
            issues.append(f"Description too short ({d_len} chars)")

        if "Subscribe" in description or "सब्सक्राइब" in description:
            score += 5
        else:
            suggestions.append("Add Subscribe CTA to description")

        if "playlist" in description.lower():
            score += 5
        else:
            suggestions.append("Add playlist link to description")

    # Tags scoring (max 25 pts)
    if tags:
        if 10 <= len(tags) <= 15:
            score += 15
        elif 5 <= len(tags) < 10:
            score += 8
            suggestions.append(f"Only {len(tags)} tags — use 10-15 for best coverage")
        else:
            score += 3

        # Check primary keywords in tags
        primary_hits = sum(1 for pk in KEYWORD_CLUSTERS["primary"] if any(pk.lower() in t.lower() for t in tags))
        score += min(10, primary_hits * 3)
        if primary_hits < 2:
            suggestions.append("Add more primary keywords to tags: Hindi Kahaniya, Moral Stories")

    # Bonus: #Shorts in description
    if description and "#Shorts" in description:
        score += 10

    return {
        "score": min(100, score),
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
        "issues": issues,
        "suggestions": suggestions
    }


# ──────────────────────────────────────────────────────────────────────────────
# AUDIT
# ──────────────────────────────────────────────────────────────────────────────

def audit_all_videos(youtube=None):
    """Pull current metadata for all videos and score SEO health."""
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    with open(tracker_file, "r", encoding="utf-8") as f:
        tracker = json.load(f)

    yt_videos = tracker.get("youtube", {})
    results = []

    print("\n" + "="*70)
    print("🔍 SEO AUDIT — MagicalTalesKidz YouTube Channel")
    print("="*70)
    print(f"{'Story Key':<28} {'Video ID':<16} {'SEO Score':<12} {'Grade'}")
    print("-"*70)

    for story_key, data in yt_videos.items():
        video_id = data.get("video_id") or data.get("media_id", "")
        if not video_id or len(video_id) < 8:
            continue

        title = data.get("title", "")
        description = data.get("description", "")
        tags = data.get("tags", [])

        # If we have a live YouTube client, fetch actual metadata
        if youtube and not description:
            try:
                resp = youtube.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()
                items = resp.get("items", [])
                if items:
                    snippet = items[0]["snippet"]
                    title = snippet.get("title", title)
                    description = snippet.get("description", "")
                    tags = snippet.get("tags", [])
                time.sleep(0.3)  # Rate limit
            except Exception as e:
                pass

        # Check if upgrade available
        has_upgrade = story_key in VIDEO_SEO_UPGRADES
        upgrade_data = VIDEO_SEO_UPGRADES.get(story_key, {})
        upg_title = upgrade_data.get("title", title)
        upg_desc = upgrade_data.get("description", description)
        upg_tags = upgrade_data.get("tags", tags)

        current_score = score_seo(title, description, tags)
        upgraded_score = score_seo(upg_title, upg_desc, upg_tags) if has_upgrade else current_score

        result = {
            "story_key": story_key,
            "video_id": video_id,
            "current": {"title": title, "score": current_score},
            "upgraded": {"title": upg_title, "score": upgraded_score} if has_upgrade else None,
            "needs_upgrade": has_upgrade and upgraded_score["score"] > current_score["score"]
        }
        results.append(result)

        upgrade_marker = f" → {upgraded_score['score']}/100 ({upgraded_score['grade']}) ✨" if has_upgrade else ""
        print(f"  {story_key:<26} {video_id:<14} {current_score['score']:>3}/100 ({current_score['grade']}){upgrade_marker}")

    print("="*70)

    # Save audit report
    report = {
        "audited_at": datetime.now().isoformat(),
        "total_videos": len(results),
        "videos": results
    }
    report_path = os.path.join(BASE_DIR, "seo_audit_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📊 Full audit saved to: {report_path}")
    return results


# ──────────────────────────────────────────────────────────────────────────────
# UPDATE SINGLE VIDEO
# ──────────────────────────────────────────────────────────────────────────────

def update_video_seo(youtube, story_key: str) -> bool:
    """Update a single video's SEO metadata using upgrade data."""
    if story_key not in VIDEO_SEO_UPGRADES:
        print(f"⚠️  No SEO upgrade defined for '{story_key}'")
        return False

    # Get video_id from tracker
    tracker_file = os.path.join(BASE_DIR, "uploads_tracker.json")
    with open(tracker_file, "r", encoding="utf-8") as f:
        tracker = json.load(f)

    video_data = tracker.get("youtube", {}).get(story_key, {})
    video_id = video_data.get("video_id") or video_data.get("media_id", "")
    if not video_id or len(video_id) < 8:
        print(f"⚠️  No valid video_id found for '{story_key}'")
        return False

    upgrade = VIDEO_SEO_UPGRADES[story_key]

    print(f"\n🔧 Updating SEO for: {story_key} (ID: {video_id})")
    print(f"   New Title: {upgrade['title'][:60]}...")

    try:
        # Fetch current snippet to preserve required fields
        current = youtube.videos().list(part="snippet,localizations", id=video_id).execute()
        items = current.get("items", [])
        if not items:
            print(f"   ⚠️  Video {video_id} not found on channel")
            return False

        snippet = items[0]["snippet"]
        snippet["title"] = upgrade["title"]
        snippet["description"] = upgrade["description"]
        snippet["tags"] = upgrade["tags"]
        snippet["defaultLanguage"] = "hi"
        snippet["defaultAudioLanguage"] = "hi"

        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        ).execute()

        print(f"   ✅ SEO updated successfully for {story_key}!")
        time.sleep(1)  # Rate limit
        return True

    except Exception as e:
        print(f"   ❌ Error updating {story_key}: {e}")
        return False


def update_all_videos_seo(youtube):
    """Batch-update all videos with improved SEO metadata."""
    print("\n" + "="*70)
    print("🚀 BATCH SEO UPDATE — All MagicalTalesKidz Videos")
    print("="*70)

    success_count = 0
    fail_count = 0

    for story_key in VIDEO_SEO_UPGRADES:
        ok = update_video_seo(youtube, story_key)
        if ok:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(2)  # Respect API quota

    print(f"\n✅ Updated: {success_count} | ❌ Failed: {fail_count}")
    print("="*70)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SEO Optimizer for MagicalTalesKidz YouTube Channel")
    parser.add_argument("--audit", action="store_true", help="Audit all videos' current SEO scores")
    parser.add_argument("--update", type=str, metavar="STORY_KEY", help="Update single video's SEO metadata")
    parser.add_argument("--update-all", action="store_true", help="Batch update all videos with improved SEO")
    parser.add_argument("--report", action="store_true", help="Print existing SEO audit report")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making API calls")
    args = parser.parse_args()

    if args.report:
        report_path = os.path.join(BASE_DIR, "seo_audit_report.json")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print("No audit report found. Run --audit first.")
        return

    if args.dry_run:
        print("\n🔍 DRY RUN — SEO Upgrades Preview")
        for key, data in VIDEO_SEO_UPGRADES.items():
            score = score_seo(data["title"], data["description"], data["tags"])
            print(f"  {key:<28} Score: {score['score']}/100 ({score['grade']})")
            print(f"    Title: {data['title'][:65]}...")
        return

    youtube = get_youtube_client()

    if args.audit:
        audit_all_videos(youtube)
    elif args.update:
        if not youtube:
            print("❌ YouTube auth failed. Cannot update.")
            return
        update_video_seo(youtube, args.update)
    elif args.update_all:
        if not youtube:
            print("❌ YouTube auth failed. Cannot update.")
            return
        update_all_videos_seo(youtube)
    else:
        # Default: run audit
        audit_all_videos(youtube)


if __name__ == "__main__":
    main()

