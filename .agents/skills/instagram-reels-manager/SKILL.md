---
name: instagram-reels-manager
description: >-
  Specialized agentic skill to manage Instagram Reels marketing, cross-post 9:16 vertical animations from YouTube Shorts, optimize Instagram search & explore SEO, engineer high-save captions, and drive profile traffic to YouTube.
---

# Instagram Reels Manager & Viral Cross-Posting Skill 📱✨

This skill orchestrates the multi-platform expansion of **Magical Tales Kidz** across Instagram Reels ([@magicaltaleskid](https://www.instagram.com/magicaltaleskid/)). It ensures that every 3D animated Short produced for YouTube is seamlessly adapted, packaged, and optimized for maximum organic reach and explore page visibility on Instagram.

---

## 1. Instagram Reels Algorithm Mechanics 🧠

Instagram Reels uses a distinct recommendation engine compared to YouTube Shorts:
1. **Watch Time & Completion Rate**: Watching the video to completion signals quality.
2. **Saves & Shares > Likes**: The algorithm weights **Shares** (DM sends to friends/parents) and **Saves** (bookmarking moral stories for kids) 5x higher than passive likes.
3. **First 125 Characters (Above the Fold)**: Instagram captions truncate at ~125 characters. The hook question and topic must be completely visible before the viewer clicks "...more".
4. **Keyword Search Indexing**: Instagram indexes the entire caption text, not just hashtags. Using natural phrases like `"Hindi Kahaniya"`, `"Panchatantra Stories"`, and `"Bal Kahani"` in the text directly ranks the Reel in Instagram Explore Search.

---

## 2. Technical Specifications & Quality Assurance 📐

Every reel published to `@magicaltaleskid` MUST adhere to these technical standards:
- **Aspect Ratio**: 9:16 vertical (1080x1920 pixels).
- **Duration**: 30 to 55 seconds (ideal for retention loops).
- **Codec**: H.264 video, AAC audio at 48kHz stereo.
- **Safe Margins**:
  - Keep important visual focus (character faces, main action) inside the central 1080x1350 area.
  - Subtitles must be centered with a safe bottom margin of 280–320px so Instagram's caption overlay and audio attribution don't obscure them.
- **Cover Photo (Thumbnail)**: 9:16 high-contrast frame with bold emotional expression.

---

## 3. High-Conversion Instagram Caption Architecture ✍️

Every Instagram Reel caption must follow this proven high-engagement structure:

```text
[Line 1-2 Hook Question / Curiosity Trigger with Emojis] 🪺✨
(Must be under 120 characters so it fits before the "...more" fold)

[2-3 sentence Hindi story summary highlighting the drama or conflict]

🌟 कहानी की सीख (Moral of the Story):
[Inspiring 1-sentence moral takeaway]

💬 [Discussion / Engagement Trigger]:
क्या आपने भी कभी ऐसी सीख अनुभव की है? हमें Comments में ज़रूर बताएं! 👇

👉 अपने बच्चों और दोस्तों के साथ यह जादुई कहानी ज़रूर SHARE और SAVE करें! ❤️
🎬 पूरी 3D कहानी और नए एपिसोड्स देखने के लिए BIO में दिए गए YouTube लिंक पर क्लिक करें! 🔔
Follow @magicaltaleskid for daily 3D Hindi moral stories! ✨

#HindiReels #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation #HindiStories #ReelsIndia #PanchatantraTales #3DAnimation #ReelsInstagram #ExplorePage #MagicalTalesKidz
```

---

## 4. Curated Instagram Hashtag Matrix 🏷️

Instagram ranks posts best with **8 to 12 hyper-relevant hashtags**. Never spam 30 irrelevant tags.

### Standard 10-Hashtag Cluster:
1. **Core Genre**: `#HindiKahaniya #MoralStories #Panchatantra`
2. **Niche & Audience**: `#KidsAnimation #HindiStories #BalKahaniya`
3. **Format & Distribution**: `#HindiReels #ReelsIndia #ExplorePage`
4. **Brand Anchor**: `#MagicalTalesKidz #magicaltaleskid`

---

## 5. Funneling Instagram Reach to YouTube Growth 🚀

Instagram is a prime discovery channel to drive high-retention subscribers to YouTube:
1. **Instagram Bio Optimization**:
   - Bio Text:
     ```text
     ✨ 3D Pixar-Style Hindi Moral Stories for Kids & Family 🌟
     📚 पंचतंत्र और जादुई बाल कहानियां
     🎬 Watch Full Episodes & Daily Shorts on YouTube 👇
     ```
   - Bio Link: `https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1`
2. **Pinned Comment on Every Reel**:
   Pin the first comment with the direct episode and playlist link:
   > *"🎬 इस कहानी का पूरा 3D अनुभव हमारे YouTube चैनल पर देखें! Link bio में उपलब्ध है 👉 @magicaltaleskid ✨"*

---

## 6. Automated Reel Packaging & Upload Workflow 📦

### A. Packaging Reels
Run [`backend/scripts/prepare_instagram_reels.py`](file:///d:/WorkSpace/MyVideoWorkspace/backend/scripts/prepare_instagram_reels.py) to package any ready Short:
- Copies the final MP4 to `backend/output/instagram_reels_packages/[video_id]/`.
- Generates high-res 1080x1920 cover photo thumbnail.
- Creates `caption.txt` containing the pre-formatted hook, story, moral, engagement CTA, and hashtag cloud.

### B. Automated Uploading via Python (`instagrapi`)
Run [`backend/scripts/upload_instagram_reel.py`](file:///d:/WorkSpace/MyVideoWorkspace/backend/scripts/upload_instagram_reel.py) to publish directly to [@magicaltaleskid](https://www.instagram.com/magicaltaleskid/):

```powershell
# 1. List all ready reels
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --list

# 2. Upload a specific story reel
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --story golden_goose

# 3. Batch upload all packaged reels
.\backend\venv\Scripts\python.exe backend\scripts\upload_instagram_reel.py --story all
```

- **Session Persistence**: Saves login token to `backend/instagram_session.json` (gitignored) so you only need to authenticate once.
- **2FA & Challenges**: Prompts for SMS/Authenticator code if 2FA is active.
- **Auto-Traffic Funnel**: Automatically posts a first comment on the Reel pointing viewers to the YouTube link in bio.
