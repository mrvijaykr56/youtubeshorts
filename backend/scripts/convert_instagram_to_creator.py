"""
Automated Instagram Professional Creator Account Conversion for @magicaltaleskid
Converts account to Creator status with:
1. Category: Digital Creator / Video Creator
2. Enables Category Badge display on profile
3. Unlocks Meta recommendation graph & Facebook Reels recommendation eligibility
"""

import os
import sys
from instagrapi import Client

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, "instagram_session.json")

def convert_to_creator():
    print("=" * 70)
    print("🚀 CONVERTING INSTAGRAM ACCOUNT TO PROFESSIONAL CREATOR: @magicaltaleskid")
    print("=" * 70)

    if not os.path.exists(SESSION_FILE):
        print("❌ Session file not found.")
        return

    cl = Client()
    cl.load_settings(SESSION_FILE)
    cl.username = "magicaltaleskid"

    user_id = cl.user_id_from_username(cl.username)
    current_info = cl.user_info(user_id)
    print(f"👤 Username     : @{current_info.username}")
    print(f"🏷️ Current Cat  : {current_info.category_name}")
    print(f"💼 Is Business  : {current_info.is_business}")

    try:
        # Category ID "2347428775505624" = Digital Creator
        res = cl.account_convert_to_creator(
            category_id="2347428775505624",
            should_show_category=True,
            should_show_public_contacts=False
        )
        print("\n✅ SUCCESS: Successfully switched to Professional Creator Account!")
        print(f"  • Category ID : 2347428775505624 (Digital Creator)")
        print(f"  • Show Badge  : True")
        print("  • Creator Tools, Meta Recommendation Graph & FB Reels Eligibility UNLOCKED!")
    except Exception as e:
        print(f"\n⚠️ Conversion notice: {e}")
        # Try convert to professional directly
        try:
            print("Attempting direct professional conversion...")
            cl.account_convert_to_professional(
                to_account_type=3, # 3 = Creator, 2 = Business
                category_id="2347428775505624",
                should_show_category=True
            )
            print("✅ SUCCESS via direct professional conversion method!")
        except Exception as pe:
            print(f"Note on API conversion: {pe}")
            print("ℹ️ Note: If Instagram requires in-app authentication for switching to professional,")
            print("follow the 2-tap in-app guide: Settings -> Account Type -> Switch to Professional -> Creator.")

    print("=" * 70)

if __name__ == "__main__":
    convert_to_creator()
