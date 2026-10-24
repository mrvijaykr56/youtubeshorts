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

## 2. End-to-End 7-Step Production Lifecycle (The "Magic Millstone" Standard) 🔄🎬

This is the exact, battle-tested operational sequence executed to produce high-retention AI Video Shorts with zero errors in one single run:

```
[Step 1: Story & Script Calibration] ──> 100-115 words, 5 scenes, validator pre-flight (0 errors)
                 │
                 ▼
[Step 2: Reference Image Generation] ──> 9:16 Pixar 3D master + Visual Reference Chaining (ImagePaths)
                 │
                 ▼
[Step 3: 4-Layer Video Prompting]    ──> Camera Vector + Rigid Anatomy Guard + Gravity Dynamics + 30fps
                 │
                 ▼
[Step 4: AI Video Clip Drop-In]      ──> Veo 2 / Kling 1.5 (clip_1.mp4 ... clip_5.mp4)
                 │
                 ▼
[Step 5: Pre-Flight Clip Dry Run]    ──> assemble_video_short.py --dry_run (verifies decode & CFR)
                 │
                 ▼
[Step 6: Master Broadcast Assembly]  ──> Speed-ramp sync + Swara TTS + CFR 30 + xfade + ASS captions
                 │
                 ▼
[Step 7: Dual-Platform Publishing]   ──> YouTube Shorts + Instagram Reels + Pinned Comment Magnet
```

### Detailed Operational Steps:

#### Step 1: Story Selection & Script Calibration (100–115 Words)
* Select priority story from the 3 Golden Clusters in `story_roadmap.md` (e.g., Cluster 1: Relic Multiplication).
* Draft 5-scene JSON with `character_anchor`, `world_anchor`, 0–3s sensory hook, moral takeaway, and pinned engagement question.
* Run pre-flight validator:
  ```powershell
  python -u backend/scripts/storyboard_validator.py --json "backend/output/<story_dir>/storyboard.json"
  ```
* **Hard Gate**: Must achieve `STATUS: ✅ PASSED VALIDATION` (0 blocking errors, word count strictly 100–115 words / ~45s–52s).

#### Step 2: Reference Image Generation (Character & World Anchor)
* Generate `scene_1.jpg` in 9:16 vertical ratio using Antigravity's `generate_image` (defines 3D Pixar character age, clothing, eyes, and environment).
* For Scenes 2–5, use **Visual Reference Chaining** (`ImagePaths: ["<path_to_scene_1.jpg>"]`) to condition the diffusion latent space, locking character identity and relic texture across all 5 scenes.
* Save as `scene_1.jpg` through `scene_5.jpg` in `backend/output/<story_dir>/`.

#### Step 3: Ultra-Precision 4-Layer Prompt Engineering (I2V Mode)
* Formulate 4-layer prompts for Google Veo 2 / Kling 1.5 / Luma Dream Machine:
  * `Layer 1: Camera Vector & Speed Modulation` (e.g., slow forward dolly-in with gimbal stabilization).
  * `Layer 2: Rigid Body & Material Guards` (e.g., character facial features and stone millstone maintain rigid geometry without morphing, zero melting).
  * `Layer 3: Gravity & Fluid Dynamics` (e.g., realistic gravity simulation for cascading sweets, streaming coins, pouring salt).
  * `Layer 4: Engine Style & FPS Lock` (e.g., 3D Pixar aesthetic, 30fps, 8K resolution, natural motion blur).
* Define tool-specific motion sliders (Camera Intensity 2/10 to 4/10, Motion Brush targets).

#### Step 4: AI Video Clip Generation & Drop-In
* Attach `scene_1.jpg` to `scene_5.jpg` as the starting frame in the AI video tool.
* Apply the 4-layer prompt and motion brush.
* Download and place the 5 rendered MP4s into `backend/output/<story_dir>/` as:
  `clip_1.mp4`, `clip_2.mp4`, `clip_3.mp4`, `clip_4.mp4`, `clip_5.mp4`.

#### Step 5: Pre-Flight Health Inspection & Dry Run
* Run the inspection tool to verify decode health, durations, resolutions, and pixel formats before processing:
  ```powershell
  python -u backend/scripts/assemble_video_short.py --job_dir "backend/output/<story_dir>" --dry_run
  ```
* Flags corrupted clips or mismatched aspect ratios.

