---
name: shorts-image-director
description: >-
  Specialized agentic skill to direct, engineer prompts, batch generate, manually curate, and assemble
  high-quality 9:16 vertical images for Image-to-Video YouTube Shorts using Antigravity's generate_image
  tool and the MyVideoWorkspace backend rendering engine. Maintains character and world visual consistency,
  supports manual scene image uploads, and delivers pristine full-frame video renders with zero scrubber bars.
---

# YouTube Shorts Visual Director & Image-to-Video Skill

This skill guides the agent in generating, managing, and rendering cohesive, cinematic 9:16 vertical scenes for Image-to-Video YouTube Shorts and Instagram Reels using Antigravity's native `generate_image` tool, the web frontend, and the Python rendering engine.

---

## 1. Visual Consistency Framework (Character & World Sync) 👥🌍

When generating 5 to 20 images for an Image-to-Video Short, avoiding stylistic or character drift is critical. If a character's face, clothing, or environment shifts randomly between scenes, video immersion breaks.

### The 3 Pillars of Scene-to-Scene Synchronization:

1. **The Character DNA Blueprint**:
   - Replicate the exact same 5-part character formula in every scene featuring the character:
     `[Name + Age/Gender] + [Hair style & color] + [Facial traits] + [Exact clothing items & colors]`
   - *Example*: `"Maya, a 26-year-old female archaeologist with messy curly dark hair in a ponytail, freckles, wearing an olive linen safari shirt and brass compass necklace"`
   - Never substitute with generic terms like "she looks" or "the woman".

2. **The World & Lighting Anchor**:
   - Define a shared environment statement prepended to all scene prompts:
     `[Setting] + [Primary light source & color temperature] + [Shadow style] + [Atmosphere]`
   - *Example*: `"Subterranean ancient Egyptian sandstone tomb, warm amber torchlight casting deep flickering shadows, floating golden dust particles, dark cobalt background."`

3. **Visual Reference Chaining (`ImagePaths` parameter)** 🔗:
   - Antigravity's `generate_image` tool natively supports **`ImagePaths`** (passing previous images as visual conditioning references).
   - **The Workflow**:
     1. Generate **Scene 1** (establishing master character and lighting).
     2. Save `scene_1.jpg`.
     3. For **Scene 2, 3, 4...**, pass `ImagePaths: ["<path_to_scene_1.jpg>"]` into `generate_image`.
     4. This feeds Scene 1's visual latent features directly to Imagen 3, anchoring face shape, clothing color, and environmental tones across all subsequent scenes!

### The 3D Pixar & Disney Animation Art Style Standard 🎨✨

All visual content produced for `@MagicalTalesKidz` strictly adheres to the signature **3D Pixar / Disney Kids Animation** style:
- **Character Aesthetics**: Stylized 3D characters with large, glossy, expressive eyes, warm subsurface scattering on skin/fur/feathers, tactile clay/cloth textures, and vibrant facial emotion.
- **Fairytale Lighting & Atmosphere**: Rich volumetric god rays, magical floating golden particles, warm golden-hour rim lights, and saturated cinematic storybook color palettes.
- **Composition & Framing**: 9:16 vertical portrait composition, Octane/Unreal Engine 5 3D render feel, shallow depth of field focusing on character warmth. Never use flat 2D cartoons or grim photorealism.

---

## 2. Pre-Flight Validation & User Approval 🛑

**CRITICAL REQUIREMENT (Zero Token Wastage)**:
Before executing batch `generate_image` calls:
1. **Run the Pre-Flight Storyboard Validator**:
   ```powershell
   .\backend\venv\Scripts\python.exe backend\scripts\storyboard_validator.py --json "path/to/script.json"
   ```
   - Must have **0 blocking errors** (e.g., no banned text tokens, valid 9:16 signals, within 60s Shorts ceiling).
2. **Present the Validated Storyboard & Art Style** to the user with the validation stats.
3. **Ask for explicit user approval**:
   > *"The storyboard has passed all pre-flight safety checks (0 errors, ~Xs estimated length). Would you like me to proceed with generating these [N] 9:16 images, or would you like to tweak any scenes or style parameters first?"*
4. **DO NOT generate images until the user gives explicit confirmation.**

---

## 3. Generating Images with Antigravity `generate_image`

For each scene in the storyboard (after receiving user approval):

1. **Pre-Generation Duplicate / Cache Check** 🛑:
   - Check if `scene_{X}.jpg` or `scene_{X}.png` already exists in the destination folder (`backend/output/<job_id>/`) and is valid (>10 KB).
   - If it already exists, **skip regeneration** to prevent wasted tokens, unless the user explicitly asks to regenerate/re-roll that specific scene.

2. **Synthesize the Final Prompt (Ensuring Distinct Camera Framing)**:
   ```
   [World Anchor] + [Character Anchor] + [Scene Action & DISTINCT Camera Angle] + [Global Art Style Template] + [9:16 Vertical Composition]
   ```
   - Ensure the camera shot (e.g. wide vs macro vs reaction) differs from the preceding scene to avoid generating visually identical stills.

3. **Invoke the Tool**:
   Call `generate_image` with:
   - `AspectRatio`: `"9:16"`
   - `ImageName`: `scene_1`, `scene_2`, `scene_3`, etc. (strictly unique per scene).
   - `Prompt`: The synthesized prompt.
   - `ImagePaths`: For scenes 2..N, pass `["<path_to_scene_1.jpg>"]` for visual conditioning.

