---
name: shorts-script-polisher
description: >-
  Specialized agentic skill to transform raw ideas, topics, articles, or rough drafts into
  high-retention viral YouTube Shorts storyboards. Formats output as strict JSON with
  0-3s psychological hooks, punchy narration, embedded subtitle emojis, and granular visual
  camera prompts for 9:16 image generation. Supports English, Hindi, and Hinglish.
---

# YouTube Shorts Script Polisher & Storyboard Director

This skill guides the agent in crafting viral, high-retention YouTube Shorts scripts and converting them into structured storyboard JSON compatible with the MyVideoWorkspace rendering pipeline.

---

## 1. Core Principles of YouTube Shorts Retention

1. **The 3-Second Hook Rule**:
   - The first scene MUST disrupt scrolling with a curiosity gap, paradoxical question, counter-intuitive statement, or high-stakes reveal.
   - *Bad*: "Today we will talk about honey and its properties."
   - *Viral*: "Did you know honey never expires? 🍯 Scientists ate 3,000-year-old honey from Egyptian tombs!"

2. **Pacing, Word Count & The 2-Line Per Scene Standard** 📜:
   - **Scene Count**: 5 to 6 scenes.
   - **2 Lines Per Scene Mandate**: Never write a bare 1-line scene. Each scene MUST have **2 engaging, descriptive sentence lines** (approx. 18–22 words per scene).
   - **Target Duration**: **95–110 words total (~45–52 seconds)**. Single-sentence scenes end too fast (~25s) and feel incomplete; 2 lines per scene allow character depth, sensory detail, and emotional plot resolution while staying safely within the 60-second Shorts limit.
   - 1 scene = 2 story lines = 1 cohesive visual image (held for 8–10 seconds with dynamic Ken Burns motion).

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

7. **Seamless Loop & Complete Inspiring Ending (Targeting >100% APV)** 🔄:
   - Construct endings that are clean, grammatically complete, and inspiring. 
   - 🚫 **STRICT BAN ON "JUST LIKE..." / "ठीक जैसे..."**: NEVER end narration with trailing comparison stems such as `"just like..."`, `"just like"`, `"जैसे..."`, or `"ठीक जैसे..."`. Every ending sentence MUST be fully resolved, punchy, and self-contained.
   - *Example Opening*: "क्या आप जानते हैं कि एक जादुई बत्तख पूरे गांव को कैसे बदल सकती है? 🪺✨"
   - *Example Ending*: "हमेशा याद रखें, सब्र और संतोष ही जीवन का सबसे बड़ा खजाना है! 🌟" (Complete, inspiring takeaway).

8. **Audience & Growth Metadata Payload** 📈:
   - Always include in the storyboard JSON:
     - `story_moral`: Emotional moral in Hindi (`शिक्षा`) for parental sharing.
     - `pinned_comment_question`: Thought-provoking Hindi question to drive high comment velocity.
     - `self_declared_made_for_kids`: `false` (General Audience / Family-Friendly to unlock comments and notification bells).

9. **Top 10 Competitor SEO Architecture (Benchmarked vs Koo Koo TV, Infobells, PunToon Kids)** 🏆:
   - **Leading Hashtags**: Place high-velocity hashtag cloud right at the very top of description (e.g. `#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation #3DAnimation #HindiCartoon #BalKahani`).
   - **3-Tier Tag Cloud (25-28 Tags)**:
     - *Tier 1 (Story/Character)*: Exact character names, story titles, English + transliterated Hindi (e.g. `sone ka anda`, `golden goose story`, `lalchi kisan`).
     - *Tier 2 (High-Traffic Niche Umbrella)*: `jadui kahaniya`, `hindi animated tales`, `hindi stories for kids`, `hindi story cartoon`, `moral stories in hindi`, `panchatantra stories`, `stories for kids`, `bedtime stories in hindi`.
     - *Tier 3 (Dual-Script Devanagari)*: `हिंदी कहानियां`, `पंचतंत्र की कहानियां`, `नैतिक कहानियां`, `हिंदी कार्टून`, `बाल कहानियां`.
   - **Category**: Always enforce **Category 1 (Film & Animation)**.

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

### Format C: 2-Character Dialogue Short
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

---

## 6. Top 10 Competitor Metadata & SEO Architecture 🏆

Every generated Short must include competitor-benchmarked metadata learned directly from **Koo Koo TV (4.88M subs)**, **Infobells Hindi (72.8M subs)**, and **PunToon Kids (3.94M subs)**:

### 1. Title Formulation (Strictly $\le 95$ Chars)
YouTube rejects titles $\ge 100$ characters. Use the proven high-CTR formula:
`[Emotional Hook / Intriguing Question in Hindi + 1-2 Emojis] [English Name] | 3D Hindi Kahaniya #Shorts`
- *Example*: `कुल्हाड़ी नदी में गिरी, जलपरी ने क्या दिया? 🪓✨ Honest Woodcutter | 3D Hindi Kahaniya #Shorts` (92 chars)
- *Example*: `रोज एक सोने का अंडा! पर लालच ने क्या किया? 🪺✨ Goose of Gold | 3D Hindi Kahaniya #Shorts` (90 chars)

### 2. Infobells Leading Hashtag Cloud & Description
Place 5–8 high-velocity hashtags at the very top of the description to lock in YouTube Shorts algorithmic classification immediately:
```text
#Shorts #HindiKahaniya #MoralStories #Panchatantra #[StoryKeyword] #3DAnimation #HindiCartoon #BalKahani

[2-3 sentence engaging story summary in Hindi]

🌟 कहानी की सीख (Moral of the Story):
[Clear, inspiring moral message without trailing comparison phrases]

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation
```

### 3. 3-Tier Video Tags Architecture (Strictly $\le 380$ Chars)
To avoid YouTube's HTTP 400 `invalidTags` ceiling:
1. **Tier 1 (Specific Story Tags - 5-7 tags)**: Story-specific search queries (English + Romanized Hindi).
2. **Tier 2 (High-Volume Competitor Anchor Tags - 8-10 tags)**: `"Hindi Kahaniya"`, `"moral stories in hindi"`, `"panchatantra stories"`, `"kids moral stories"`, `"3d animated stories"`, `"hindi cartoon"`, `"bal kahaniya"`, `"jadui kahaniya"`, `"stories for kids"`, `"shorts"`, `"yt shorts"`.
3. **Tier 3 (Devanagari Dual-Script Tags - 4-5 tags)**: `"हिंदी कहानियां"`, `"पंचतंत्र की कहानियां"`, `"नैतिक कहानियां"`, `"हिंदी कार्टून"`.
- Total character length must never exceed 380 characters.


