---
name: shorts-script-polisher
description: >-
  Specialized agentic skill to transform raw ideas, topics, articles, or rough drafts into
  high-retention viral YouTube Shorts storyboards. Formats output as strict JSON with
  0-3s psychological hooks, punchy narration, embedded subtitle emojis, and granular visual
  camera prompts for 9:16 image generation. Supports English, Hindi, and Hinglish.
---

# YouTube Shorts Script Polisher & Storyboard Director

This skill guides the agent in crafting viral, high-retention YouTube Shorts scripts and converting them into structured storyboard JSON compatible with the YTShorts rendering pipeline.

---

## 1. Core Principles of YouTube Shorts Retention

1. **The 3-Second Hook Rule**:
   - The first scene MUST disrupt scrolling with a curiosity gap, paradoxical question, counter-intuitive statement, or high-stakes reveal.
   - *Bad*: "Today we will talk about honey and its properties."
   - *Viral*: "Did you know honey never expires? 🍯 Scientists ate 3,000-year-old honey from Egyptian tombs!"

2. **Pacing & Word Count**:
   - Total length: **5 to 8 scenes** (approx. 50–85 words total for a 30–45 second Short).
   - Each narration sentence should be concise (8–14 words maximum) so TTS does not sound rushed and Whisper captions remain legible.
   - 1 scene = 1 sentence = 1 visual image.

3. **Subtitle Emoji Injection**:
   - Embed 1–2 contextually relevant emojis into each scene's narration (e.g. `🏛️`, `👑`, `⚡`, `💀`).
   - These emojis are picked up by the caption styling engine (TikTok/Karaoke style) for visual flair.

4. **Strict Language Purity (Full English or Full Hindi Only)** 🎙️:
   - Spoken narration must be **100% pure English OR 100% pure Hindi**. Never mix English words or Hinglish into Hindi narration sentences.
   - **No Spoken Emojis**: Emojis are reserved strictly for visual subtitle pop. The TTS engine automatically strips them from the audio stream so voice models never read emoji names (e.g. "pleading face", "sparkles") aloud.

5. **Default Caption Standards & Bilingual Setup** 📺:
   - **Position**: Always **Bottom-Center** (Alignment 2, MarginV=240) so captions sit safely in the lower-third without obscuring character faces.
   - **Font Size**: Reduced, compact font size (50px base) to keep the canvas clean and readable.
   - **Bilingual Shorts (Hindi Voice + English Captions)**: Always include both `"narration_hi"` (spoken in 100% pure Hindi) and `"narration"` (displayed in English captions).

6. **High-CTR Viral Title Formula** 💥:
   - Structure every title with a high-curiosity Hindi hook, an English contextual subtitle, and ranking tags:
     `[Emotional Hindi Hook + Emoji] | [Punchy English Subtitle] | [Niche Tags #Shorts]`
   - *Example*: `लालिची बंदर को मिली जादुई सीख! 🐒✨ Never Be Greedy | Hindi Kahaniya #Shorts`
   - *Example*: `आसमान से गिरा एक जादुई तारा! 🐿️⭐ Cheeku's Magic Wish | Hindi Kids Story #Shorts`

7. **The Infinite Seamless Loop (Targeting >100% APV)** 🔄:
   - To maximize algorithmic retention, construct the final sentence so it grammatically and rhythmically connects directly back to the opening hook sentence.
   - *Example Opening*: "क्या आपने कभी सोचा है कि आसमान का तारा ज़मीन पर गिरे तो क्या होगा? 🌟"
   - *Example Ending*: "...और चीकू की यह जादुई कहानी हमें यही सिखाती है, ठीक जैसे..." (loops back to opening).

8. **Audience & Growth Metadata Payload** 📈:
   - Always include in the storyboard JSON:
     - `story_moral`: Emotional moral in Hindi (`शिक्षा`) for parental sharing.
     - `pinned_comment_question`: Thought-provoking Hindi question to drive high comment velocity.
     - `self_declared_made_for_kids`: `false` (General Audience / Family-Friendly to unlock comments and notification bells).

---

## 2. Character DNA & World Consistency Framework 👥🌍

To ensure every scene's imagery looks like it belongs in the **same exact movie**:

