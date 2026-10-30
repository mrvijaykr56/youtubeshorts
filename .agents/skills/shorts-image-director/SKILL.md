---
name: shorts-image-director
description: >-
  Specialized agentic skill to direct, engineer prompts, batch generate, manually curate, and assemble
  high-quality 9:16 vertical images for Image-to-Video YouTube Shorts using Antigravity's generate_image
  tool and the MyVideoWorkspace backend rendering engine. Maintains character and world visual consistency,
  features Chintu the Monkey mascot, enforces 2-3s visual cut pacing, strict kid-safe shields, and delivers
  pristine full-frame video renders with zero scrubber bars.
---

# YouTube Shorts Visual Director & Image-to-Video Skill (MagicalTalesKidz)

This skill guides the agent in generating, managing, and rendering cohesive, cinematic 9:16 vertical scenes for Image-to-Video YouTube Shorts and Instagram Reels using Antigravity's native `generate_image` tool, the web frontend, and the Python rendering engine.

---

## 1. Visual Consistency Framework (Character & World Sync) 👥🌍

When generating images for an Image-to-Video Short, avoiding stylistic or character drift is critical. If a character's face, clothing, or environment shifts randomly between scenes, video immersion breaks.

### The 3 Pillars of Scene-to-Scene Synchronization:

1. **The Official Channel Mascot DNA: Chintu the Monkey (चिंटू बंदर)** 🐒✨
   - When generating or featuring the channel mascot, ALWAYS use the immutable character anchor:
     `"Chintu, an adorable 3D Pixar-style golden-brown Indian monkey mascot, oversized expressive warm amber eyes, soft cream-colored tummy and muzzle, wearing a tiny red festive vest with gold trim, bouncy curled tail, emotive floppy ears, lively and playful gestures."`
   - *Role*: Chintu can be the story protagonist, a curious spectator on a branch, or the friendly companion who reacts to the plot twists.

2. **The World & Lighting Anchor**:
   - Define a shared environment statement prepended to all scene prompts:
     `[Setting] + [Primary light source & color temperature] + [Shadow style] + [Atmosphere]`
   - *Example*: `"Ancient Indian banyan forest, warm amber morning sunbeams piercing through mist, glowing golden dust motes, rich terracotta soil, 3D Pixar aesthetic, 9:16 vertical framing."`

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

## 2. Visual Pacing & Rapid Cut Architecture (2–3 Seconds Per Beat) ⏱️✂️

In modern YouTube Shorts, holding a single static image for 8–10 seconds causes catastrophic viewer drop-off.
For high-retention 30–38s Shorts (70–85 words), enforce **rapid visual cut pacing**:

1. **Cut Frequency**:
   - Plan a dynamic visual beat change every **2 to 3 seconds** (6 to 10 visual prompt beats across the Short).
   - If using 5 narrative scenes, each scene MUST feature distinct camera angles and perspective changes rather than static repeats.

2. **The 5-Beat Kinetic Camera Progression**:
   - **Beat 1 (0–3s - Immediate Action Hook)**: Dynamic low-angle or Dutch tilt dropping into crisis (e.g. net collapsing, pot bubbling gold).
   - **Beat 2 (3–7s - Tension / Reaction)**: Over-the-shoulder medium shot showing character emotional reaction (wide eyes, gasping).
   - **Beat 3 (7–12s - The Catalyst / Decision)**: Close-up on the magical object or determined character gesture.
   - **Beat 4 (12–18s - The Climax / Collective Action)**: Dynamic upward action angle (flapping wings, swirling light, bursting sparks).
   - **Beat 5 (18–25s - The Foil / Comedic Reaction)**: Reaction shot of the antagonist/villain frozen in comedic surprise.
   - **Beat 6 (25–35s - Heroic Resolution & Loop Staging)**: Radiant golden-hour macro or wide hero shot resolving into the loop.

---

## 3. Strict Kid-Safe Content Guardrails & Negative Shields 🛡️👶

Because our primary audience includes toddlers, young children (ages 3–9), and discerning parents, all visual prompts MUST be protected by strict kid-safe guardrails:

### Banned Visual Elements (Zero-Tolerance):
- ❌ **No Nightmare Horror**: No eerie dark shadows, glowing red eyes, creepy silhouettes, or demonic grins.
- ❌ **No Realistic Violence / Pain**: No blood, open wounds, sharp fangs snapping on necks, weapons piercing bodies, or animals in genuine distress.
- ❌ **No Grotesque Predators**: Wolves, lions, snakes, and hunters must be styled as cute, animated, or softly comedic characters (similar to *The Lion King* or *Madagascar*), never menacing or photorealistic monsters.
- ❌ **No Text or Artifacts**: Never write "letters", "text", "watermark", "subtitles" in prompts (distorts image synthesis).

### Approved Visual Tones:
- Warm, luminous color palettes (mango yellow, peacock teal, marigold orange, emerald green, warm terracotta).
- Soft rounded edges on characters and props.
- Comedic, expressive character expressions (pouting, wide-eyed curiosity, cheerful smiles, funny exaggerated jaw drops).

