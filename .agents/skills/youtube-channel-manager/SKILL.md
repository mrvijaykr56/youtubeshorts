---
name: youtube-channel-manager
description: >-
  Specialized agentic skill to automate YouTube account management, upload Shorts,
  manage playlists, update video metadata, unlock COPPA restrictions for community growth,
  and sync branding assets via Google YouTube Data API v3 and OAuth tokens.
---

# YouTube Channel & Growth Manager Skill

This skill guides the agent in managing a YouTube channel using Google YouTube Data API v3, managing authentication tokens, automating playlists, and optimizing metadata for maximum viral reach.

---

## 1. Authentication & OAuth Scopes 🔐

Persistent credentials are stored in `backend/token.json` and client secrets in `backend/client_secret.json`.

### Required Scopes for Full Account Management:
1. `https://www.googleapis.com/auth/youtube.upload`: Direct video and Shorts uploading.
2. `https://www.googleapis.com/auth/youtube.readonly`: Read channel stats, subscriber count, and video analytics.
3. `https://www.googleapis.com/auth/youtube.force-ssl`: **Full Management** (Required for creating playlists, updating existing video titles/descriptions, modifying privacy status, and posting comments).

### Authentication Script:
```powershell
.\backend\venv\Scripts\python.exe -u backend\scripts\authenticate_youtube.py
```
- Checks `token.json` scopes against required scopes.
- Handles browser callbacks with robust loopback handling on `localhost`.

---

## 2. Automated Playlist Management 📂

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

---

## 3. Video Metadata & Viral Optimization 🚀

When optimizing videos for click-through rate (CTR) and search discoverability:

1. **Title Formulation**:
   - `[Emotional Hindi Hook + Emoji] | [Punchy English Subtitle] | [Niche Tags #Shorts]`
   - e.g., `लालिची बंदर को मिली जादुई सीख! 🐒✨ Never Be Greedy | Hindi Kahaniya #Shorts`
2. **Description & Moral Payload**:
   - Include Hindi synopsis, moral lesson (`कहानी की सीख`), 1-click playlist link, and subscribe CTA link (`?sub_confirmation=1`).
3. **Tags**:
   - Inject 10–15 high-volume search tags (`hindi kahaniya`, `moral stories`, `panchatantra stories`, `3d animation`).

---

## 4. COPPA & Audience Settings Strategy (Unlocking Comments & Bells) 🔔

- **Platform Rule**: Marking videos as strictly "Made for Kids" disables user comments, disables the notification bell, and restricts recommendations.
- **Family-Friendly Solution**: Set `status.selfDeclaredMadeForKids = False` via `youtube.videos().update(part="status", ...)` while keeping stories 100% wholesome, educational, and clean.
- This immediately enables:
  - Viewer comment discussions.
  - Subscriber notification bell alerts.
  - Pinned engagement questions.

---

## 5. Automated Channel Branding Updates 🎨

YouTube Data API v3 supports updating channel branding directly:

1. **Channel Banner Upload**:
   - Upload 2560x1440 JPEG using `youtube.channelBanners().insert(media_body=media)`.
   - Capture returned CDN URL (`https://yt3.googleusercontent.com/...`).
   - Attach to channel via `youtube.channels().update(part="brandingSettings", body={"id": CHANNEL_ID, "brandingSettings": {"image": {"bannerExternalUrl": banner_url}, "channel": {"title": "..."}}})`.
2. **Channel Description & Keywords**:
   - Injected into `brandingSettings.channel.description` and `brandingSettings.channel.keywords`.
