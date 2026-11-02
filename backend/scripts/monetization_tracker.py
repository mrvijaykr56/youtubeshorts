# -*- coding: utf-8 -*-
"""
Monetization Tracker — MagicalTalesKidz
Tracks YouTube Partner Program eligibility, revenue milestones,
and generates sponsorship/monetization strategy reports.

Usage:
  python backend/scripts/monetization_tracker.py --status       # Full monetization status
  python backend/scripts/monetization_tracker.py --ypt          # YPP eligibility check
  python backend/scripts/monetization_tracker.py --sponsorship  # Generate sponsorship brief
  python backend/scripts/monetization_tracker.py --forecast     # Growth forecast
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
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

# YouTube Partner Program thresholds
YPP_THRESHOLD_SUBS = 1000
YPP_THRESHOLD_WATCH_HOURS = 4000  # in 12 months
YPP_SHORTS_THRESHOLD_VIEWS = 10_000_000  # 10M Shorts views (alternative)

# Channel current state (updated from API or manually)
CHANNEL_STATE = {
    "subscribers": 3,
    "total_views": 256,
    "total_videos": 26,
    "channel_start_date": "2026-10-20",
    "channel_id": "UCL3Xsads7oyNr70erqz8vPQ",
    "instagram_followers": 0,  # Update after checking
    "instagram_avg_plays": 223  # Average reels plays
}

# Revenue estimates (industry benchmarks for kids Hindi content)
REVENUE_BENCHMARKS = {
    "youtube_rpm_usd": 1.50,        # Revenue per 1000 views (Hindi kids content)
    "youtube_rpm_shorts_usd": 0.05,  # Shorts RPM (lower than long-form)
    "instagram_brand_deal_per_1k_followers": 5,  # USD per 1K followers
    "sponsorship_per_video_at_10k_subs": 50,     # USD per sponsored video
    "sponsorship_per_video_at_100k_subs": 500,   # USD per sponsored video
    "affiliate_commission_rate": 0.05            # 5% average
}

# Growth projections (conservative/realistic/optimistic)
GROWTH_SCENARIOS = {
    "conservative": {"daily_sub_rate": 2, "daily_view_rate": 50},
    "realistic": {"daily_sub_rate": 5, "daily_view_rate": 120},
    "optimistic": {"daily_sub_rate": 15, "daily_view_rate": 400}
}


# ──────────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────────

def get_live_stats():
    """Try to fetch live channel stats from YouTube API."""
    try:
        import googleapiclient.discovery
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        token_file = os.path.join(BASE_DIR, "token.json")
        scopes = [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

        if not os.path.exists(token_file):
            return None

        credentials = Credentials.from_authorized_user_file(token_file, scopes)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        yt = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        resp = yt.channels().list(
            part="statistics,snippet",
            id=CHANNEL_STATE["channel_id"]
        ).execute()

        items = resp.get("items", [])
        if items:
            stats = items[0]["statistics"]
            return {
                "subscribers": int(stats.get("subscriberCount", CHANNEL_STATE["subscribers"])),
                "total_views": int(stats.get("viewCount", CHANNEL_STATE["total_views"])),
                "total_videos": int(stats.get("videoCount", CHANNEL_STATE["total_videos"]))
            }
    except Exception as e:
        print(f"[live_stats] Using cached data: {e}", flush=True)

    return None


# ──────────────────────────────────────────────────────────────────────────────
# YPP ELIGIBILITY
# ──────────────────────────────────────────────────────────────────────────────

def check_ypp_eligibility(live_stats=None):
    """Calculate YPP eligibility gap and time to achieve."""
    stats = live_stats or CHANNEL_STATE

    subs = stats.get("subscribers", CHANNEL_STATE["subscribers"])
    views = stats.get("total_views", CHANNEL_STATE["total_views"])

    # Estimate watch hours (avg 30s per short = 0.5 min, 80% completion)
    avg_watch_minutes_per_view = 0.4  # 24 seconds avg
    estimated_watch_hours = (views * avg_watch_minutes_per_view) / 60

    print("\n" + "="*65)
    print("💰 YOUTUBE PARTNER PROGRAM (YPP) ELIGIBILITY TRACKER")
    print("="*65)
    print(f"\n📊 Current Channel Status:")
    print(f"   Subscribers:        {subs:,} / {YPP_THRESHOLD_SUBS:,}  ({(subs/YPP_THRESHOLD_SUBS*100):.1f}%)")
    print(f"   Estimated Watch Hrs: {estimated_watch_hours:.1f} / {YPP_THRESHOLD_WATCH_HOURS:,}  ({(estimated_watch_hours/YPP_THRESHOLD_WATCH_HOURS*100):.1f}%)")
    print(f"   Total Views:        {views:,}")

    subs_gap = max(0, YPP_THRESHOLD_SUBS - subs)
    watch_gap = max(0, YPP_THRESHOLD_WATCH_HOURS - estimated_watch_hours)

    print(f"\n🎯 Gap to YPP:")
    print(f"   Need {subs_gap:,} more subscribers")
    print(f"   Need {watch_gap:.0f} more watch hours")

    # Time estimates
    print(f"\n⏱️  Time to YPP (by scenario):")
    for scenario, rates in GROWTH_SCENARIOS.items():
        daily_subs = rates["daily_sub_rate"]
        daily_views = rates["daily_view_rate"]
        daily_watch_min = daily_views * avg_watch_minutes_per_view
        daily_watch_hours = daily_watch_min / 60

        days_for_subs = subs_gap / daily_subs if daily_subs > 0 else float('inf')
        days_for_watch = watch_gap / daily_watch_hours if daily_watch_hours > 0 else float('inf')
        days_total = max(days_for_subs, days_for_watch)
        target_date = datetime.now() + timedelta(days=days_total)

        print(f"   {scenario.capitalize():<14}: {days_total:.0f} days → {target_date.strftime('%b %Y')}"
              f"  ({daily_subs}/day subs, {daily_views}/day views)")

    print(f"\n💡 Priority Actions to Accelerate YPP:")
    print(f"   1. Post 1 video/day consistently at 18:30 IST")
    print(f"   2. Share each Short to Instagram + WhatsApp groups")
    print(f"   3. Create 1-2 long-form compilations/month (more watch hours)")
    print(f"   4. Engage in comments within first hour of posting")
    print(f"   5. Use Children's Day (Nov 14) for viral push")

    return {
        "subs": subs,
        "subs_gap": subs_gap,
        "estimated_watch_hours": estimated_watch_hours,
        "watch_hours_gap": watch_gap,
        "ypp_eligible": subs >= YPP_THRESHOLD_SUBS and estimated_watch_hours >= YPP_THRESHOLD_WATCH_HOURS
    }


# ──────────────────────────────────────────────────────────────────────────────
# SPONSORSHIP BRIEF
# ──────────────────────────────────────────────────────────────────────────────

def generate_sponsorship_brief():
    """Generate a media kit / sponsorship brief for brand deals."""
    brief = """