1. **Character DNA Anchor**:
   When a story involves characters, define an immutable **Character Anchor** with 5 fixed traits:
   - **Name & Age/Build**: e.g., "Maya, 26-year-old athletic female"
   - **Hair & Eyes**: e.g., "messy curly dark raven hair tied in a loose ponytail, sharp hazel eyes"
   - **Distinctive Facial Feature**: e.g., "slight freckles across nose, determined expression"
   - **Signature Wardrobe**: e.g., "distressed olive linen safari shirt, brass compass necklace, brown leather belt"
   - **Never Use Bare Pronouns**: NEVER write "she looks at the artifact" or "a girl runs". Always write: `"Maya (26-year-old female with curly dark ponytail in olive safari shirt) examines the golden artifact..."`

2. **World & Environment Anchor**:
   Define an immutable **World Anchor** with setting, lighting, and palette:
   - *Example*: `"Ancient subterranean sandstone tomb, flickering amber torchlight, deep cobalt shadows, floating atmospheric dust motes, 35mm film grain."`
   - Every scene prompt MUST inherit this world anchor so lighting, color temperature, and architecture remain 100% unified.

3. **Shot Progression & Anti-Duplication Rule (No Redundant Visuals)** 🚫🔄:
   - **Never repeat prompts**: Consecutive scenes must NEVER share identical framing, action, or camera angles.
   - **Enforce Dynamic Shot Progression**:
     - **Scene 1**: *Establishing Wide / Epic Scale* (Hooks the viewer with the grand environment)
     - **Scene 2**: *Medium Action / Discovery* (Focus on subject or character performing an action)
     - **Scene 3**: *Extreme Macro Close-up* (Reveals intricate texture, glowing details, or scientific micro-view)
     - **Scene 4**: *Over-the-shoulder / High-Tension Angle* (Climax, reaction, or revelation)
     - **Scene 5+**: *Hero Low-Angle / Cinematic Climax* (Resolution and CTA)

---

## 3. Storyboard Types & Formats

### Format A: Character-Driven Story / Narrative (With Anchors)
```json
{
  "character_anchor": "Maya, a 26-year-old female archaeologist, messy curly dark raven hair in a ponytail, olive linen safari shirt, brass compass necklace",
  "world_anchor": "Ancient Egyptian underground sandstone tomb, flickering amber torchlight, deep cobalt shadows, floating golden dust motes",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "Deep beneath the Egyptian desert, Maya uncovered a tomb sealed for 3,000 years! 🏛️",
      "visual": "Maya (26yo female archaeologist, curly dark ponytail, olive linen shirt) holding a flickering bronze torch, staring in awe at a towering stone doorway covered in glowing hieroglyphs, low-angle cinematic shot, warm amber torchlight, dramatic rim lighting, 9:16 vertical framing, 8k resolution"
    },
    {
      "scene_number": 2,
      "narration": "Inside, three untouched alabaster jars glowed under the torchlight. 🍯",
      "visual": "Maya (26yo female archaeologist, curly dark ponytail, olive linen shirt) kneeling beside an ancient stone altar, inspecting three translucent golden honey jars, macro extreme close-up, warm amber glow illuminating her face, volumetric lighting, 9:16 vertical"
    }
  ]
}
```

### Format B: Viral Fact / Narrative (Default)
Standard storytelling or mind-blowing fact short.

```json
[
  {
    "scene_number": 1,
    "narration": "What if your brain could predict the future before you blink? ⚡",
    "visual": "Extreme close-up of a glowing human eye, neural synapses pulsing with electric cyan and magenta lightning in the iris, cinematic macro photography, shallow depth of field, 9:16 vertical framing, photorealistic 8k, dramatic rim lighting"
  },
  {
    "scene_number": 2,
    "narration": "Scientists found your subconscious makes decisions 7 seconds before you realize it! 🧠",
    "visual": "A futuristic laboratory MRI scanner visualizing a glowing holographic human brain with fiery orange neural pathways, dark moody aesthetic, volumetric lighting, 8k resolution"
  }
]
```

### Format B: 2-Character Dialogue Short
Alternating conversation between two characters (great for interviews, debates, or comedy).