---

## 4. Pre-Flight Validation & User Approval 🛑

**CRITICAL REQUIREMENT (Zero Token Wastage)**:
Before executing batch `generate_image` calls:
1. **Run the Pre-Flight Storyboard Validator**:
   ```powershell
   python -u backend/scripts/storyboard_validator.py --json "path/to/script.json"
   ```
   - Must have **0 blocking errors** (e.g., no banned text tokens, valid 9:16 signals, within Shorts ceiling).
2. **Present the Validated Storyboard & Art Style** to the user with the validation stats.
3. **Ask for explicit user approval**:
   > *"The storyboard has passed all pre-flight safety checks (0 errors, ~Xs estimated length). Would you like me to proceed with generating these [N] 9:16 images, or would you like to tweak any scenes or style parameters first?"*
4. **DO NOT generate images until the user gives explicit confirmation.**

---

## 5. Generating Images with Antigravity `generate_image`

For each scene in the storyboard (after receiving user approval):

1. **Pre-Generation Duplicate / Cache Check** 🛑:
   - Check if `scene_{X}.jpg` or `scene_{X}.png` already exists in destination folder (`backend/output/<job_id>/`) and is valid (>10 KB).
   - If it already exists, **skip regeneration** to prevent wasted tokens, unless the user explicitly requests a re-roll.

2. **Synthesize the Final Prompt (Ensuring Distinct Camera Framing)**:
   ```
   [World Anchor] + [Character Anchor (including Chintu if present)] + [Scene Action & DISTINCT Camera Angle] + [3D Pixar Art Style Template] + [Kid-Safe Shields] + [9:16 Vertical Composition]
   ```

3. **Invoke the Tool**:
   Call `generate_image` with:
   - `AspectRatio`: `"9:16"`
   - `ImageName`: `scene_1`, `scene_2`, `scene_3`, etc. (strictly unique per scene).
   - `Prompt`: The synthesized prompt.
   - `ImagePaths`: For scenes 2..N, pass `["<path_to_scene_1.jpg>"]` for visual conditioning.

---

## 6. Manual Scene Image Upload & Replacement 📤🖼️

The Image-to-Video pipeline supports **manual scene image uploads**, allowing creators or agents to supply custom stills, high-resolution art, or real photography for any scene without re-running AI generation:

1. **Frontend Web Interface**:
   - In **Step 2 (Storyboard & Prompts)**, each scene card features an **"Upload Image"** action with drag-and-drop and file selection.
   - Selecting a file immediately uploads the image, refreshes the scene preview with a cache-busting timestamp, and saves the asset into the active job directory.

2. **Backend API Endpoint**:
   - `POST /upload-scene-image`
   - **Form Fields**:
     - `image`: The uploaded image binary (PNG, JPG, JPEG, WebP, AVIF).
     - `scene_number`: 1-based integer corresponding to target scene.
     - `job_id` (optional): Active job directory in `backend/output/`.
   - **Processing**:
     - The backend standardizes all uploads into high-quality RGB JPEG format (`scene_{scene_number}.jpg`).
     - Cleans up stale legacy PNG variants (`scene_{scene_number}.png`).
     - Automatically updates `storyboard.json` and `script.json` with the new file path.

---

## 7. Asset Deployment & Workspace Organization

All assets for the active Short must be organized in the job directory under `backend/output/<job_id>/`:

```text
backend/output/<job_id>/
├── script.json          # Storyboard metadata and narration lines
├── storyboard.json      # Complete validated storyboard schema
├── scene_1.jpg          # Standard 9:16 visual for Scene 1
├── scene_2.jpg          # Standard 9:16 visual for Scene 2
├── scene_3.jpg          # Standard 9:16 visual for Scene 3
...
└── final_short.mp4      # Compiled video output
```

---

## 8. Video Compilation & Rendering (Image to Video) 🚀

Once images and `script.json` are staged in `backend/output/<job_id>/`, video assembly can be triggered via the web UI or CLI:

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
1. **Pristine Full-Frame Standard (Zero Scrubber Bar)**:
   - The final video MUST have **zero bottom progress scrubber bars**. Clean, uninterrupted 9:16 vertical canvas.
2. **Compile Auto-Recovery / Fault Tolerance**:
   - If a scene image is missing or corrupted, the pipeline synthesizes a **3D Pixar enchanted storybook fallback card** (`_create_fallback_image`) with an indigo-to-amber gradient, golden fairytale border, and stardust aura.
3. **Motion & Transitions**:
   - Continuous subtle Ken Burns camera motion (pan/zoom) on each still to create lifelike motion.
   - Smooth optical transitions (`xfade`) between scenes.
4. **Audio & Subtitles**:
   - High-definition Edge-TTS / KittenTTS narration.
   - Word-level synchronized ASS subtitles positioned bottom-center (Alignment 2, MarginV=240, 50px compact font).
