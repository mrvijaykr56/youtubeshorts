# -*- coding: utf-8 -*-
"""
analytics_engine.py — YouTube Analytics API puller for MagicalTalesKidz
Fetches per-video performance metrics, computes viral scores, and writes
analytics_cache.json with recommendations.
"""

import sys
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import os
import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
TOKEN_PATH = BASE_DIR / "token.json"
TRACKER_PATH = BASE_DIR / "uploads_tracker.json"
DEFAULT_OUTPUT = BASE_DIR / "analytics_cache.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def load_credentials():
    """Load / refresh OAuth2 credentials from token.json."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        if not TOKEN_PATH.exists():
            raise FileNotFoundError(f"token.json not found at {TOKEN_PATH}")

        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json(), encoding='utf-8')
        return creds
    except Exception as exc:
        raise RuntimeError(f"Failed to load credentials: {exc}") from exc


# ---------------------------------------------------------------------------
# Upload tracker helpers
# ---------------------------------------------------------------------------

def load_video_ids(tracker_path: Path) -> list[dict]:
    """Return list of {video_id, story_key, title} from uploads_tracker.json."""
    if not tracker_path.exists():
        print(f"[WARN] uploads_tracker.json not found at {tracker_path}")
        return []

    with tracker_path.open(encoding='utf-8', errors='replace') as fh:
        tracker = json.load(fh)

    videos = []
    youtube_section = tracker.get("youtube", {})
    for story_key, data in youtube_section.items():
        vid = data.get("video_id")
        if not vid:
            continue  # skip entries with only media_id
        videos.append({
            "video_id": vid,
            "story_key": story_key,
            "title": data.get("title", story_key),
        })
    return videos


# ---------------------------------------------------------------------------
# Analytics fetchers
# ---------------------------------------------------------------------------

def fetch_analytics_for_video(yt_analytics, video_id: str, start_date: str, end_date: str) -> dict:
    """Fetch analytics metrics for a single video via YouTube Analytics API."""
    metrics = (
        "views,estimatedMinutesWatched,averageViewDuration,"
        "averageViewPercentage,subscribersGained,likes,comments,shares,"
        "impressions,impressionClickThroughRate"
    )
    resp = (
        yt_analytics.reports()
        .query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics=metrics,
            filters=f"video=={video_id}",
            dimensions="video",
        )
        .execute()
    )

    rows = resp.get("rows", [])
    col_headers = [c["name"] for c in resp.get("columnHeaders", [])]

    if not rows:
        return _empty_metrics()

    row = rows[0]
    # col_headers[0] is "video" dimension; skip it
    col_map = {name: idx for idx, name in enumerate(col_headers)}

    def g(key, default=0):
        idx = col_map.get(key)
        return row[idx] if idx is not None else default

    return {
        "views": int(g("views")),
        "watch_time_minutes": float(g("estimatedMinutesWatched")),
        "avg_view_duration_s": float(g("averageViewDuration")),
        "avg_view_percentage": float(g("averageViewPercentage")),
        "ctr_impressions": float(g("impressionClickThroughRate")),
        "likes": int(g("likes")),
        "comments": int(g("comments")),
        "shares": int(g("shares")),
        "subscribers_gained": int(g("subscribersGained")),
        "impressions": int(g("impressions")),
    }


def fetch_statistics_fallback(yt_data, video_ids: list[str]) -> dict:
    """Fallback: use Videos.list statistics endpoint (no Analytics API needed)."""
    result = {}
    # batch in groups of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = (
            yt_data.videos()
            .list(part="statistics", id=",".join(batch))
            .execute()
        )
        for item in resp.get("items", []):
            vid = item["id"]
            stats = item.get("statistics", {})
            result[vid] = {
                "views": int(stats.get("viewCount", 0)),
                "watch_time_minutes": 0,
                "avg_view_duration_s": 0,
                "avg_view_percentage": 0,
                "ctr_impressions": 0,
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "shares": 0,
                "subscribers_gained": 0,
                "impressions": 0,
            }
    return result


def _empty_metrics() -> dict:
    return {
        "views": 0,
        "watch_time_minutes": 0,
        "avg_view_duration_s": 0,
        "avg_view_percentage": 0,
        "ctr_impressions": 0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "subscribers_gained": 0,
        "impressions": 0,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_viral_score(metrics: dict, max_views: float = 1.0) -> float:
    """
    viral_score = (views*0.3 + avg_view_percentage*0.3 + ctr_impressions*100*0.2
                   + (likes+comments+shares)*0.2) normalized 0-100
    """
    views_norm = (metrics["views"] / max(max_views, 1)) * 100
    avg_pct = metrics["avg_view_percentage"]          # already 0-100
    ctr_component = metrics["ctr_impressions"] * 100  # 0-100
    engagement = metrics["likes"] + metrics["comments"] + metrics["shares"]
    engagement_norm = min(engagement, 10_000) / 100   # cap at 10k → 100

    score = (
        views_norm * 0.3
        + avg_pct * 0.3
        + ctr_component * 0.2
        + engagement_norm * 0.2
    )
    return min(round(score, 2), 100.0)


def assign_tier(score: float) -> str:
    if score > 80:
        return "viral"
    if score > 60:
        return "hot"
    if score > 40:
        return "warm"
    return "cold"


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def generate_recommendations(videos_data: dict) -> list[str]:
    recs = []

    all_metrics = [v["metrics"] for v in videos_data.values()]
    if not all_metrics:
        return ["No video data available. Publish your first Short to start tracking!"]

    avg_ctr = sum(m["ctr_impressions"] for m in all_metrics) / len(all_metrics)
    avg_ret = sum(m["avg_view_percentage"] for m in all_metrics) / len(all_metrics)
    total_views = sum(m["views"] for m in all_metrics)
    total_subs = sum(m["subscribers_gained"] for m in all_metrics)

    # CTR
    if avg_ctr < 0.04:
        recs.append(
            f"📌 Average CTR is {avg_ctr*100:.1f}% — below 4% benchmark. "
            "A/B test 2-3 thumbnail variations with stronger emotional hook faces."
        )
    elif avg_ctr > 0.08:
        recs.append(
            f"🔥 Excellent CTR at {avg_ctr*100:.1f}%! Current thumbnail style is working — "
            "maintain consistency with close-up character expressions."
        )

    # Retention
    if avg_ret < 50:
        recs.append(
            f"⚠️ Average view retention is {avg_ret:.1f}% — aim for >65%. "
            "Tighten scripts to 28-35s, open with a stronger visual shock in first 1.5s."
        )
    elif avg_ret > 70:
        recs.append(
            f"✅ Great retention at {avg_ret:.1f}%! Story pacing is working well. "
            "Consider testing a series format (2-3 episode arcs) to boost watch sessions."
        )

    # Viral performers
    viral_count = sum(1 for v in videos_data.values() if v["performance_tier"] == "viral")
    hot_count = sum(1 for v in videos_data.values() if v["performance_tier"] == "hot")
    if viral_count > 0:
        recs.append(
            f"🚀 {viral_count} video(s) reached VIRAL tier. "
            "Produce sequel stories for viral titles — audiences already love those characters."
        )
    if hot_count > 0:
        recs.append(
            f"🌡️ {hot_count} video(s) in HOT tier — boost these with a Community Post "
            "and pin them as channel highlight for 48h."
        )

    # Cold performers
    cold = [k for k, v in videos_data.items() if v["performance_tier"] == "cold"]
    if len(cold) > 3:
        recs.append(
            f"❄️ {len(cold)} videos are in COLD tier. Review their hooks — "
            "replace any opener starting with 'एक' and add a curiosity gap question in first frame."
        )

    # Subs conversion
    sub_rate = (total_subs / max(total_views, 1)) * 1000
    if sub_rate < 2:
        recs.append(
            "📊 Subscriber conversion is low (<2 per 1k views). "
            "Add a consistent end-card CTA: 'Subscribe for daily Kahaniyaan' in last 3s of every Short."
        )

    # Upload cadence
    recs.append(
        "📅 Maintain 18:30 IST daily publish schedule — algorithm rewards consistent cadence. "
        "Pre-schedule 7 days ahead using YouTube Studio batch upload."
    )

    if not recs:
        recs.append("Keep publishing consistently — channel is performing well across all metrics!")

    return recs


# ---------------------------------------------------------------------------
# Channel totals
# ---------------------------------------------------------------------------

def compute_channel_totals(videos_data: dict) -> dict:
    totals = {
        "total_videos_tracked": len(videos_data),
        "total_views": 0,
        "total_watch_time_minutes": 0,
        "total_likes": 0,
        "total_comments": 0,
        "total_shares": 0,
        "total_subscribers_gained": 0,
        "avg_viral_score": 0.0,
        "tier_breakdown": {"viral": 0, "hot": 0, "warm": 0, "cold": 0},
    }
    if not videos_data:
        return totals

    for v in videos_data.values():
        m = v["metrics"]
        totals["total_views"] += m["views"]
        totals["total_watch_time_minutes"] += m["watch_time_minutes"]
        totals["total_likes"] += m["likes"]
        totals["total_comments"] += m["comments"]
        totals["total_shares"] += m["shares"]
        totals["total_subscribers_gained"] += m["subscribers_gained"]
        tier = v["performance_tier"]
        totals["tier_breakdown"][tier] = totals["tier_breakdown"].get(tier, 0) + 1

    scores = [v["viral_score"] for v in videos_data.values()]
    totals["avg_viral_score"] = round(sum(scores) / len(scores), 2)
    return totals


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(videos_data: dict, channel_totals: dict, days: int):
    TIER_ICON = {"viral": "🚀", "hot": "🔥", "warm": "🌤️", "cold": "❄️"}
    print()
    print("=" * 90)
    print(f"  📊  MagicalTalesKidz — YouTube Analytics (last {days} days)")
    print("=" * 90)
    print(f"{'Story Key':<28} {'Views':>8} {'Ret%':>6} {'CTR%':>6} {'Likes':>6} {'Score':>7} {'Tier'}")
    print("-" * 90)

    for vid_id, info in sorted(
        videos_data.items(), key=lambda x: x[1]["viral_score"], reverse=True
    ):
        m = info["metrics"]
        icon = TIER_ICON.get(info["performance_tier"], "")
        key = info["story_key"][:27]
        print(
            f"{key:<28} {m['views']:>8,} {m['avg_view_percentage']:>5.1f}%"
            f" {m['ctr_impressions']*100:>5.1f}% {m['likes']:>6,}"
            f" {info['viral_score']:>6.1f} {icon} {info['performance_tier']}"
        )

    print("-" * 90)
    print(
        f"{'CHANNEL TOTAL':<28} {channel_totals['total_views']:>8,}"
        f"                         Avg Score: {channel_totals['avg_viral_score']}"
    )
    print("=" * 90)
    td = channel_totals["tier_breakdown"]
    print(f"  🚀 Viral: {td.get('viral',0)}  🔥 Hot: {td.get('hot',0)}"
          f"  🌤️  Warm: {td.get('warm',0)}  ❄️  Cold: {td.get('cold',0)}")
    print("=" * 90)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MagicalTalesKidz — YouTube Analytics Engine"
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT),
        help="Path to output JSON file (default: analytics_cache.json)"
    )
    parser.add_argument(
        "--days", type=int, default=28,
        help="Number of days to look back (default: 28)"
    )
    parser.add_argument(
        "--force-refresh", action="store_true",
        help="Ignore existing cache and force a fresh API pull"
    )
    args = parser.parse_args()

    output_path = Path(args.output)

    # Check existing cache
    if output_path.exists() and not args.force_refresh:
        print(f"[INFO] Cache found at {output_path}. Use --force-refresh to re-fetch.")
        with output_path.open(encoding='utf-8') as fh:
            cached = json.load(fh)
        print_summary(cached.get("videos", {}), cached.get("channel_totals", {}), args.days)
        return

    # Date range
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=args.days)).isoformat()
    end_date = today.isoformat()

    # Load video list from tracker
    video_entries = load_video_ids(TRACKER_PATH)
    if not video_entries:
        print("[WARN] No video IDs found in uploads_tracker.json. Exiting.")
        return

    print(f"[INFO] Found {len(video_entries)} video(s) to analyse. Range: {start_date} → {end_date}")

    # Build credentials and API clients
    try:
        creds = load_credentials()
        from googleapiclient.discovery import build
        yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)
        yt_data = build("youtube", "v3", credentials=creds)
        use_analytics_api = True
        print("[INFO] YouTube Analytics API v2 connected.")
    except Exception as exc:
        print(f"[WARN] Could not connect to Analytics API: {exc}")
        print("[INFO] Falling back to Videos.list statistics endpoint.")
        use_analytics_api = False
        try:
            creds = load_credentials()
            from googleapiclient.discovery import build
            yt_data = build("youtube", "v3", credentials=creds)
        except Exception as exc2:
            print(f"[ERROR] Cannot connect to YouTube Data API either: {exc2}")
            return

    # Fetch metrics
    videos_data: dict = {}
    video_ids = [e["video_id"] for e in video_entries]

    if use_analytics_api:
        # Try analytics for each video; fallback per-video if needed
        fallback_ids = []
        for entry in video_entries:
            vid = entry["video_id"]
            try:
                metrics = fetch_analytics_for_video(yt_analytics, vid, start_date, end_date)
                videos_data[vid] = {
                    "story_key": entry["story_key"],
                    "title": entry["title"],
                    "metrics": metrics,
                    "viral_score": 0.0,
                    "performance_tier": "cold",
                }
                print(f"  ✓  {entry['story_key']} ({vid})")
            except Exception as exc:
                print(f"  ✗  {entry['story_key']} — Analytics failed ({exc}), will use fallback")
                fallback_ids.append(entry)

        if fallback_ids:
            fb_map = fetch_statistics_fallback(yt_data, [e["video_id"] for e in fallback_ids])
            for entry in fallback_ids:
                vid = entry["video_id"]
                videos_data[vid] = {
                    "story_key": entry["story_key"],
                    "title": entry["title"],
                    "metrics": fb_map.get(vid, _empty_metrics()),
                    "viral_score": 0.0,
                    "performance_tier": "cold",
                }
    else:
        # Pure fallback
        fb_map = fetch_statistics_fallback(yt_data, video_ids)
        for entry in video_entries:
            vid = entry["video_id"]
            videos_data[vid] = {
                "story_key": entry["story_key"],
                "title": entry["title"],
                "metrics": fb_map.get(vid, _empty_metrics()),
                "viral_score": 0.0,
                "performance_tier": "cold",
            }

    # Compute viral scores
    max_views = max((v["metrics"]["views"] for v in videos_data.values()), default=1)
    for vid, info in videos_data.items():
        score = compute_viral_score(info["metrics"], max_views=max_views)
        info["viral_score"] = score
        info["performance_tier"] = assign_tier(score)

    # Top performers
    top_performers = sorted(
        [{"video_id": k, "story_key": v["story_key"], "viral_score": v["viral_score"]}
         for k, v in videos_data.items()],
        key=lambda x: x["viral_score"],
        reverse=True,
    )[:5]

    # Channel totals
    channel_totals = compute_channel_totals(videos_data)

    # Recommendations
    recommendations = generate_recommendations(videos_data)

    # Build output
    output = {
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "channel_totals": channel_totals,
        "videos": videos_data,
        "top_performers": top_performers,
        "recommendations": recommendations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding='utf-8') as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)

    print(f"\n[INFO] Analytics cache written → {output_path}")
    print_summary(videos_data, channel_totals, args.days)

    print("\n💡 Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")
    print()


if __name__ == "__main__":
    main()
