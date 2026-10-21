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
   - Script reference: [`backend/scripts/manage_channel.py`](file:///d:/WorkSpace/YTShorts/backend/scripts/manage_channel.py).

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