3. **Channel Avatar / Profile Picture**:
   - Generated as 1024x1024 3D mascot image.
   - User uploads in 1 click at [YouTube Studio Customization](https://studio.youtube.com/channel/UCL3Xsads7oyNr70erqz8vPQ/editing/images).

---

## 6. Community Tab Posts & Polls 📊

- **Google API Constraint**: YouTube Data API v3 does NOT have public endpoints for creating Community Tab posts or polls.
- **Workflow**:
  - Agent prepares 4 square 1:1 character cards in `backend/output/community_poll_assets/`.
  - Agent prepares viral Hindi/English poll copy.
  - User posts via 1-click link to [YouTube Studio Community](https://studio.youtube.com/channel/UCL3Xsads7oyNr70erqz8vPQ/posts).

---

## 7. Top 10 Competitor SEO Architecture (Koo Koo TV, Infobells, PunToon Kids) 🏆

Learned from direct API analysis of the top 3 Hindi kids storytelling channels:
- **Infobells Hindi** (72.8M subscribers, 50B+ views)
- **Koo Koo TV Hindi** (4.88M subscribers, 2.5B+ views)
- **PunToon Kids** (3.94M subscribers, 2.8B+ views)

### A. Channel-Level Keyword Cloud Formula
Inject into `brandingSettings.channel.keywords` (space-separated, multi-word terms enclosed in double quotes):
```text
"Hindi Kahaniya" "Moral Stories in Hindi" "Panchatantra Stories" "Kids Stories" "Hindi Cartoon" "Jadui Kahaniya" "Stories for kids" "Infobells Hindi" "Koo Koo TV" "PunToon Kids" "Bal Kahaniya" "Hindi Fairy Tales" "Bedtime Stories" "3D Animated Stories" "Hindi Stories for Kids" "MagicalTalesKidz" "हिंदी कहानियां" "पंचतंत्र की कहानियां" "बाल कहानियां" "नैतिक कहानियां"
```
> [!IMPORTANT]
> **API Constraint**: Always isolate writable properties when updating `brandingSettings`. Never pass read-only fields like `image.bannerExternalUrl`. Keep the keywords string $\le 400$ characters to avoid HTTP 400 `badRequest`.

### B. Video Title Architecture (Max 95 Chars)
YouTube enforces a strict 100-character ceiling for video titles. Any title $\ge 100$ characters is rejected with `invalidTitle`.
**Top 10 Formula**:
`[Emotional Hook / Question in Hindi + 1-2 Emojis] [English Story Title] | 3D Hindi Kahaniya #Shorts`
- *Example*: `रोज एक सोने का अंडा! पर लालच ने क्या किया? 🪺✨ Goose of Gold | 3D Hindi Kahaniya #Shorts` (90 chars)
- *Example*: `अचानक ये सियार पूरा नीला कैसे हो गया? 🐺💙 The Blue Jackal | 3D Hindi Kahaniya #Shorts` (87 chars)

### C. Infobells-Style Top-of-Description Hashtag Cloud
Infobells always places 5–8 high-velocity hashtags at the very first line of the description. This enables YouTube Shorts feed classification within seconds of publication:
```text
#Shorts #HindiKahaniya #MoralStories #Panchatantra #GoldenGoose #SoneKaAnda #3DAnimation #HindiCartoon #BalKahani

[2-3 sentence Hindi story hook]

🌟 कहानी की सीख (Moral of the Story):
[Clear, inspiring 1-sentence moral takeaway]

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #3DAnimation
```

### D. 3-Tier Video Tags Architecture (Strictly $\le 380$ Chars)
YouTube returns `invalidTags` (HTTP 400) if the comma-joined tags exceed 400–500 characters. Always use the 3-Tier Tag Assembly:
1. **Tier 1 (Specific Story Tags - 5-7 tags)**: `"golden goose story"`, `"sone ka anda"`, `"lalchi kisan"`, `"the goose of gold"`, `"lalach buri bala hai"`.
2. **Tier 2 (Competitor Algorithmic Anchor Tags - 8-10 tags)**: `"Hindi Kahaniya"`, `"moral stories in hindi"`, `"panchatantra stories"`, `"kids moral stories"`, `"3d animated stories"`, `"hindi cartoon"`, `"jadui kahaniya"`, `"stories for kids"`, `"shorts"`, `"yt shorts"`.
3. **Tier 3 (Devanagari Dual-Script Tags - 4-5 tags)**: `"हिंदी कहानियां"`, `"पंचतंत्र की कहानियां"`, `"नैतिक कहानियां"`, `"हिंदी कार्टून"`.
- Total tags: 18–22 tags. Total length: strictly $\le 380$ characters.

### E. Algorithm & Audience Compliance
- **Category ID**: `1` (Film & Animation) — Highest CPM and recommendation velocity for animated stories.
- **COPPA Status**: `selfDeclaredMadeForKids = False` — Unlocks viewer comments, notification bell alerts, and community tab interactions.
- **Binge Playlist Sync**: Every video must be added to the official channel playlist (`PLJE6ifX-QD0A`) upon upload to trigger YouTube's auto-play session watch-time boost.
- **Instant Pinned Discussion Comment**: Immediately post an engagement magnet comment via `youtube.commentThreads().insert` containing the curiosity question + official playlist link + `?sub_confirmation=1` link to trigger algorithmic discussion velocity.

---

## 8. Catalog Synchronization & Upload Ledger 🗂️

All published videos must be logged in `backend/uploads_tracker.json` and synchronized with the official playlist:
- `vPdF1JQcZz8`: *The Magic Pot (जादुई मटका)* (Oct 24, 2026) - **Latest**
- `yQQlvP0MtG8`: *The Clever Crow (बुद्धिमान कौवा)* (Oct 23, 2026)
- `RQsyj6r_980`: *Goose of Gold (सोने का अंडा)* (Oct 22, 2026)
- `1d8fNhpscXY`: *The Blue Jackal (नीला सियार)* (Oct 22, 2026)
- `Wio6lrQKrjA`: *Honest Woodcutter (ईमानदार लकड़हारा)* (Oct 22, 2026)
- `wsaNFDsKSM8`: *Monkey & Crocodile (बंदर और मगरमच्छ)* (Oct 22, 2026)
- `HEVzgJuGzyE`: *The Clever Rabbit (चतुर खरगोश)* (Oct 21, 2026)
- `WNNNbeNU_o4`: *The Mouse & Lion (शेर और चूहा)* (Oct 21, 2026)
- Total Catalog: 18 Videos active, 100% categorized in Category 1, COPPA unlocked.

