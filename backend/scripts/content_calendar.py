# -*- coding: utf-8 -*-
"""
Content Calendar Engine — MagicalTalesKidz
Generates an algorithmic 30-Day editorial calendar aligning YouTube Shorts & Instagram Reels
with seasonal spikes, cultural festivals, character arcs, and audience retention loops.

Usage:
  python backend/scripts/content_calendar.py --generate
  python backend/scripts/content_calendar.py --ideas
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_MD = os.path.join(BASE_DIR, "content_calendar.md")
BIBLE_PATH = os.path.join(BASE_DIR, "output", "series_bible.json")
TRACKER_PATH = os.path.join(BASE_DIR, "uploads_tracker.json")

def generate_calendar():
    start_date = datetime(2026, 11, 3)
    
    # Pre-defined high retention stories & upcoming festival anchors
    schedule_data = [
        ("2026-11-03", "Tuesday", "magic_wishing_tree", "Shorts + Reel", "Kalpavriksha Wisdom", "Scheduled (18:30 IST)"),
        ("2026-11-04", "Wednesday", "magic_cauldron", "Shorts + Reel", "Greed vs Contentment", "Ready in Queue"),
        ("2026-11-05", "Thursday", "talkative_turtle", "Shorts + Reel", "Mindful Speech", "Ready in Queue"),
        ("2026-11-06", "Friday", "golden_fish", "Shorts + Reel", "Wishes & Karma", "Ready in Queue"),
        ("2026-11-07", "Saturday", "lion_and_clever_hare", "Shorts + Reel", "Wit over Strength", "Scripting"),
        ("2026-11-08", "Sunday", "panchatantra_compilation_vol2", "16:9 Longform", "Weekend Watch-Time Boost", "Compilation"),
        ("2026-11-09", "Monday", "two_fighting_goats", "Shorts + Reel", "Stubbornness Warning", "Scripting"),
        ("2026-11-10", "Tuesday", "monkey_and_cats_loaf", "Shorts + Reel", "Third-Party Meddling", "Scripting"),
        ("2026-11-11", "Wednesday", "brave_little_potter", "Shorts + Reel", "Accidental Bravery", "Planned"),
        ("2026-11-12", "Thursday", "four_friends_deer_tortoise", "Shorts + Reel", "Children's Day Leadup", "Planned"),
        ("2026-11-13", "Friday", "chintu_special_adventure", "Shorts + Reel", "Mascot Milestone", "Planned"),
        ("2026-11-14", "Saturday", "childrens_day_grand_magic", "Shorts + Reel", "Children's Day Special (Bal Diwas)", "Anchor Event"),
        ("2026-11-15", "Sunday", "chintu_friends_moral_quiz", "Community Poll", "Interactive Sunday", "Poll + Clip"),
        ("2026-11-16", "Monday", "donkey_in_lions_skin", "Shorts + Reel", "Fake Identity Consequence", "Planned"),
        ("2026-11-17", "Tuesday", "crane_and_clever_crab", "Shorts + Reel", "Deceit Meets Justice", "Planned"),
        ("2026-11-18", "Wednesday", "musical_donkey_jackal", "Shorts + Reel", "Timing in Life", "Planned"),
        ("2026-11-19", "Thursday", "three_fishes_caution", "Shorts + Reel", "Preparedness Saves Lives", "Planned"),
        ("2026-11-20", "Friday", "elephant_and_sparrow_solidarity", "Shorts + Reel", "Power of Small Allies", "Planned"),
        ("2026-11-21", "Saturday", "guru_nanak_jayanti_compassion", "Shorts + Reel", "Guru Nanak Jayanti Festival Special", "Festival Anchor"),
        ("2026-11-22", "Sunday", "panchatantra_compilation_vol3", "16:9 Longform", "Weekend Watch-Time Boost", "Compilation"),
        ("2026-11-23", "Monday", "cunning_jackal_drum_sound", "Shorts + Reel", "Facing the Unknown Fear", "Planned"),
        ("2026-11-24", "Tuesday", "mongoose_and_farmer_wife", "Shorts + Reel", "Haste Brings Regret", "Planned"),
        ("2026-11-25", "Wednesday", "foolish_camel_bell", "Shorts + Reel", "Self-Control Under Pressure", "Planned"),
        ("2026-11-26", "Thursday", "lion_mouse_eternal_friendship", "Shorts + Reel", "No Friend Too Small", "Planned"),
        ("2026-11-27", "Friday", "tortoise_flute_magical_melody", "Shorts + Reel", "Artistic Triumph", "Planned"),
        ("2026-11-28", "Saturday", "sparrows_nest_wild_wind", "Shorts + Reel", "Perseverance in Crisis", "Planned"),
        ("2026-11-29", "Sunday", "best_moments_chintu_shorts", "Shorts + Reel", "Channel Recap & Teaser", "Recap"),
        ("2026-11-30", "Monday", "golden_feather_swan_part2", "Shorts + Reel", "Sequel Story Arc", "Sequel"),
        ("2026-12-01", "Tuesday", "winter_forest_magic_lantern", "Shorts + Reel", "Winter Season Kickoff", "Seasonal"),
        ("2026-12-02", "Wednesday", "magic_snow_deer_himalayas", "Shorts + Reel", "Winter Wonderland Special", "Seasonal")
    ]

    md_content = "# 📅 30-Day Growth & Publishing Calendar — MagicalTalesKidz\n\n"
    md_content += "**Prime Distribution Window:** Daily 18:30 IST (13:00 UTC)\n"
    md_content += "**Cross-Platform Strategy:** YouTube Shorts (9:16) + Instagram Reels (9:16) + Bi-weekly 16:9 Compilations\n\n"
    md_content += "| Date | Day | Story Key / Title | Content Type | Strategic Focus / Occasion | Status |\n"
    md_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for row in schedule_data:
        md_content += f"| {row[0]} | {row[1]} | `{row[2]}` | {row[3]} | {row[4]} | {row[5]} |\n"

    md_content += "\n\n## 🎯 Strategic Milestones in This 30-Day Sprint:\n"
    md_content += "1. **Nov 3 - Nov 6**: Burn inventory backlog (`magic_wishing_tree`, `magic_cauldron`, `talkative_turtle`, `golden_fish`) at steady 1 video/day rate.\n"
    md_content += "2. **Nov 8 & Nov 22**: Launch two 16:9 Long-Form Compilations on Sundays to aggregate watch time for YPP (4,000 hrs threshold).\n"
    md_content += "3. **Nov 14 (Children's Day / Bal Diwas)**: High-retention festive tentpole special to capture search spikes.\n"
    md_content += "4. **Nov 21 (Guru Nanak Jayanti)**: Universal moral values special with cross-community viral hooks.\n"

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ Generated 30-Day Editorial Calendar at: {OUTPUT_MD}")
    print(md_content[:1200] + "\n...[truncated for display]...")

def print_ideas():
    ideas = [
        {"title": "बाल दिवस जादुई मेला: चिंटू का सरप्राइज! 🎪✨", "concept": "Children's Day Special — Chintu hosts a magical funfair where every balloon grants a kind wish.", "score": 94},
        {"title": "सियार और नगाड़ा: रहस्यमयी आवाज़ का सच! 🥁🦊", "concept": "Jackal and the War Drum — Overcoming fear of the unknown with curiosity.", "score": 89},
        {"title": "एकता में बल: चार पक्के दोस्त! 🦌🐢🕊️", "concept": "The Four Friends (Deer, Turtle, Crow, Mouse) outsmart the hunter together.", "score": 92},
        {"title": "मूर्ख ऊंट और मीठी बांसुरी! 🐪🎶", "concept": "The foolish camel who insists on singing in the night and ruins the feast.", "score": 85},
        {"title": "नेवला और किसान की पत्नी: जल्दबाज़ी का पछतावा! 🐍", "concept": "Loyal Mongoose — Heart-wrenching moral on never reacting without verifying the truth.", "score": 96}
    ]
    print("\n💡 TOP 5 HIGH-VIRALITY HINDI MORAL STORY CONCEPTS:")
    for idx, idea in enumerate(ideas, 1):
        print(f"{idx}. {idea['title']} (Viral Potential: {idea['score']}/100)")
        print(f"   Concept: {idea['concept']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", default=True, help="Generate calendar")
    parser.add_argument("--ideas", action="store_true", help="Print high virality ideas")
    args = parser.parse_args()

    if args.ideas:
        print_ideas()
    else:
        generate_calendar()
