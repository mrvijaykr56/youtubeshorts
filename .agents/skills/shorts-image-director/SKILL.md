---
name: shorts-image-director
description: >-
  Specialized agentic skill to direct, engineer prompts, batch generate, manually curate, and assemble
  high-quality 9:16 vertical images for Image-to-Video YouTube Shorts using Antigravity's generate_image
  tool and the MyVideoWorkspace backend rendering engine. Maintains character and world visual consistency,
  features Chintu the Monkey mascot, enforces 2-3s visual cut pacing, dual-reference chaining (drift control),
  strict kid-safe shields, and delivers pristine full-frame video renders with zero scrubber bars.
---

# YouTube Shorts Visual Director & Image-to-Video Skill (MagicalTalesKidz)

This skill guides the agent in generating, managing, and rendering cohesive, cinematic 9:16 vertical scenes for Image-to-Video YouTube Shorts and Instagram Reels using Antigravity's native `generate_image` tool, the web frontend, and the Python rendering engine.

---

## 1. Visual Consistency Framework (Character & World Sync) 👥🌍

When generating images for an Image-to-Video Short, avoiding stylistic or character drift is critical. If a character's face, clothing, or environment shifts randomly between scenes, video immersion breaks.

### The 4 Pillars of Scene-to-Scene Synchronization:

1. **The Official Channel Mascot DNA: Chintu the Monkey (चिंटू बंदर)** 🐒✨
   - When generating or featuring the channel mascot, ALWAYS use the immutable character anchor:
     `"Chintu, an adorable 3D Pixar-style golden-brown Indian monkey mascot, oversized expressive warm amber eyes, soft cream-colored tummy and muzzle, wearing a tiny red festive vest with gold trim, bouncy curled tail, emotive floppy ears, lively and playful gestures."`
   - For all recurring characters, **copy the `anchor` string verbatim from `backend/output/series_bible.json`**. Never paraphrase it.

2. **The World & Lighting Anchor**:
   - Define a shared environment statement prepended to all scene prompts:
     `[Setting] + [Primary light source & color temperature] + [Shadow style] + [Atmosphere]`
   - *Example*: `"Ancient Indian banyan forest, warm amber morning sunbeams piercing through mist, glowing golden dust motes, rich terracotta soil, 3D Pixar aesthetic, 9:16 vertical framing."`

3. **Dual Visual Reference Chaining (`ImagePaths` parameter)** 🔗:
   - Antigravity's `generate_image` tool natively supports **`ImagePaths`** (passing previous images as conditioning references).
   - **The Workflow**:
     1. Generate **Scene 1** (establishing master character look and lighting). Save it.
     2. For **Scene 2, 3, 4, 5...**, pass both references: `ImagePaths: ["<path_to_scene_1.jpg>", "<path_to_previous_scene.jpg>"]`.
     3. This conditions the generative model on both the master character appearance (Scene 1) and the immediate preceding action state (previous scene), eliminating character drift!

4. **The Single-Scene Re-Roll Rule**:
   - If a character drifts in a scene (e.g. wrong vest color, altered facial shape), **re-roll only that specific scene** rather than regenerating the entire batch. Feed Scene 1 and the best prior scene as references.

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
   - Plan a dynamic visual beat change every **2 to 3 seconds** (5 to 6 distinct scenes across a 32–36s Short).
   - Each scene MUST feature distinct camera angles and perspective changes rather than static repeats.

2. **The 5-Beat Kinetic Camera Progression**:
   - **Beat 1 (0–3s - Immediate Action Hook)**: Dynamic low-angle or Dutch tilt dropping into crisis (e.g. net collapsing, pot bubbling gold).
   - **Beat 2 (3–7s - Tension / Reaction)**: Over-the-shoulder medium shot showing character emotional reaction (wide eyes, gasping).
   - **Beat 3 (7–14s - The Catalyst / Decision)**: Close-up on the magical object or determined character gesture.
   - **Beat 4 (14–22s - The Climax / Collective Action)**: Dynamic upward action angle (flapping wings, swirling light, bursting sparks).
   - **Beat 5 (22–32s - Celebratory Resolution & Loop Staging)**: Radiant golden-hour macro or wide hero shot resolving into the loop.

