---
name: video-to-video-director
description: >-
  Specialized agentic skill to direct, prompt-engineer, and assemble multi-clip AI video shorts
  (using Google Veo, VideoFX, Luma, Kling, or Gemini Pro storyboards). Handles 5-clip timeline
  synchronization, speed-ramping, 9:16 vertical formatting, 4K/8K mastering, and seamless transitions.
---

# YouTube Shorts & Reels Video-to-Video Director Skill

This skill guides the agent and creator in planning, prompting, and assembling multi-clip AI video shorts from generative video models (Google Veo, Google VideoFX, Luma Dream Machine, Kling AI, etc.) into broadcast-ready, ultra-high-definition 9:16 vertical videos.

---

## 1. Multi-Clip Architecture (5 Scenes $\times$ 10s) 🎬

A viral Short or Reel must stay **strictly under 58 seconds**.
The 5-scene formula provides the optimal retention pacing:

1. **Scene 1 (0s–3s)**: High-Stakes Visual Hook (rapid motion, dramatic reveal, dynamic camera pull).
2. **Scene 2 (4s–15s)**: Context & Deepening Mystery (subject in action, atmospheric world-building).
3. **Scene 3 (16s–30s)**: Core Climax / Pivot (turning point, dramatic visual reaction or phenomenon).
4. **Scene 4 (31s–45s)**: Shocking Discovery / Secret (unveiling the core revelation).
5. **Scene 5 (46s–55s)**: High-Engagement Question + Call-to-Action ("What would you do? Subscribe for more!").

---

## 2. Prompt Engineering for Google Veo / VideoFX / Video AI 🎥

When writing video prompts for each scene, include:
* **Camera Movement**: `slow cinematic dolly in`, `orbital sweep 360`, `low-angle tilt-up`, `drone descent`.
* **Framing**: `Vertical 9:16 ratio`, `close-up shot`, `wide establishing shot`.
* **Motion & Physics**: Explicitly describe *movement* (`flowing fabric`, `glowing bioluminescent particles drifting`, `wind blowing hair`, `water ripples`).
* **Lighting & Atmosphere**: `cinematic volumetric lighting`, `35mm anamorphic lens`, `hyper-realistic textures`.

### Example Scene Prompt for Google Veo / VideoFX:
```text
Vertical 9:16 ratio. Cinematic drone descent into an ancient neon-lit bioluminescent ocean trench.
Giant glowing crystal formations pulse with electric blue energy. Small schools of iridescent fish dart
past the camera with realistic fluid dynamics. Photorealistic 8K, volumetric lighting, motion blur, 24fps.
```

---

## 3. Assembling Clips with the Backend Engine 🚀

Once the 5 video clips are generated (e.g., `clip_1.mp4` to `clip_5.mp4`):

```powershell
.\backend\venv\Scripts\python.exe backend\scripts\assemble_video_short.py `
    --job_dir "backend/output/my_short_01" `
    --resolution 4k `
    --voice in_female `
    --caption_style tiktok `
    --music lofi `
    --transition dynamic `
    --mode speed_ramp
```

### Parameters:
* `--resolution`: `1080p`, `4k` (default), or `8k` (Ultra HD).
* `--mode`:
  * `speed_ramp` (recommended): Rescales playback speed so the entire clip action matches narration without abrupt cuts.
  * `trim`: Trims excess length to exact narration duration.
* `--transition`: `dynamic`, `dissolve`, `whip_pan`, `flash`, or `none`.
* `--voice`: `in_female`, `in_male`, `hi_male`, `hi_female`, etc.
* `--music`: `none`, `lofi`, `upbeat`.
