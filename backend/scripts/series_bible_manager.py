# -*- coding: utf-8 -*-
"""
Series Bible Manager — MagicalTalesKidz
Manages characters, visual standards, voice parameters, and story inventory.

Usage:
  python backend/scripts/series_bible_manager.py --show
  python backend/scripts/series_bible_manager.py --add-appearance chintu story_key
  python backend/scripts/series_bible_manager.py --add-queue story_key 2026-11-07
"""

import os
import sys
import json
import argparse
from datetime import datetime

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE_PATH = os.path.join(BASE_DIR, "output", "series_bible.json")

def load_bible():
    if not os.path.exists(BIBLE_PATH):
        raise FileNotFoundError(f"Series Bible not found at {BIBLE_PATH}")
    with open(BIBLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_bible(data):
    with open(BIBLE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Series Bible updated: {BIBLE_PATH}")

def show_summary():
    data = load_bible()
    print("=" * 70)
    print("📖 MAGICALTALESKIDZ SERIES BIBLE v" + data.get("version", "1.0"))
    print("=" * 70)
    print(f"Channel: {data['channel']['name']} ({data['channel']['handle']})")
    print(f"Target Age: {data['channel']['target_age']} | Prime Window: {data['channel']['prime_publish_time_ist']} IST")
    print("\n🎭 CHARACTERS:")
    for key, char in data.get("characters", {}).items():
        print(f"  • {char['name']} ({char['hindi_name']}) - {char['species']} [{char['role'].upper()}]")
        print(f"    Style: {char['appearance']['style']} | Accessory: {char['appearance'].get('signature_accessory', 'None')}")
        print(f"    Appearances: {len(char.get('story_appearances', []))} stories")
    
    print("\n📅 STORY QUEUE:")
    for item in data.get("story_queue", []):
        print(f"  • {item['key']:<25} | Status: {item['status']:<10} | Target: {item.get('scheduled', 'TBD')}")
    print("=" * 70)

def add_appearance(char_key, story_key):
    data = load_bible()
    if char_key not in data.get("characters", {}):
        print(f"❌ Unknown character '{char_key}'. Available: {list(data.get('characters', {}).keys())}")
        return
    apps = data["characters"][char_key].setdefault("story_appearances", [])
    if story_key not in apps:
        apps.append(story_key)
        save_bible(data)
        print(f"✅ Added '{story_key}' to appearances of {char_key}.")
    else:
        print(f"ℹ️ '{story_key}' already recorded for {char_key}.")

def add_to_queue(story_key, scheduled_date, occasion=""):
    data = load_bible()
    queue = data.setdefault("story_queue", [])
    for item in queue:
        if item.get("key") == story_key:
            item["scheduled"] = scheduled_date
            if occasion:
                item["occasion"] = occasion
            save_bible(data)
            print(f"✅ Updated existing story '{story_key}' in queue.")
            return
    queue.append({
        "key": story_key,
        "status": "planned",
        "scheduled": scheduled_date,
        "occasion": occasion
    })
    save_bible(data)
    print(f"✅ Enqueued '{story_key}' for {scheduled_date}.")

def main():
    parser = argparse.ArgumentParser(description="Series Bible Manager")
    parser.add_argument("--show", action="store_true", help="Display Series Bible summary")
    parser.add_argument("--add-appearance", nargs=2, metavar=("CHAR", "STORY"), help="Record character appearance")
    parser.add_argument("--add-queue", nargs=2, metavar=("STORY", "DATE"), help="Add/update story in queue")
    parser.add_argument("--occasion", type=str, default="", help="Occasion for story queue")
    args = parser.parse_args()

    if args.show:
        show_summary()
    elif args.add_appearance:
        add_appearance(args.add_appearance[0], args.add_appearance[1])
    elif args.add_queue:
        add_to_queue(args.add_queue[0], args.add_queue[1], args.occasion)
    else:
        show_summary()

if __name__ == "__main__":
    main()