---

## 3. Strict Kid-Safe Content Guardrails & Negative Shields 🛡️👶

Because our primary audience includes toddlers, young children (ages 3–9), and discerning parents, all visual prompts MUST be protected by strict kid-safe guardrails:

### Banned Visual Elements (Zero-Tolerance):
- ❌ **No Nightmare Horror**: No eerie dark shadows, glowing red eyes, creepy silhouettes, or demonic grins.
- ❌ **No Realistic Violence / Pain**: No blood, open wounds, sharp fangs snapping on necks, weapons piercing bodies, or animals in genuine distress.
- ❌ **No Grotesque Predators**: Wolves, lions, snakes, and hunters must be styled as cute, animated, or softly comedic characters (similar to *The Lion King* or *Madagascar*), never menacing or photorealistic monsters.
- ❌ **No Banned Text Tokens**: Never write `text`, `words`, `letters`, `subtitles`, `watermark`, `font`, `logo`, `title card`, `captions` in prompts (distorts image synthesis into illegible scribbles).

### Approved Visual Tones:
- Warm, luminous color palettes (mango yellow, peacock teal, marigold orange, emerald green, warm terracotta).
- Cozy fairytale textures and radiant volumetric sunlight.

---

## 4. Pre-Flight Validation & User Approval 🛑

Never generate images without explicit human confirmation:
1. Verify script has passed `backend/scripts/storyboard_validator.py`.
2. Present all 5 scene prompts to the user with camera, lighting, and mascot specifications.
3. Wait for explicit user approval before calling the image generator.

---

## 5. Generating Images with Gemini Inbuilt AI

Always invoke the `image-generator` subagent using **Gemini inbuilt AI**:
- Prompt specification includes: 9:16 vertical aspect ratio, 3D Disney Pixar animation aesthetic, character anchor, world lighting, and 8k Octane rendering cues.
- Save assets cleanly as `scene_1.jpg`, `scene_2.jpg`, `scene_3.jpg`, `scene_4.jpg`, `scene_5.jpg` in the corresponding `backend/output/<story_key>/` directory.
- Create or select a high-contrast **cover thumbnail** (`cover.jpg` / `scene_1.jpg`) with bold character expression.

---

## 6. Optional Image-to-Video Motion Prompts 🎥

When generating or extending visuals into full video animation (e.g. via Veo 2 or Luma Dream Machine), append camera motion vectors:
- **Scene 1 (Hook)**: `Fast dynamic push-in camera track, slight low-angle rise, dramatic volumetric dust swirl.`
- **Scene 2 (Reaction)**: `Smooth orbital pan 15 degrees around character, shallow depth of field shift.`
- **Scene 3 (Magic/Action)**: `Rapid rising crane shot, glittering particles exploding outward, kinetic camera shake.`
- **Scene 4 (Payoff)**: `Slow-motion cinematic glide, soft glowing god rays, warm lens flare.`
- **Scene 5 (Loop End)**: `Wide static tableau with gentle breathing character animation, smooth wind through leaves.`

---

## 7. Video Compilation & Rendering Specifications 🚀

Assemble the Short using the standalone pipeline:
```powershell
python -u backend/scripts/assemble_short.py --job_dir "backend/output/<story_key>" --voice hi_female --caption_lang Hindi --caption_style tiktok --music none --resolution 1080p --transition dynamic
```

### Rendering Specifications:
- **Resolution**: 1080x1920 Full HD (9:16 portrait).
- **Motion Engine**: Ken Burns zoom_in, zoom_out, pan_left, pan_right proportionally aligned to spoken word count.
- **Hardware Acceleration**: Automatically selects `h264_qsv` (Intel QuickSync) or `h264_nvenc` (NVIDIA) for fast 60fps encoding.
- **Transitions**: Cinematic xfade transitions with matched whoosh Foley audio cues.
- **Subtitles**: ASS TikTok-style animated word-by-word subtitles centered in the lower-third with safe margins.
