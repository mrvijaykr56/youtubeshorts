---
name: youtube-channel-manager
description: >-
  Specialized agentic skill to automate YouTube account management, upload Shorts,
  manage playlists, update video metadata, manage audience/COPPA compliance, API quota hygiene,
  synthetic media disclosures, and sync branding assets via Google YouTube Data API v3 and OAuth tokens.
---

# YouTube Channel & Growth Manager Skill (MagicalTalesKidz)

This skill guides the agent in managing a YouTube channel using Google YouTube Data API v3, managing authentication tokens, automating playlists, and optimizing metadata for maximum viral reach for **@MagicalTalesKidz**.

---

## 1. Authentication & OAuth Scopes 🔐

Persistent credentials are stored in `backend/token.json` and client secrets in `backend/client_secret.json`.

### Required Scopes for Full Account Management:
1. `https://www.googleapis.com/auth/youtube.upload`: Direct video and Shorts uploading.
2. `https://www.googleapis.com/auth/youtube.readonly`: Read channel stats, subscriber count, and video analytics.
3. `https://www.googleapis.com/auth/youtube.force-ssl`: **Full Management** (Required for creating playlists, updating existing video titles/descriptions, modifying privacy status, and posting comments).
4. `https://www.googleapis.com/auth/yt-analytics.readonly`: Optional retention and watch-time analytics reads.

### Authentication Script:
```powershell
python -u backend/scripts/authenticate_youtube.py
```
- Checks `token.json` scopes against required scopes.
- Handles browser callbacks with robust loopback handling on `localhost`.

---

## 2. API Quota & Upload Hygiene ⚙️

The YouTube Data API v3 enforces a default daily quota of **10,000 units/day** (resets at midnight Pacific Time / 13:30 IST):

| Action | Cost | Daily Budget Limit |
|---|---|---|
| **Video Upload (`videos.insert`)** | **1,600 units** | Max 4–5 uploads/day safely |
| **Video Update (`videos.update`)** | **50 units** | 20+ updates |
| **Playlist Insert (`playlistItems.insert`)** | **50 units** | 20+ additions |
| **Comment Insert (`commentThreads.insert`)** | **50 units** | 20+ comments |
| **Read/List Calls (`videos.list`, `channels.list`)** | **1 unit** | Practically unlimited |

### Pre-Upload Hygiene Checklist:
1. Video file exists and is valid 1080x1920 MP4 (<100MB).
2. Title is strictly **≤ 95 characters** (YouTube API rejects ≥ 100 characters).
3. Tags string total length is strictly **≤ 380 characters**.
4. Default language is set to `hi` and default audio language to `hi`.
5. Category ID is set to `1` (Film & Animation).
6. Synthetic media disclosure: if AI animation is photorealistic or depicts real entities, mark the YouTube Studio synthetic content toggle.

---

## 3. Automated Playlist Management 📂

Playlists increase session watch time and drive binge-viewing in the YouTube algorithm:

1. **Check/Create Playlist**:
   - Query existing playlists using `youtube.playlists().list(part="snippet,status", mine=True)`.
   - If not found, insert with `part="snippet,status"`:
     - Title: `Magical Tales Hindi Shorts | हिंदी बाल कहानियाँ (3D Animation)`
     - Privacy: `public`