================================================================================
📦 MEDIA KIT — MagicalTalesKidz
    Premium Hindi 3D Kids Content | YouTube Shorts + Instagram Reels
================================================================================

🎯 CHANNEL OVERVIEW
-------------------
Channel Name  : MagicalTalesKidz
Platform      : YouTube (@MagicalTalesKidz) + Instagram (@magicaltaleskid)
Content Type  : 3D Animated Hindi Panchatantra & Moral Stories
Target Demo   : Kids age 3–12 + Parents (Hindi-speaking households)
Language      : Pure Hindi (Devanagari) with optional English subtitles
Format        : YouTube Shorts (9:16, 30–42s) + Instagram Reels
Publishing    : Daily at 18:30 IST

📊 AUDIENCE DEMOGRAPHICS
-------------------------
Primary Language : Hindi
Primary Markets  : India (Tier 1/2 cities), Indian diaspora (UAE, UK, USA, Canada)
Age Bracket      : Parents 25–40, Kids 3–12
Interest Profile : Kids education, moral stories, Indian culture, animation

💰 SPONSORSHIP PACKAGES
------------------------
Package A — Mention (5s verbal callout)     : ₹500 / $6 per video
Package B — Integration (15s story segment) : ₹2,000 / $24 per video
Package C — Dedicated Episode               : ₹5,000 / $60 per video
Package D — Monthly Bundle (30 videos)      : Custom pricing

