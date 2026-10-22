"""
Unified Upload Tracker & Duplicate Prevention System for YouTube & Instagram
Maintains persistent ledger in backend/uploads_tracker.json and SQLite jobs.db
Prevents accidental duplicate uploads.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKER_JSON = os.path.join(BASE_DIR, "uploads_tracker.json")
DB_PATH = os.path.join(BASE_DIR, "jobs.db")

# Initial seed data from current live accounts
INITIAL_SEED_DATA = {
    "instagram": {
        "golden_goose": {
            "title": "Goose of Gold (सोने का अंडा)",
            "media_id": "4013742681645544223_53534506021",
            "code": "DezrbQHTnMf",
            "url": "https://www.instagram.com/reel/DezrbQHTnMf/",
            "uploaded_at": "2026-10-23 00:28:00",
            "status": "published"
        },
        "diwali_lion": {
            "title": "Lion King (जंगल का राजा)",
            "media_id": "DewmKH-JNWG",
            "code": "DewmKH-JNWG",
            "url": "https://www.instagram.com/reel/DewmKH-JNWG/",
            "uploaded_at": "2026-10-21 14:14:07",
            "status": "published"
        },
        "diwali_elephant": {
            "title": "Golu Elephant (नन्हा हाथी)",
            "media_id": "Dewl7A7p-Gb",
            "code": "Dewl7A7p-Gb",
            "url": "https://www.instagram.com/reel/Dewl7A7p-Gb/",
            "uploaded_at": "2026-10-21 14:12:02",
            "status": "published"
        },
        "squirrel_star": {
            "title": "Squirrel & Star (जादुई तारा)",
            "media_id": "DewlR2wJINr",
            "code": "DewlR2wJINr",
            "url": "https://www.instagram.com/reel/DewlR2wJINr/",
            "uploaded_at": "2026-10-21 14:06:25",
            "status": "published"
        },
        "crow_mango": {
            "title": "Crow & Monkey (कौवा और बंदर)",
            "media_id": "Dewk9qHJavu",
            "code": "Dewk9qHJavu",
            "url": "https://www.instagram.com/reel/Dewk9qHJavu/",
            "uploaded_at": "2026-10-21 14:03:39",
            "status": "published"
        },
        "peacock_feathers": {
            "title": "Peacock (घमंडी मोर)",
            "media_id": "Dewks3tJEpK",
            "code": "Dewks3tJEpK",
            "url": "https://www.instagram.com/reel/Dewks3tJEpK/",
            "uploaded_at": "2026-10-21 14:01:22",
            "status": "published"
        },
        "magic_paintbrush": {
            "title": "Magic Paintbrush (जादुई ब्रश)",
            "media_id": "DewkdrAp1eF",
            "code": "DewkdrAp1eF",
            "url": "https://www.instagram.com/reel/DewkdrAp1eF/",
            "uploaded_at": "2026-10-21 13:59:22",
            "status": "published"
        },
        "clever_rabbit": {
            "title": "Clever Rabbit (चतुर खरगोश)",
            "media_id": "DewkHItJ8Fm",
            "code": "DewkHItJ8Fm",
            "url": "https://www.instagram.com/reel/DewkHItJ8Fm/",
            "uploaded_at": "2026-10-21 13:56:16",
            "status": "published"
        },
        "monkey_and_crocodile": {
            "title": "Monkey & Croc (बंदर और मगरमच्छ)",
            "media_id": "DewjjXqp2R5",
            "code": "DewjjXqp2R5",
            "url": "https://www.instagram.com/reel/DewjjXqp2R5/",
            "uploaded_at": "2026-10-21 13:51:21",
            "status": "published"
        },
        "mouse_and_lion": {
            "title": "Mouse & Lion (शेर और चूहा)",
            "media_id": "Dewhu6VpnHb",
            "code": "Dewhu6VpnHb",
            "url": "https://www.instagram.com/reel/Dewhu6VpnHb/",
            "uploaded_at": "2026-10-21 13:35:30",
            "status": "published"
        }
    },
    "youtube": {
        "golden_goose": {
            "title": "Goose of Gold | 3D Hindi Kahaniya",
            "video_id": "RQsyj6r_980",
            "url": "https://www.youtube.com/shorts/RQsyj6r_980",
            "uploaded_at": "2026-10-22 22:30:00",
            "status": "published"
        },
        "blue_jackal": {
            "title": "The Blue Jackal | 3D Hindi Kahaniya",
            "video_id": "1d8fNhpscXY",
            "url": "https://www.youtube.com/shorts/1d8fNhpscXY",
            "uploaded_at": "2026-10-22 22:15:00",
            "status": "published"
        },
        "honest_woodcutter": {
            "title": "Honest Woodcutter | 3D Hindi Kahaniya",
            "video_id": "Wio6lrQKrjA",
            "url": "https://www.youtube.com/shorts/Wio6lrQKrjA",
            "uploaded_at": "2026-10-22 22:00:00",
            "status": "published"
        },
        "monkey_and_crocodile": {
            "title": "The Monkey & Crocodile",
            "video_id": "wsaNFDsKSM8",
            "url": "https://www.youtube.com/shorts/wsaNFDsKSM8",
            "uploaded_at": "2026-10-22 17:00:00",
            "status": "published"
        },
        "clever_rabbit": {
            "title": "The Clever Rabbit",
            "video_id": "HEVzgJuGzyE",
            "url": "https://www.youtube.com/shorts/HEVzgJuGzyE",
            "uploaded_at": "2026-10-21 12:00:00",
            "status": "published"
        },
        "mouse_and_lion": {
            "title": "The Lion and Mouse",
            "video_id": "WNNNbeNU_o4",
            "url": "https://www.youtube.com/shorts/WNNNbeNU_o4",
            "uploaded_at": "2026-10-21 11:30:00",
            "status": "published"
        },
        "magic_paintbrush": {
            "title": "The Magic Paintbrush",
            "video_id": "cKAR_Y-g0Gw",
            "url": "https://www.youtube.com/shorts/cKAR_Y-g0Gw",
            "uploaded_at": "2026-10-21 11:00:00",
            "status": "published"
        },
        "peacock_feathers": {
            "title": "The Proud Peacock",
            "video_id": "cN6k6lu0-Mc",
            "url": "https://www.youtube.com/shorts/cN6k6lu0-Mc",
            "uploaded_at": "2026-10-21 10:30:00",
            "status": "published"
        },
        "crow_mango": {
            "title": "Sharing Brings Joy",
            "video_id": "JNMuCm6b8xg",
            "url": "https://www.youtube.com/shorts/JNMuCm6b8xg",
            "uploaded_at": "2026-10-21 10:00:00",
            "status": "published"
        },
        "squirrel_star": {
            "title": "Cheeku's Magic Wish",
            "video_id": "OHny_kUkjAw",
            "url": "https://www.youtube.com/shorts/OHny_kUkjAw",
            "uploaded_at": "2026-10-21 09:30:00",
            "status": "published"
        },
        "diwali_elephant": {
            "title": "True Kindness",
            "video_id": "mR2eWSWiZoE",
            "url": "https://www.youtube.com/shorts/mR2eWSWiZoE",
            "uploaded_at": "2026-10-21 09:00:00",
            "status": "published"
        },
        "diwali_lion": {
            "title": "Power vs Love",
            "video_id": "OQGNGYqde3c",
            "url": "https://www.youtube.com/shorts/OQGNGYqde3c",
            "uploaded_at": "2026-10-21 08:30:00",
            "status": "published"
        },
        "miku_laddoo": {
            "title": "Never Be Greedy",
            "video_id": "cuaCG-6B-1M",
            "url": "https://www.youtube.com/shorts/cuaCG-6B-1M",
            "uploaded_at": "2026-10-20 18:00:00",
            "status": "published"
        },
        "ant_and_dove": {
            "title": "The Ant & Dove",
            "video_id": "HYHK9AW6tA8",
            "url": "https://www.youtube.com/shorts/HYHK9AW6tA8",
            "uploaded_at": "2026-06-25 12:00:00",
            "status": "published"
        }
    }
}

def init_tracker():
    if not os.path.exists(TRACKER_JSON):
        with open(TRACKER_JSON, "w", encoding="utf-8") as f:
            json.dump(INITIAL_SEED_DATA, f, indent=2, ensure_ascii=False)
    
    # Ensure SQLite table exists
    try:
        conn = sqlite3.connect(DB_PATH)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_key TEXT,
                    platform TEXT,
                    media_id TEXT,
                    url TEXT,
                    title TEXT,
                    uploaded_at TEXT,
                    status TEXT,
                    UNIQUE(story_key, platform)
                )
            """)
            # Seed SQLite if empty
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM platform_uploads")
            if cursor.fetchone()[0] == 0:
                for platform, stories in INITIAL_SEED_DATA.items():
                    for sk, info in stories.items():
                        cursor.execute("""
                            INSERT OR IGNORE INTO platform_uploads
                            (story_key, platform, media_id, url, title, uploaded_at, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            sk, platform,
                            info.get("media_id") or info.get("video_id"),
                            info.get("url"),
                            info.get("title"),
                            info.get("uploaded_at"),
                            info.get("status", "published")
                        ))
        conn.close()
    except Exception as e:
        print(f"[Tracker DB Note]: {e}")

def load_tracker():
    init_tracker()
    try:
        with open(TRACKER_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return INITIAL_SEED_DATA

def is_uploaded(platform: str, story_key: str) -> tuple[bool, dict]:
    """
    Checks if a story has already been uploaded to a specific platform.
    Returns (True, info_dict) if uploaded, (False, {}) otherwise.
    """
    tracker = load_tracker()
    plat_data = tracker.get(platform.lower(), {})
    if story_key.lower() in plat_data:
        return True, plat_data[story_key.lower()]
    return False, {}

def record_upload(platform: str, story_key: str, media_id: str, url: str, title: str = ""):
    """
    Records a completed upload in both uploads_tracker.json and SQLite jobs.db.
    """
    init_tracker()
    tracker = load_tracker()
    plat = platform.lower()
    if plat not in tracker:
        tracker[plat] = {}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "title": title or story_key,
        "media_id": media_id,
        "url": url,
        "uploaded_at": now_str,
        "status": "published"
    }
    tracker[plat][story_key.lower()] = entry

    with open(TRACKER_JSON, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)

    # Sync to SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO platform_uploads
                (story_key, platform, media_id, url, title, uploaded_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (story_key.lower(), plat, media_id, url, title, now_str, "published"))
        conn.close()
    except Exception as e:
        print(f"[Tracker Sync Note]: {e}")

    print(f"📝 [Tracker]: Successfully recorded {story_key} upload for {plat.upper()}!")

def show_status():
    tracker = load_tracker()
    print("=" * 75)
    print("📊 UNIFIED PLATFORM UPLOADS LEDGER (DUPLICATE PREVENTION)")
    print("=" * 75)

    for plat in ["youtube", "instagram"]:
        stories = tracker.get(plat, {})
        print(f"\n🌐 {plat.upper()} UPLOADS ({len(stories)} Published):")
        print("-" * 75)
        for i, (sk, info) in enumerate(stories.items(), 1):
            url = info.get("url", "")
            date = info.get("uploaded_at", "")
            print(f" {i:2d}. [{sk:<22}] | {date} | {url}")

    print("\n" + "=" * 75)

if __name__ == "__main__":
    init_tracker()
    show_status()