4. **Batch Generation**:
   Generate scenes sequentially or in groups of scenes (up to 20 per short).

---

## 4. Manual Scene Image Upload & Replacement 📤🖼️

The Image-to-Video pipeline supports **manual scene image uploads**, allowing creators or agents to supply custom stills, high-resolution art, or real photography for any scene without re-running AI generation:

1. **Frontend Web Interface**:
   - In **Step 2 (Storyboard & Prompts)**, each scene card features an **"Upload Image"** action with drag-and-drop and file selection.
   - Selecting a file immediately uploads the image, refreshes the scene preview with a cache-busting timestamp, and saves the asset into the active job directory.

2. **Backend API Endpoint**:
   - `POST /upload-scene-image`
   - **Form Fields**:
     - `image`: The uploaded image binary (supports PNG, JPG, JPEG, WebP, AVIF).
     - `scene_number`: 1-based integer corresponding to the target scene.
     - `job_id` (optional): Active job directory in `backend/output/`.
   - **Processing**:
     - The backend standardizes all uploads into high-quality RGB JPEG format (`scene_{scene_number}.jpg`).
     - Cleans up stale legacy PNG variants (`scene_{scene_number}.png`) to eliminate file collisions.
     - Automatically updates `storyboard.json` and `script.json` with the new file path.

---

## 5. Asset Deployment & Workspace Organization

All assets for the active Short must be organized in the job directory under `backend/output/<job_id>/`:

```text
d:\WorkSpace\MyVideoWorkspace\backend\output\<job_id>\
├── script.json          # Storyboard metadata and narration lines
├── storyboard.json      # Complete validated storyboard schema
├── scene_1.jpg          # Standard 9:16 visual for Scene 1
├── scene_2.jpg          # Standard 9:16 visual for Scene 2
├── scene_3.jpg          # Standard 9:16 visual for Scene 3
...
└── final_short.mp4      # Compiled video output
```

---

## 6. Video Compilation & Rendering (Image to Video) 🚀

Once images and `script.json` are staged in `backend/output/<job_id>/`, video assembly can be triggered via the web UI or CLI:

### A. Web API Trigger:
```http
POST /compile
Content-Type: application/json

{
  "job_id": "<job_id>",
  "voice": "in_female",
  "caption_style": "tiktok",
  "resolution": "1080p",
  "music": "none",
  "transition": "dynamic"
}
```

### B. Standalone CLI Trigger:
```powershell
python backend\scripts\assemble_short.py `
    --job_dir "backend/output/<job_id>" `
    --voice in_female `
    --caption_style tiktok `
    --music none `
    --resolution 1080p `
    --transition dynamic
```

### Critical Rendering Specifications:

1. **Zero Background Music Mandate (No BGM)**:
   - Do NOT use background music (`--music none`). Voice narration must remain 100% crisp, pure, and distraction-free for optimal speech clarity and mobile intelligibility.

2. **Pristine Full-Frame Standard (Zero Scrubber Bar)**:
   - The final video MUST have **zero bottom progress scrubber bars** (no cyan/sky-blue or colored lines at the bottom).
   - Clean, uninterrupted 9:16 vertical canvas for maximum viewer immersion and YouTube algorithm favorability.

3. **Compile Auto-Recovery / Fault Tolerance (3D Pixar Enchanted Storybook Fallback)**:
   - If a scene image is missing, corrupted, or mid-download during compile, the pipeline automatically synthesizes a **3D Pixar enchanted storybook fallback card** (`_create_fallback_image`) featuring a magical deep indigo-to-sunset-amber gradient, golden fairytale border, and shimmering stardust aura. This preserves 100% aesthetic harmony with our 3D animation universe rather than showing an unstyled placeholder.
   - Compilation is 100% resilient against transient asset failures.

4. **Motion & Transitions**:
   - Continuous subtle Ken Burns camera motion (pan/zoom) on each still to create lifelike motion.
   - Smooth optical transitions (`xfade`) between scenes.

5. **Audio & Subtitles**:
   - High-definition Edge-TTS / KittenTTS narration without background music clutter.
   - Word-level synchronized ASS subtitles positioned bottom-center (Alignment 2, MarginV=240, 50px compact font).

---

## 7. Channel Branding & Community Asset Generation 🎨📊

Beyond 9:16 vertical story scenes, the visual director also produces marketing assets using Antigravity's native `generate_image` tool:

1. **Community Tab Image Polls (1:1 Square)**:
   - Generate or center-crop characters to 1024x1024 square cards.
   - Stage cards in `backend/output/community_poll_assets/` (e.g. `poll_1_character.jpg`).
   - Image polls generate 3x–5x more reach on new channels than standard text posts.

2. **Channel Avatar Mascot (1:1 Square)**:
   - Generate centered 1024x1024 3D Pixar character portrait with expressive glossy eyes, holding a glowing storybook.
   - Save to `backend/output/channel_branding/channel_avatar_1024x1024.jpg`.

3. **Panoramic Channel Banner (16:9 Landscape)**:
   - Generate 16:9 panoramic cinematic landscape of the channel's recurring world.
   - Upscale with Lanczos filter to 2560x1440.
   - Save to `backend/output/channel_branding/channel_banner_2560x1440.jpg`.

4. **Zero External API Mandate**:
   - Always prioritize Antigravity's native `generate_image` tool. Never fall back to unverified free external image APIs.