Best-fit Brands:
  • Kids education apps (BYJU'S, Vedantu, Toppr)
  • Children's food/health brands (Complan, Horlicks, Pediasure)
  • Stationery/toys (Crayola, Funskool, Lego India)
  • OTT platforms for kids (Disney+ Hotstar, Amazon miniTV)
  • EdTech/language learning apps

📈 GROWTH TRAJECTORY
---------------------
Channel launched  : October 20, 2026
Content cadence   : 1 Short/day + 1 Reel/day (cross-posting)
Growth target     : 1,000 subscribers by Jan 2027
Revenue target    : YPP eligible by Mar 2027

📧 CONTACT
-----------
For brand partnerships: [Add contact email]
YouTube: https://www.youtube.com/@MagicalTalesKidz
Instagram: https://www.instagram.com/magicaltaleskid/

================================================================================
"""
    print(brief)

    # Save to file
    brief_path = os.path.join(BASE_DIR, "sponsorship_brief.txt")
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(brief)
    print(f"✅ Sponsorship brief saved to: {brief_path}")


# ──────────────────────────────────────────────────────────────────────────────
# REVENUE FORECAST
# ──────────────────────────────────────────────────────────────────────────────

def revenue_forecast():
    """Project revenue at key subscriber milestones."""
    print("\n" + "="*65)
    print("📈 REVENUE FORECAST — MagicalTalesKidz")
    print("="*65)

    milestones = [1000, 5000, 10000, 50000, 100000]

    print(f"\n{'Subscribers':<14} {'Monthly Views':<16} {'Ad Revenue/mo':<16} {'Sponsorship/mo':<18} {'Total/mo'}")
    print("-"*75)

    for subs in milestones:
        # Estimate monthly views based on subs (avg 10x views per sub per month for shorts)
        monthly_views = subs * 8
        ad_revenue_usd = (monthly_views / 1000) * REVENUE_BENCHMARKS["youtube_rpm_shorts_usd"]
        sponsorship_usd = (REVENUE_BENCHMARKS["sponsorship_per_video_at_10k_subs"]
                          if subs < 10000 else REVENUE_BENCHMARKS["sponsorship_per_video_at_100k_subs"]) * 4  # 4 deals/month
        total_usd = ad_revenue_usd + sponsorship_usd
        total_inr = total_usd * 84  # Approx INR conversion

        print(f"  {subs:>10,}   {monthly_views:>12,}   ${ad_revenue_usd:>8.2f}/mo    ${sponsorship_usd:>8.2f}/mo     ${total_usd:>8.2f} (₹{total_inr:,.0f})")

    print(f"\n💡 Revenue Unlocking Strategy:")
    print(f"   • 0–1K subs: Focus on growth, build audience loyalty, zero ads")
    print(f"   • 1K–5K subs: Apply for YPP, start affiliate links in description")
    print(f"   • 5K–10K subs: Approach micro-brands for ₹500–2000/video deals")
    print(f"   • 10K–50K subs: Channel memberships, Super Thanks, brand deals ₹5K+")
    print(f"   • 50K+ subs: Premium sponsorships, merchandise, courses")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Monetization Tracker for MagicalTalesKidz")
    parser.add_argument("--status", action="store_true", help="Full monetization status report")
    parser.add_argument("--ypp", action="store_true", help="Check YPP eligibility and timeline")
    parser.add_argument("--sponsorship", action="store_true", help="Generate sponsorship media kit")
    parser.add_argument("--forecast", action="store_true", help="Revenue forecast by milestone")
    args = parser.parse_args()

    live = get_live_stats()
    if live:
        print(f"📡 Live stats: {live['subscribers']} subs, {live['total_views']} views")

    if args.ypp or args.status:
        check_ypp_eligibility(live)

    if args.sponsorship or args.status:
        generate_sponsorship_brief()

    if args.forecast or args.status:
        revenue_forecast()

    if not any([args.status, args.ypp, args.sponsorship, args.forecast]):
        # Default: show everything
        check_ypp_eligibility(live)
        revenue_forecast()


if __name__ == "__main__":
    main()

