---
name: video-to-video-director
description: >-
  Specialized agentic skill to direct, prompt-engineer, and assemble multi-clip AI video shorts
  (using Google Veo 2, VideoFX, Luma Dream Machine, Kling AI, or Runway Gen-3). Handles 5-clip timeline
  synchronization, zero-error CFR normalization, speed-ramping, 9:16 vertical formatting, 4K/8K mastering,
  dynamic xfade transitions, and synchronized bilingual subtitles in one single pass.
---

# YouTube Shorts & Reels Video-to-Video Director Skill (v2.0 Zero-Error Pipeline)

This skill guides the agent and creator in planning, prompting, inspecting, and assembling multi-clip AI video shorts from modern generative video platforms (Google Veo 2, Google VideoFX, Luma Dream Machine, Kling AI, Runway Gen-3) into broadcast-ready, ultra-high-definition 9:16 vertical videos with **zero errors in one go**.

---

## 1. Zero-Error Pipeline Architecture 🛡️⚙️

AI video generators introduce significant inconsistencies that traditionally crash video rendering pipelines:
- **Audio Clashes & Missing Streams**: Some AI clips have audio tracks; others are completely silent (`-an`).
- **Variable Frame Rate (VFR)**: Generative models output variable frame intervals, causing severe audio-video drift and muxer timestamp crashes.
- **Aspect Ratio & SAR Distortions**: Generative outputs can be 16:9 landscape, 1:1 square, non-standard rectangular (e.g. 720x1280), or have non-square pixel aspect ratios (`SAR != 1:1`).
- **Timestamp Collisions**: Stitching multiple generative clips without strict timecode resetting results in `Non-monotonic DTS` warnings and frozen frames.

### The 6 Deterministic Pillars of the v2.0 Zero-Error Engine:

```
[Raw AI Clips (Veo/Kling/Luma)] 
         │
         ▼
[1. Pre-Flight Health Inspector] ──> Verifies durations, ffprobe decode, non-zero file sizes
         │
         ▼
[2. Geometry & CFR Normalizer]  ──> Center-crops to 9:16, strips audio (-an), enforces constant FPS & yuv420p
         │
         ▼
[3. Monotonic PTS Re-Timing]    ──> Injects setpts=PTS-STARTPTS to guarantee clean clock reset
         │
         ▼
[4. Collision-Guarded Xfade]     ──> Calculates exact floating-point offsets (safe trans <= 35% clip duration)
         │
         ▼
[5. Mastered Podcast Audio Sync] ──> Proportional word-count scene durations + broadcast loudnorm (I=-16, TP=-1.5)
         │
         ▼
[6. Font-Resilient Subtitle Burn]──> Synchronized ASS subtitles with automatic DirectWrite / NirmalaUI font fallback
         │
         ▼
[Master 9:16 Broadcast MP4 (Zero Error in One Go!)]
```

---

## 2. Multi-Clip Story Architecture (5 Scenes $\times$ 8–10s) 🎬

A viral Short or Reel must stay **strictly under 55 seconds** to maximize Average Percentage Viewed (APV >95%):

1. **Scene 1 (0s–4s) — High-Stakes Sensory Hook**:
   - Immediate dynamic action or shocking question. Never start with static scenery.
   - *Example Prompt*: Low-angle camera rushing through glowing mystical ruins as an ancient relic awakens.
2. **Scene 2 (5s–15s) — Deepening Mystery & Discovery**:
   - The protagonist discovers the supernatural rule or miracle.
3. **Scene 3 (16s–28s) — Core Transformation / Climax**:
   - The turning point: sudden multiplication, visual spectacle, or magical escalation.
4. **Scene 4 (29s–42s) — Greed / Threat / Conflict**:
   - Antagonist or high-stakes challenge interferes; dramatic reaction and tension.
5. **Scene 5 (43s–52s) — Resolution, Complete Moral & Loop CTA**:
   - Clean, inspiring moral resolution followed by a high-engagement question.

---

## 3. High-Fidelity Prompt Engineering for Google Veo 2 / Kling / Luma 🎥

To prevent generic outputs or distorted movement, structure every video prompt with 5 physical parameters:

```text
[Framing & Aspect Ratio] + [Camera Motion Vector] + [Subject & Dynamic Physical Action] + [Lighting & Atmospheric Texture] + [Quality & Frame Cadence]
```

### Video Prompt Syntax Checklist:
* **Framing**: Always prefix with `Vertical 9:16 portrait ratio, centered composition`.
* **Camera Movement Vector**: `Cinematic slow dolly-in`, `low-angle heroic tilt-up`, `dynamic orbital 180 sweep`, `crane descent`.
* **Physical Dynamics & Particle Flow**: Explicitly describe fluids, particles, or fabric in motion (`floating golden embers drifting upward`, `shimmering ripples in turquoise water`, `billowing silk kurta in desert wind`).
* **Lighting & Shading**: `Volumetric god rays`, `golden hour sunset rim lighting`, `deep chiaroscuro shadows`, `iridescent bioluminescent glow`.
* **Rendering Style**: `Octane 3D render, Pixar Disney animation aesthetic, photorealistic 8K, 30fps, motion blur`.

