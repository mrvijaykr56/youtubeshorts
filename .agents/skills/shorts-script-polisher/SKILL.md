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

4. **Mandatory Ultra-Precision Protocol for Generative AI Video (Veo 2 / Kling / Luma)** 🎥🛡️:
   - When generating prompts for AI Video-to-Video assembly, ALWAYS format scene prompts using the **4-Layer Studio Prompt Architecture** (defined in `video-to-video-director`):
     - `Layer 1: Camera Vector & Speed Modulation` (slow forward dolly, 45° orbital pan, gimbal stabilization)
     - `Layer 2: Rigid Body Anatomy & Material Preservation Guards` (`[Character] maintains rigid, anatomically consistent facial features without morphing/warping`, `rigid stone/wood geometry`, `zero face melting`)
     - `Layer 3: Realistic Gravity-Driven Fluid & Particle Dynamics` (`cascading downward under realistic gravity simulation`, `fluid particle dynamics`, `curling volumetric steam`)
     - `Layer 4: Engine Style & FPS Lock` (`3D Pixar Disney aesthetic, 30fps, 8K resolution, smooth natural motion blur`)
   - Never use short 1-line video prompts in Image-to-Video mode; short prompts cause rubber warping and face melting.


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

---

## 7. The 3 Proven Viral Topic Clusters & Top 15 High-Velocity Story Roadmap 🌟

Based on the live October 2026 cross-platform audit of `@MagicalTalesKidz` and benchmarks across **Koo Koo TV (4.88M subs, 2.5B views)**, **Infobells Hindi (72.8M subs, 50.5B views)**, and **PunToon Kids (3.94M subs, 2.05B views)**:

### A. The 3 Winning Topic Clusters:
1. **Cluster 1: Village Protagonist + Supernatural/Magic Vessel** 🏺✨
   - *Formula*: A humble, kind villager unearths an ancient wish-granting or multiplying object.
   - *Examples*: *जादुई मटका (The Magic Pot)*, *जादुई चक्की (The Magic Flour Mill)*, *जादुई कुआं (The Wishing Well)*, *जादुई बांसुरी (The Enchanted Flute)*.
2. **Cluster 2: Greed vs Contentment (Supernatural Consequence)** 🪺🔥
   - *Formula*: Immediate dramatic loss when greed overrides patience.
   - *Examples*: *सोने का अंडा (The Goose of Gold)*, *सोने की कुल्हाड़ी (Honest Woodcutter)*, *लालची हलवाई और जादुई कड़ाही (Greedy Sweetmaker)*, *सोने का हिरण (The Golden Deer)*.
3. **Cluster 3: Brains over Brawn (Clever Underdog Animals)** 🧠🦁
   - *Formula*: Smallest creature outsmarts the strongest predator.
   - *Examples*: *नीला सियार (The Blue Jackal)*, *चतुर खरगोश और शेर (Clever Rabbit & Lion)*, *प्यासा कौवा (Thirsty Crow)*, *बंदर और मगरमच्छ (Monkey & Crocodile)*, *चार मित्र और शिकारी का जाल (Four Smart Friends)*.

### B. Curated Top 15 Upcoming Story Roadmap (Ranked by Viral Potential):

| Priority | Story Title (Hindi & English) | Topic Cluster | Core 0.5s Sensory Hook | Target APV |
| :---: | :--- | :---: | :--- | :---: |
| **#1** | **जादुई चक्की: जो मांगो वो निकले! 🪨✨** *(The Magic Millstone)* | Cluster 1 | जब पत्थर की पुरानी चक्की अपने आप घूमने लगी और चांदी बरसने लगी! | >105% |
| **#2** | **चार बुद्धिमान मित्र और शिकारी का जाल! 🕊️🕸️** *(Four Smart Friends)* | Cluster 3 | शिकारी के मजबूत लोहे के जाल को पूरा कबूतरों का झुंड कैसे उड़ा ले गया? | >98% |
| **#3** | **जादुई कल्पवृक्ष: हर सोच होगी सच! 🌳✨** *(The Wishing Tree)* | Cluster 1 | पेड़ के नीचे बैठते ही जो सोचा वो सामने आ गया! पर जब भूत का ख्याल आया? | >102% |
| **#4** | **लालची हलवाई और जादुई कड़ाही! 🍯🔥** *(The Greedy Sweetmaker)* | Cluster 2 | एक बूंद दूध से पूरी कड़ाही रसमलाई से कैसे भर गई? | >95% |
| **#5** | **कौवे की चतुराई और दुष्ट काला सांप! 🦅🐍** *(The Crow & The Snake)* | Cluster 3 | जहरीले नाग को भगाने के लिए कौवे ने राजकुमारी का हीरों का हार क्यों चुराया? | >100% |
| **#6** | **जादुई सोने की मछली! 🐟✨** *(The Golden Fish & 3 Wishes)* | Cluster 1 | जब नदी से निकली बात करने वाली सुनहरी मछली ने दिया एक अद्भुत वरदान! | >96% |
| **#7** | **दो हंस और बातूनी कछुआ! 🐢🪿** *(The Talkative Turtle)* | Cluster 3 | आसमान में उड़ते हुए कछुए ने जैसे ही मुंह खोला, क्या हुआ? | >105% |
| **#8** | **जादुई दर्पण: जो सच दिखाए! 🪞✨** *(The Mirror of Truth)* | Cluster 1 | इस आईने के सामने खड़े होते ही इंसान का असली रूप क्यों दिखने लगता था? | >98% |
| **#9** | **ब्राह्मण का सपना और मिट्टी का घड़ा! 🏺💭** *(The Broken Dream)* | Cluster 2 | सत्तू के घड़े को लात मारते ही कैसे टूटा करोड़पति बनने का सपना? | >97% |
| **#10** | **बगुला भगत और चतुर केकड़ा! 🦀🪶** *(The Crane & The Crab)* | Cluster 3 | ढोंगी बगुले की गर्दन पर केकड़े के नुकीले पंजों ने क्या सबक सिखाया? | >100% |
| **#11** | **जादुई जूते: हवा में उड़ाने वाले! 🥿⚡** *(The Flying Shoes)* | Cluster 1 | पुराने चमड़े के जूतों को पहनते ही मोहन बादलों के ऊपर कैसे उड़ने लगा? | >98% |
| **#12** | **सच्चा मित्र और भालू! 🐻🌲** *(The Two Friends & The Bear)* | Cluster 3 | जब खूंखार भालू सामने आया, तो दोस्त पेड़ पर चढ़कर अकेले क्यों बैठ गया? | >95% |
| **#13** | **जादुई थैला: जो कभी खाली न हो! 🎒✨** *(The Endless Bag)* | Cluster 1 | अकाल में पूरे गांव को खाना खिलाने वाला यह चमत्कारी थैला कहां से आया? | >100% |
| **#14** | **ऊंट और सियार की चालाकी! 🐪🐺** *(The Camel & The Jackal)* | Cluster 3 | गन्ने के खेत में सियार ने जानबूझकर हुआं-हुआं क्यों चिल्लाना शुरू किया? | >96% |
| **#15** | **जादुई बांसुरी और नटखट बंदर! 🪈🐒** *(The Enchanted Flute)* | Cluster 1 | जब बांसुरी की धुन पर पूरा जंगल हंसते-हंसते नाचने लगा! | >98% |