2. **Add Videos**:
   - Insert video items using `youtube.playlistItems().insert(part="snippet", body={...})`.
   - Check existing items to avoid duplicates.
   - Script reference: [`backend/scripts/manage_channel.py`](file:///d:/WorkSpace/MyVideoWorkspace/backend/scripts/manage_channel.py).
3. **Series-Specific Playlists**:
   - Create sub-playlists for recurring character series (e.g. `चिंटू बंदर की जादुई दुनिया` / `Chintu the Monkey's Adventures`) to encourage binge sessions.

---

## 4. Video Metadata & Viral Optimization 🚀

When optimizing videos for click-through rate (CTR) and search discoverability:

1. **Title Formulation**:
   - `[Emotional Hindi Hook + Emoji] | [Punchy English Subtitle] | [Niche Tags #Shorts]`
   - e.g., `लालिची बंदर को मिली जादुई सीख! 🐒✨ Never Be Greedy | Hindi Kahaniya #Shorts`
2. **Description & Moral Payload**:
   - Include Hindi synopsis, moral lesson (`कहानी की सीख`), 1-click playlist link, and subscribe CTA link (`?sub_confirmation=1`).
3. **Tags**:
   - Inject 12–18 high-volume search tags (`hindi kahaniya`, `moral stories`, `panchatantra stories`, `3d animation`, `bal kahaniya`).

---

## 5. COPPA & Audience Settings Strategy (Unlocking Comments & Bells) 🔔

- **Platform Rule**: Marking videos as strictly "Made for Kids" disables user comments, disables the notification bell, and restricts recommendations.
- **Family-Friendly Solution**: Set `status.selfDeclaredMadeForKids = False` via `youtube.videos().update(part="status", ...)` while keeping stories 100% wholesome, educational, and clean.
- This immediately enables:
  - Viewer comment discussions.
  - Subscriber notification bell alerts.
  - Pinned engagement questions.

---

## 6. Channel Geographic & Vernacular Localization 🌍

YouTube requires clear geographic and linguistic signals to route newly published Shorts into the correct regional recommendation feeds:
1. **Country Code**: `IN` (India). Never leave unassigned.
2. **Default Language**: `hi` (Hindi).
3. **Execution Script**:
   ```powershell
   python backend/scripts/optimize_youtube_channel_branding.py
   ```
4. **Channel Search Keywords (42 Dual-Script Tags)**:
   Injected into `brandingSettings.channel.keywords`:
   ```text
   "Hindi Kahaniya" "Moral Stories in Hindi" "Panchatantra Stories" "Kids Stories in Hindi" "3D Animated Stories" "Hindi Cartoon" "Jadui Kahaniya" "Stories for kids" "Bal Kahaniya" "Bedtime Stories Hindi" "Hindi Fairy Tales" "MagicalTalesKidz" "हिंदी कहानियां" "पंचतंत्र की कहानियां" "बाल कहानियां" "नैतिक कहानियां" "3D कार्टून"
   ```

---

## 7. Anti-Cannibalization Publishing Cadence (The 18:30 IST Rule) ⏱️

Empirical analysis of the October relaunch batch (9 shorts in 3 hours) revealed severe **algorithmic seed starvation**:
- When multiple Shorts are published in rapid succession, YouTube terminates seed distribution on earlier uploads to test the newer ones.
- **Enforced Protocol**:
  - Exactly **1 Short per day**.
  - Published at **18:30 IST (6:30 PM Indian Standard Time)** to capture peak evening co-viewing.
  - Minimum gap between uploads: **12 hours**.

---

## 8. Shorts Retention Benchmarks & Feed Mechanics 📊

To graduate from the initial 50–200 impression seed tier to the 2,000–10,000 Browse/Explore tier, a Short must achieve:
1. **Viewed vs. Swiped-Away**: **> 70%** (Controlled by the first 1.5 seconds: bold Devanagari motion hook + instant visual drama).
2. **Average Percentage Viewed (APV)**: **> 100%** (Requires loopable 28–38s pacing).
3. **Engagement Velocity**: Pinned comments and immediate like/comment signals.

---

## 9. Top 10 Competitor SEO Architecture (Koo Koo TV, Infobells, PunToon Kids) 🏆

Learned from direct API analysis of the top 3 Hindi kids storytelling channels:
- **Infobells Hindi** (72.8M subscribers, 50B+ views)
- **Koo Koo TV Hindi** (4.88M subscribers, 2.5B+ views)
- **PunToon Kids** (3.94M subscribers, 2.8B+ views)

### A. Video Title Architecture (Max 95 Chars)
`[Emotional Hook / Question in Hindi + 1-2 Emojis] [English Story Title] | 3D Hindi Kahaniya #Shorts`
- *Example*: `रोज एक सोने का अंडा! पर लालच ने क्या किया? 🪺✨ Goose of Gold | 3D Hindi Kahaniya #Shorts` (90 chars)
- *Example*: `अचानक ये सियार पूरा नीला कैसे हो गया? 🐺💙 The Blue Jackal | 3D Hindi Kahaniya #Shorts` (87 chars)

### B. Infobells-Style Top-of-Description Hashtag Cloud
```text
#Shorts #HindiKahaniya #MoralStories #Panchatantra #[StoryKeyword] #3DAnimation #HindiCartoon #BalKahani

[2-3 sentence Hindi story hook]

🌟 कहानी की सीख (Moral of the Story):
[Clear, inspiring 1-sentence moral takeaway]

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation
```

### C. 3-Tier Video Tags Architecture (Strictly $\le 380$ Chars)
1. **Tier 1 (Specific Story Tags - 5-7 tags)**: `"golden goose story"`, `"sone ka anda"`, `"lalchi kisan"`, `"the goose of gold"`.
2. **Tier 2 (Competitor Algorithmic Anchor Tags - 8-10 tags)**: `"Hindi Kahaniya"`, `"moral stories in hindi"`, `"panchatantra stories"`, `"kids moral stories"`, `"3d animated stories"`, `"hindi cartoon"`, `"jadui kahaniya"`, `"stories for kids"`, `"shorts"`, `"yt shorts"`.
3. **Tier 3 (Devanagari Dual-Script Tags - 4-5 tags)**: `"हिंदी कहानियां"`, `"पंचतंत्र की कहानियां"`, `"नैतिक कहानियां"`, `"हिंदी कार्टून"`.

---

## 10. Weekly Analytics Review Loop 📈

Every 7 days, review channel KPIs via `backend/scripts/analyze_channel.py`:
- **Average Percentage Viewed (APV)**: Target **> 85%** (Shorts under 35s should target >100%).
- **Viewed vs. Swiped Away**: Target **> 70%**.
- **Click-Through Rate (CTR)**: Target **> 10%**.
- If a Short drops below 60% Viewed, analyze the opening 1.5 seconds (was the hook question clear? Was the camera static?). Iterate on the next video.