#### Step 6: Master Broadcast Assembly (Single-Pass 0-Error Render)
* Execute the master assembly command:
  ```powershell
  python -u backend/scripts/assemble_video_short.py `
      --job_dir "backend/output/<story_dir>" `
      --resolution 1080p `
      --voice hi_female `
      --caption_style tiktok `
      --caption_lang English `
      --music none `
      --transition dynamic `
      --mode speed_ramp `
      --fps 30
  ```
* **Automated Engine Tasks Performed**:
  1. Hindi Swara Neural TTS with broadcast loudness compliance (`I=-16, TP=-1.5`).
  2. Proportional scene duration calculation based on spoken word counts + 1.5s outro CTA loop padding.
  3. Center-crop to 9:16 vertical full frame, audio stripping (`-an`), CFR 30fps lock.
  4. Monotonic PTS clock reset (`setpts=PTS-STARTPTS`) preventing xfade DTS desync.
  5. Optical xfade transitions with synchronized whoosh SFX.
  6. Kinetic ASS word-by-word highlighted subtitles with DirectWrite font fallback.
  7. High-res 9:16 poster thumbnail auto-extraction at $t = 1.0\text{s}$ (`thumbnail.jpg`).

#### Step 7: Dual-Platform Publishing & Community Growth
* Publish to YouTube Shorts and Instagram Reels using our automated scripts.
* Attach to official playlist (`PLJE6ifX-QD0A`), enforce Category 1 (Film & Animation), set `selfDeclaredMadeForKids = false`, and immediately post the high-engagement pinned comment.

---

## 3. Multi-Clip Story Architecture (5 Scenes $\times$ 8–10s) 🎬

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

## 3. Mandatory Ultra-Precision Video Prompt Protocol (Image-to-Video Mode) 🎥🛡️

> [!CRITICAL]
> **Why Short 1-Sentence Prompts Cause AI Video Failures**:
> In Image-to-Video (I2V) mode (Google Veo 2, Kling 1.5, Luma Dream Machine, Runway Gen-3), the starting image supplies the initial latent geometry. Short or vague text prompts force the generative diffusion model to guess physical rigidity, leading to 3 catastrophic errors:
> 1. **Rubber Warping / Morphing**: Rigid stone, metal, or wooden objects bend, flex, or melt like rubber.
> 2. **Character Anatomy Distortion**: Fast or unconstrained camera motion tears, morphs, or stretches faces and fingers.
> 3. **Static Freeze**: Fluid elements (cascading sweets, silver coins, pouring salt, steam) remain frozen or float sideways like smoke without realistic gravity.

---

### The 4-Layer Studio Prompt Architecture:
Every single video prompt generated in this workspace MUST follow this 4-layer structure:

```text
[Layer 1: Camera Vector & Speed] + [Layer 2: Rigid Anatomy & Material Guards] + [Layer 3: Gravity & Fluid Dynamics] + [Layer 4: Engine Style & FPS Lock]
```

1. **Layer 1: Camera Movement Vector & Speed Modulation**:
   - Explicitly define camera trajectory and physical stabilization.
   - *Syntax*: `Slow cinematic forward dolly-in with smooth gimbal stabilization`, `Macro 45-degree slow orbital camera pan`, `Cinematic wide overhead crane shot slowly rising upward`.
2. **Layer 2: Rigid Body Anatomy & Material Preservation Guards**:
   - Explicitly instruct the diffusion model to preserve geometry and prevent morphing.
   - *Syntax*: `[Character] maintains rigid, anatomically consistent facial features and body geometry without morphing or warping`, `[Object] maintains solid rigid structure while spinning smoothly`, `zero face distortion, rigid stone/wood geometry, no melting`.
3. **Layer 3: Realistic Gravity-Driven Fluid & Particle Dynamics**:
   - Explicitly dictate directional gravity, fluid viscosity, and realistic particle motion.
   - *Syntax*: `Steaming hot golden sweets cascade downward under realistic gravity simulation, tumbling and settling onto the shining brass plate with curling wisps of white volumetric steam`, `A steady, shimmering waterfall of heavy solid silver coins streams continuously out, cascading downward under gravity with metallic clinking dynamics`.
4. **Layer 4: Engine Style, Atmospheric Texture & Cadence**:
   - Lock frame cadence, lighting texture, and render style.
   - *Syntax*: `3D Pixar Disney animation aesthetic, warm ambient rim lighting, volumetric god rays, smooth natural motion blur, 30fps, 8K resolution`.

---

### Tool-Specific Motion Configuration Matrix:

| Platform | Recommended Mode | Camera Slider | Motion Brush Targets | Anti-Warp Settings |
| :--- | :--- | :---: | :--- | :--- |
| **Kling AI 1.5** | Image-to-Video (Professional 10s) | Intensity `2/10` to `4/10` | Brush moving hand/spout + falling particles (set downward vector) | Relevance: `0.75` |
| **Google Veo 2** | Image-to-Video | Cinematic Gimbal | Particle emitters + character action zone | High prompt fidelity |
| **Luma Dream Machine** | Keyframe / I2V | Smooth Dolly/Pan | Highlight kinetic subjects (water, coins, steam) | Strict geometry lock |
| **Runway Gen-3 Alpha** | Gen-3 I2V | Fixed Camera or Pan `1.5` | Motion Brush 1 on character arm, Brush 2 on falling particles | Motion level `3` |

---

### Production Benchmark: The Magic Millstone (5 Ultra-Precision Clips):

* **Clip 1 (`clip_1.mp4`) — Cave & Glowing Runes (Discovery)**:
  *Attached Starting Frame: `scene_1.jpg`*
  ```text
  Slow cinematic forward dolly-in with smooth gimbal stabilization. Keshav maintains rigid, anatomically consistent facial features and body geometry without morphing; his right hand slowly and gently moves forward to touch the glowing circular stone millstone. Golden mystical runes pulse with warm breathing light, casting flickering amber reflections across his face and clothes. Soft golden dust particles drift upward through volumetric sunbeams filtering into the mossy cave. 3D Pixar Disney aesthetic, smooth natural motion blur, 30fps, zero face distortion, rigid stone geometry.
  ```
* **Clip 2 (`clip_2.mp4`) — Turning Handle & Sweets (Miracle)**:
  *Attached Starting Frame: `scene_2.jpg`*
  ```text
  Eye-level smooth tracking camera. Keshav's joyful smile and face remain completely consistent without warping as his hands grip and smoothly rotate the rigid wooden handle clockwise in a continuous circular motion. The ancient stone millstone maintains solid rigid structure while spinning smoothly. Steaming hot golden jalebis and round sweets cascade downward under realistic gravity simulation, tumbling and settling onto the shining brass plate with curling wisps of white volumetric steam and magical sparkling golden embers. High physical realism, Pixar 3D animation, fluid particle dynamics, 30fps, no melting.
  ```
* **Clip 3 (`clip_3.mp4`) — Coins Waterfall (Multiplication)**:
  *Attached Starting Frame: `scene_3.jpg`*
  ```text
  Macro 45-degree slow orbital camera pan. The round stone millstone wheel spins smoothly on its axis with unwavering solid geometry while glowing ancient runes emit a continuous warm luminescence. A steady, shimmering waterfall of heavy solid silver and gold coins streams continuously out from the stone spout, cascading downward under gravity and piling up naturally on the clay ground with metallic clinking dynamics. Glinting metallic specular reflections, sparkling silver bokeh in shallow depth of field, warm candlelight illumination, Octane 3D render, hyper-detailed physics, 30fps.
  ```
* **Clip 4 (`clip_4.mp4`) — Storm & Salt Torrent (The Greed Trap)**:
  *Attached Starting Frame: `scene_4.jpg`*
  ```text
  Dramatic high-angle camera with subtle natural ocean roll. The rustic wooden rowboat rocks violently amidst turbulent crashing turquoise sea swells and distant white lightning flashes in storm clouds. The thief clutches his head, his terrified facial expression and clothing holding strict physical consistency. The solid stone millstone sits firmly in the boat, continuously spewing an overwhelming torrent of granulated white salt that pours rapidly downward, spreading and filling the hull, causing the wooden boat to slowly sit deeper into the water. Deep chiaroscuro atmospheric tension, Pixar 3D style, realistic granular fluid physics, 30fps.
  ```
* **Clip 5 (`clip_5.mp4`) — Resolution & Sea Whirlpool (Moral Climax)**:
  *Attached Starting Frame: `scene_5.jpg`*
  ```text
  Cinematic wide overhead crane shot slowly rising upward toward golden morning sunbeams breaking through parting dark storm clouds. On the ocean surface, a spiraling white foam whirlpool gently dissipates into crystal-clear turquoise waters. Deep beneath the clear water on the sunlit sandy seabed, the ancient stone millstone rests firmly, steadily emitting smooth ribbons of luminous white salt that swirl gently through the azure currents like silk trails. Inspiring epic moral climax, serene water caustics, radiant lens flare, 3D Pixar Disney aesthetic, 8K, 30fps, pristine motion blur.
  ```

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
