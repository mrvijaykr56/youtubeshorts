# 📖 Magical Tales Kidz — Commands & Architecture Cheat Sheet

This document is the definitive operational guide for managing video production, YouTube Channel growth, and Instagram Reels marketing for **@MagicalTalesKidz** / **@magicaltaleskid**.

---

## 📂 1. Directory Structure Map

```text
YTShorts/
├── .agents/skills/                   # Specialized AI Agent Skills
│   ├── shorts-script-polisher/       # Scripting, hooks, validation, metadata
│   ├── shorts-image-director/        # 9:16 Imagen 3 visual prompt direction
│   ├── youtube-channel-manager/      # YouTube API v3, playlists, competitor SEO
│   └── instagram-reels-manager/      # Instagram Reels SEO, packaging, uploading
├── backend/
│   ├── app.py                        # Flask Web API Server (Port 5000)
│   ├── brand_config.json             # Channel & Instagram branding definitions
│   ├── token.json                    # YouTube OAuth2 persistent credentials
│   ├── instagram_session.json        # Instagram verified session cookies (gitignored)
│   ├── client_secret.json            # Google Cloud OAuth App credentials
│   ├── output/                       # Produced 3D Shorts & packaged media
│   │   ├── [story_name]/             # Video, audio, scenes, subtitles
│   │   ├── instagram_reels_packages/ # 1080x1920 MP4, cover, caption.txt
│   │   └── community_poll_assets/    # 600x600 cropped community character cards
│   └── scripts/                      # Core engines & Master suites
│       ├── legacy_uploads/           # Archived one-off upload scripts (Shorts 1-13)
│       └── archive/                  # Archived superseded fix scripts
├── frontend/                         # Web UI (React / Vite)
└── tests/                            # Test scripts & pipelines
```

---

## 🎬 2. YouTube Operations Suite

Run all commands from the workspace root (`d:\WorkSpace\YTShorts`) using the backend virtual environment:

### A. Channel Telemetry & Competitor Analysis
```powershell
# Analyze @MagicalTalesKidz live stats & recent uploads
.\backend\venv\Scripts\python.exe backend\scripts\analyze_channel.py

# Reverse-engineer top competitors (Koo Koo TV, Infobells, PunToon Kids)
.\backend\venv\Scripts\python.exe backend\scripts\analyze_competitors.py
```

### B. Master SEO & Channel-Wide Upgrade
```powershell
# Injects dual-script channel keywords, sets 3-tier safe tags (<=380 chars),
# applies Infobells-style top hashtags, sets Category 1, and syncs playlist:
.\backend\venv\Scripts\python.exe backend\scripts\optimize_channel_and_all_videos_seo.py
```

### C. Playlist & Audience Management
```powershell
# Sync official playlist (PLJE6ifX-QD0A) and check COPPA settings:
.\backend\venv\Scripts\python.exe backend\scripts\manage_channel.py
```

### D. Storyboard Pre-Flight Validation
```powershell
# Validate scene count (5-8), word count (45-130), pacing, and ban comparison endings:
.\backend\venv\Scripts\python.exe backend\scripts\storyboard_validator.py --json "backend/output/[story_name]/script.json"
```

---

## 📱 3. Instagram Reels Suite (@magicaltaleskid)

### A. Profile & Reel Analytics
```powershell
# Inspect follower count, bio, plays, likes, and engagement:
.\backend\venv\Scripts\python.exe backend\scripts\analyze_instagram_account.py
```

### B. Package Reels for Instagram
```powershell
# Prepares 1080x1920 MP4 (with audio verification), cover thumbnail, and caption.txt:
.\backend\venv\Scripts\python.exe backend\scripts\prepare_instagram_reels.py
```

### C. Automated Reel Uploading (`instagrapi`)
```powershell
# List all packaged reels ready to publish:
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --list

# Upload a specific story reel (e.g. golden_goose, blue_jackal):
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --story blue_jackal

# Batch upload all packaged reels with 30s rate-limit pacing:
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --story all

# Verify or refresh saved Instagram session:
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --login
```

### D. Master Reels SEO & Caption Optimization
```powershell
# Upgrades all live Instagram reels with viral hooks, high-save CTAs, and 12-tag clusters:
.\backend\venv\Scripts\python.exe backend\scripts\optimize_all_instagram_reels_seo.py
```

---

## 🚀 4. Full Production Pipeline for New Shorts (e.g. Short #14)

1. **Draft & Polish**: Formulate 5–8 scene storyboard in Hindi using `shorts-script-polisher` skill.
2. **Pre-Flight Check**: Pass `storyboard_validator.py` with 0 blocking errors.
3. **User Approval**: Present storyboard and obtain user confirmation.
4. **Generate Visuals**: Batch generate 9:16 Imagen 3 scenes with character visual consistency.
5. **Assemble & Render**: Combine with Swara Hindi voiceover, dynamic ASS karaoke subtitles into 1080x1920 MP4.
6. **Publish to YouTube**: Upload via `youtube_uploader.py` or API with 3-tier tags and Category 1.
7. **Package & Publish to Instagram**: Run `prepare_instagram_reels.py` followed by `upload_instagram_reel.py`.