```json
[
  {
    "scene_number": 1,
    "speaker": "Host",
    "narration": "You spent $50,000 on virtual real estate?! 🤯",
    "visual": "Modern podcast studio, vibrant neon purple backlight, expressive young host looking shocked into camera, shallow depth of field, cinematic lighting"
  },
  {
    "scene_number": 2,
    "speaker": "Guest",
    "narration": "And I just sold it yesterday for half a million dollars! 📈💰",
    "visual": "Confident young entrepreneur smiling in modern penthouse office overlooking skyline at sunset, warm cinematic lighting"
  }
]
```

### Format C: Step-by-Step Educational Tutorial
Used for slide-based tutorials with titles and bullet points.

```json
[
  {
    "scene_number": 1,
    "step_title": "Introduction",
    "slide_title": "Master Python Lists",
    "bullets": [
      "Ordered collection of items",
      "Defined with square brackets []",
      "Fully mutable and dynamic"
    ],
    "code_snippet": "fruits = ['apple', 'mango']",
    "narration": "Here are 3 essential tricks to master Python lists in under 30 seconds! 🐍",
    "visual": "Sleek 3D modern developer workstation, glowing Python code on monitor, minimalist dark mode studio aesthetic"
  }
]
```

---

## 3. Visual Prompt Engineering for the AI Image Generator

Every scene's `"visual"` field MUST be engineered as a standalone, high-fidelity prompt:

1. **Shot Type & Angle**: `Macro extreme close-up`, `Low-angle heroic wide shot`, `Eye-level cinematic portrait`, `Birds-eye atmospheric view`.
2. **Subject & Action**: Precise physical objects, character gestures, facial expressions.
3. **Lighting & Atmosphere**: `Volumetric god rays`, `Dramatic chiaroscuro`, `Moody cyber neon rim lighting`, `Warm golden hour glow`.
4. **Composition & Quality**: `9:16 vertical framing`, `Depth of field / bokeh`, `Photorealistic 8k`, `Color graded cinematic film still`.
5. **Negative Rules**: Never write "cool", "nice", "text on screen", "watermark", or generic non-visual terms.

---

## 4. Pre-Flight Validator Check (Zero-Token Wastage Guarantee) 🛡️

To prevent token wastage, broken runs, or video render errors, **every storyboard MUST pass validation before user handoff and image generation**.

You can run the built-in validator directly:
```powershell
.\backend\venv\Scripts\python.exe backend\scripts\storyboard_validator.py --json "path/to/script.json"
```

### Validator Rule Set:
1. **Scene Count**: 4 to 9 scenes (Ideal: 5–8 scenes). Exceeding 10 scenes is blocked.
2. **Narration Duration & Limit**: Total words must be between 45 and 130 words (~20s to 55s). Exceeding 130 words is blocked as it breaches YouTube's 60-second Shorts ceiling.
3. **Pacing Per Scene**: 8 to 16 words per scene. Avoids caption line wrapping and mobile screen cutoff.
4. **TTS Formatting Integrity**: Strips unpronounceable markdown artifacts (`**bold**`, `_italic_`, `[SFX notes]`, `# headers`) so TTS never reads literal code tokens.
5. **Subtitle Emojis**: Verifies at least 1–2 emojis are injected for dynamic TikTok/Karaoke subtitles.
6. **Visual Prompt Safety & Precision**:
   - **Banned Token Filter**: Flags words like `text`, `letters`, `subtitles`, `words`, `watermark`, `font`, `logo` which cause Imagen to render distorted text artifacts.
   - **Composition Signals**: Requires explicit camera angles (`macro close-up`, `wide shot`, `cinematic portrait`, etc.).
   - **Lighting Signals**: Requires explicit illumination cues (`volumetric rays`, `chiaroscuro`, `golden hour`, `torchlight`, etc.).

---

## 5. Mandatory Human Approval Gateway 🛑

**CRITICAL RULE**: 
Never automatically generate images without explicit user approval.

1. Once the storyboard passes the Pre-Flight Validator with **0 blocking errors**, present the clean storyboard and validation report to the user.
2. Ask the user for approval:
   > *"The storyboard has passed all pre-flight checks (duration: ~Xs, scenes: N, token safety: 100%). Do you approve these scenes and visual directions, or would you like any adjustments before I generate the images?"*
3. **Wait for user confirmation** before calling any image generation tools.