### Example 5-Scene Prompt Set:
* **Scene 1**: `Vertical 9:16 portrait ratio. Low-angle dynamic push-in shot of Mohan, a 30yo Indian farmer in ochre kurta, pulling an ancient terracotta clay pot with glowing turquoise runes out of cracked earth. Golden dust particles drifting in sunset backlighting, 3D Pixar animation style, 8K, 30fps.`
* **Scene 2**: `Vertical 9:16 ratio. Medium action eye-level shot. Dozens of glowing iron axes multiply and levitate upwards from the clay pot with sparkling golden particle trails. Mohan gasping in delight, warm amber glow on his face, volumetric lighting.`
* **Scene 3**: `Vertical 9:16 portrait ratio. Macro extreme close-up of the ancient clay pot rim. Overflowing 24K gold coins pouring out onto fresh green grass, glittering golden bokeh, shallow depth of field, Octane 3D render, hyper-detailed.`
* **Scene 4**: `Vertical 9:16 ratio. Dramatic over-the-shoulder shot inside a dark rustic clay hut. A greedy landlord in emerald green silk tumbling headfirst into the oversized glowing pot, turquoise vortex illumination, deep cobalt shadows, cinematic tension.`
* **Scene 5**: `Vertical 9:16 ratio. Wide comical tracking shot at golden sunrise. Dozens of identical miniature greedy landlords running in hilarious panic across a village square while Mohan smiles peacefully beside happy villagers. 3D Pixar animation, vibrant colors, 8K.`

---

## 4. Execution & Assembly Workflow 🚀

### Step 1: Pre-Flight Verification & Dry Run
Before initiating full rendering, verify that all input clips decode properly and timestamps align:

```powershell
python backend\scripts\assemble_video_short.py `
    --job_dir "backend/output/my_short_01" `
    --dry_run
```
* Reports clip durations, resolutions, frame rates, and pixel formats.
* Flags corrupted or mismatched clips before any processing time is spent.

### Step 2: Full Master 9:16 Assembly
Run the assembly pipeline to produce the master broadcast video in a single pass:

```powershell
python backend\scripts\assemble_video_short.py `
    --job_dir "backend/output/my_short_01" `
    --resolution 1080p `
    --voice hi_female `
    --caption_style tiktok `
    --caption_lang English `
    --music none `
    --transition dynamic `
    --mode speed_ramp `
    --fps 30
```

### CLI Parameters:
* `--job_dir`: Directory containing `clip_1.mp4 ... clip_5.mp4` and `script.json`.
* `--resolution`: `1080p` (Full HD), `4k` (Ultra HD, 2160x3840), or `8k` (4320x7680).
* `--voice`: `hi_female` (Swara - Recommended), `hi_male` (Madhur), `in_female` (Neerja), `in_male` (Prabhat).
* `--caption_style`: `tiktok` (kinetic word-by-word highlight), `elegant`, or `karaoke`.
* `--caption_lang`: `English` (for bilingual Hindi voice + English subtitles) or `Hindi`.
* `--mode`:
  * `speed_ramp` (Default & Recommended): Smoothly scales playback speed so 100% of the clip action is seen without sudden cuts.
  * `trim`: Trims excess length to exact narration duration.
* `--transition`: `dynamic` (smooth rotation through fade, slideleft, fadeblack, circlecrop), `dissolve`, or `none`.
* `--fps`: Target constant frame rate (`30` standard, `60` for ultra-smooth action).
* `--music`: `none` (default for pure dialogue intelligibility) or `lofi`/`upbeat` (auto-ducked BGM).

---

## 5. Output Deliverables & Quality Gates 📦

Every completed assembly produces:
1. **`final_master_video.mp4`**: 1080x1920 / 4K broadcast video with burned kinetic subtitles, zero scrubber bar, and mastered audio.
2. **`thumbnail.jpg`**: High-resolution 9:16 poster frame auto-extracted at $t = 1.0\text{s}$.
3. **`captions.ass`**: Synchronized subtitle file formatted with safe lower-third margins (`MarginV=240`).
4. **`narration.mp3`**: Mastered vocal track with broadcast loudness compliance (`I=-16, TP=-1.5, LRA=11`).

---

## 6. Zero-Error Troubleshooting Matrix 🛠️

| Symptom | Root Cause | Automated Engine Fix |
| :--- | :--- | :--- |
| **Non-monotonic DTS warnings** | Frame rate jitter or unreset PTS across transitions | Normalized via `setpts=PTS-STARTPTS`, `fps=30`, and `-fps_mode cfr`. |
| **Subtitle text overlaps video controls** | Subtitle bottom margin too low | Enforces `MarginV=240` (lower-third safe zone for Shorts/Reels). |
| **Black bars on sides (Letterboxing)** | Clip was generated in 16:9 or square | Normalized via `scale=...:force_original_aspect_ratio=increase,crop=...` to guarantee 100% full-frame vertical coverage. |
| **Audio-video drift at end of video** | VFR drift or audio padding shortfall | Engine appends `apad=pad_dur=1.5` and trims audio to exact video timeline. |
| **Subtitles fail to render on Windows** | Font provider missing requested font | Subtitle engine dynamically falls back from `Montserrat` to `Arial-BoldMT` and `NirmalaUI-Bold`. |
