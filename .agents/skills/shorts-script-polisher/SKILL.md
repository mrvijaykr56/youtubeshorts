---
name: shorts-script-polisher
description: >-
  Specialized agentic skill to transform raw ideas, topics, articles, or rough drafts into
  high-retention viral YouTube Shorts storyboards for MagicalTalesKidz. Formats output as strict JSON with
  0-3s psychological hooks (banning "एक बार की बात है"), 70-85 Hindi words, rhythmic alternating lines,
  no moral outro, seamless grammatical loop, Hook A/B variants, Series Bible integration, exact SFX/music cues, and 9:16 visual prompts.
---

# YouTube Shorts Script Polisher & Storyboard Director (MagicalTalesKidz)

This skill guides the agent in crafting viral, high-retention YouTube Shorts scripts and converting them into structured storyboard JSON compatible with the MyVideoWorkspace rendering pipeline for **@MagicalTalesKidz**.

---

## 1. Core Principles of YouTube Shorts Retention for Kids & Parents

### 1. The 3-Second Hook Rule (No Exposition, No "एक बार की बात है") 🛑
- **Strictly Banned Openers**: NEVER start with `"एक बार की बात है"`, `"बहुत समय पहले..."`, or slow character introductions (`"एक सुंदर जंगल में चीकू नाम का एक कबूतर रहता था..."`).
- **Immediate Sensory/Action Hook**: The first 3 seconds MUST drop the viewer into the middle of intense action, an astonishing dilemma, or an impossible mystery:
  - *Banned*: "एक जंगल में बहुत सारे कबूतर रहते थे और एक दिन शिकारी आया।"
  - *Viral (0–3s)*: "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️"
  - *Viral (0–3s)*: "राजकुमारी के हीरों का हार चुराकर कौवे ने सांप के बिल में क्यों डाल दिया? 🦅💎🐍"
- **Hook A/B Variants**: For every story, write **two hook variants** in the `hook_variants` field (`A` = paradoxical curiosity question, `B` = high-stakes action statement) to test performance across similar themes.

### 2. Pacing, Word Count & The 2-Line Per Scene Standard 📜
- **Scene Count**: Strictly **5 to 6 scenes**.
- **2 Lines Per Scene**: Never write a bare 1-line scene. Each scene has **2 short sentence lines**, **14–16 words per scene** (validator hard ceiling is 16 words).
- **Total Word Count**: Strictly **70 to 85 Hindi words** in pure Devanagari script.
- **Hindi Audio Duration Check**: Devanagari speech cadence runs ~10–15% slower than English. After TTS synthesis, verify that actual audio length is **between 30s and 45s** (hard ceiling: 55 seconds). If audio exceeds 50s, trim 1–2 words per scene and re-synthesize.
- **Rhythmic Alternation**: Alternate punchy short lines (3–5 words) with descriptive rhythmic lines (9–12 words):
  - *Short*: "सब छटपटाने लगे! 😰" (3 words)
  - *Long*: "तभी नन्हे चीकू ने सबको एक साथ पंख फड़फड़ाने का इशारा किया! 🕊️💨" (11 words)
  - *Short*: "और जाल उड़ गया! ☁️✨" (4 words)
  - *Long*: "नन्हे चूहे के तेज दांतों ने एक-एक फंदा पलक झपकते ही काट डाला! 🐭✂️" (12 words)

### 3. No Preachy Moral Outro (Show, Don't Lecture) 🚫🗣️
- **Strictly Banned Outros**: NEVER write didactic phrases such as `"हमेशा याद रखें..."`, `"इस कहानी से हमें सीख मिलती है..."`, or `"दोस्तों, लालच बुरी बला है..."`.
- **Action-Driven Lesson**: The moral must be 100% experienced through the visual resolution and the emotional triumph of the character:
  - *Banned*: "हमेशा याद रखें कि एकता में ही बल है और हमें मिल-जुलकर रहना चाहिए।"
  - *Approved*: "सारे कबूतर आज़ाद होकर आसमान में खुशी से नाच उठे, क्योंकि एक साथ मिलकर हर मुसीबत छोटी हो जाती है..."

### 4. Seamless Grammatical Loop (>100% APV) 🔄
- The final sentence of the script must grammatically, tonally, and rhythmically connect back into the opening hook line of Scene 1, creating an infinite, frictionless loop:
  - *Opening Line (Scene 1)*: "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️"
  - *Final Line (Scene 5)*: "और जब भी कोई शिकारी जाल बिछाता है, वो भूल जाता है कि कैसे..."
  - *Loop Effect*: "...भूल जाता है कि कैसे... [Replay: जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया!]"
- **Endings Variety**: Rotate looping techniques (Punchy Answer, Sound/Foley cut, Proverb, Mascot reaction) rather than ending every video on the same conjunction.

### 5. Strict Language Purity & Subtitle Emojis 🎭
- Narration must be **100% pure Hindi in Devanagari** (or 100% English for English variants). Zero Hinglish in spoken audio.
- Embed **1–2 contextually relevant emojis** in each narration line (`🕊️`, `🕸️`, `✨`, `🐭`). The ASS subtitle engine renders these dynamically with TikTok-style animated pop while TTS cleanly strips emojis from the voice stream.

### 6. Audience & COPPA Decision Note 🔔
- In the storyboard JSON, include `self_declared_made_for_kids` and record the rationale in `audience_decision_note`:
  - Pure child-directed fairytale animation is declared `true` (COPPA compliant; note: disables comments & notification bell).
  - General family co-viewing / moral folklore positioned for parents & kids together can declare `false` to keep comments and community features enabled.

### 7. Originality & Monetization Guardrails 💰
- YouTube’s monetization policy penalizes repetitive, mass-produced content.
- Ensure every script features original phrasing, unique character motivations, bespoke scene compositions, and genuine human creative direction.
- Disclose realistic AI-generated animation where platform upload tools require it.

---

## 2. Character DNA, Recurring Cast & World Consistency 👥🌍

### 1. The Channel Mascot Anchor: Chintu the Monkey (चिंटू बंदर) 🐒✨
When Chintu appears as the hero, narrator, or companion, enforce his immutable anchor verbatim:
```text
Chintu, an adorable 3D Pixar-style golden-brown Indian monkey mascot, huge expressive warm amber eyes, soft cream-colored tummy and muzzle, wearing a tiny red festive vest with gold trim, bouncy curled tail, emotive floppy ears, lively and playful gestures.
```

### 2. Series Bible (`backend/output/series_bible.json`) 🎭
Maintain recurring characters in a persistent series bible to build viewer loyalty:
```json
{
  "chintu": {
    "anchor": "Chintu, an adorable 3D Pixar-style golden-brown Indian monkey mascot, huge expressive warm amber eyes, soft cream-colored tummy, tiny red festive vest with gold trim, bouncy curled tail",
    "personality": "clever, optimistic, protective, playful",
    "catchphrase_hi": "अरे वाह! देखा दिमाग का कमाल? 🐒✨",
    "appearances": ["magic_wishing_tree", "clever_crow_necklace", "diwali_magic_rangoli"]
  },
  "kalu": {
    "anchor": "Kalu, a cute intelligent 3D Pixar-style black crow with glossy raven feathers, big curious sparkling amber eyes, sleek golden-tipped beak",
    "personality": "resourceful, strategic, underdog hero",
    "appearances": ["thirsty_crow", "clever_crow_necklace"]
  }
}
```

### 3. World & Environment Anchor:
Every story must establish a shared atmospheric anchor prepended across prompts:
- *Example*: `"Ancient enchanted Indian forest, towering mossy banyan roots, golden morning sunbeams cutting through emerald leaves, soft glowing dust motes, 3D Pixar Disney aesthetic, 9:16 vertical composition, 8k resolution."`

### 4. Shot Progression & Dynamic Angles 🎬:
Consecutive scenes must NEVER share identical camera framing:
- **Scene 1**: Establishing Low-Angle / Dynamic Action Hook
- **Scene 2**: Medium Eye-Level / Character Interaction & Discovery
- **Scene 3**: High-Tension Action / Over-the-Shoulder / Conflict
- **Scene 4**: Dramatic Close-Up / Emotional Turning Point / Magic Miracle
- **Scene 5**: Sweeping Hero Wide Shot / Celebratory Resolution & Circular Loop

---

## 3. Strict Storyboard Output Contract (Valid JSON Only) 🛡️

Output **ONLY valid JSON** conforming to this schema:

```json
{
  "title": "शिकारी का जाल उड़ा ले गए कबूतर! 🕊️🕸️ Unity is Strength | 3D Hindi Kahaniya #Shorts",
  "total_hindi_words": 76,
  "hook_variants": {
    "A": "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में कैसे फंसा दिया? 🌾🕸️",
    "B": "शिकारी के मजबूत लोहे के जाल को कबूतरों ने एक झटके में कैसे उड़ा दिया? 🕊️💨"
  },
  "hook_type": "High-Stakes Crisis & Unity Miracle",
  "loop_connection": "Final sentence '...वो भूल जाता है कि कैसे' connects seamlessly into opening hook",
  "character_anchor": "Chiku, a noble pearl-grey elder dove with shimmering emerald neck feathers, and Miku, an adorable nimble field mouse with oversized round ears",
  "world_anchor": "Ancient Indian banyan forest, mossy roots, glowing morning sunbeams, terracotta ground, vibrant 3D Pixar aesthetic, 9:16 vertical, 8k resolution",
  "story_moral": "एकता में ही सबसे बड़ी शक्ति है।",
  "pinned_comment_question": "🕊️ क्या आपने कभी देखा है कि मिल-जुलकर काम करने से बड़ी मुसीबत हल हो गई? Comments में बताएं! 👇❤️",
  "self_declared_made_for_kids": false,
  "audience_decision_note": "Family folklore animated special positioned for co-viewing; comments unlocked.",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️",
      "narration_en": "Golden grains scattered in the forest trapped the flock of doves in a heavy net! 🌾🕸️",
      "visual": "A flock of adorable 3D Pixar-style pearl-grey doves landing on terracotta soil as a heavy dark hemp rope net suddenly drops over them, dramatic low-angle shot, golden morning sunbeams, 9:16 vertical framing, Octane render, 3D Pixar style",
      "sfx_cue": "[0.0s Heavy Net Whoosh], [1.2s Fluttering Wing Panics]",
      "music_mood": "Sudden suspenseful string swell, fast tempo (115 BPM), tense bansuri trill"
    },
    {
      "scene_number": 2,
      "narration": "सब डर के मारे अलग-अलग भागने लगे! 😰 तभी चीकू चिल्लाया—'अकेले नहीं, एक साथ जोर लगाओ!' 🕊️✨",
      "narration_en": "Everyone panicked in different directions! 😰 Then Chiku shouted—'Not alone, pull together!' 🕊️✨",
      "visual": "Medium close-up inside the trapped net, Chiku the noble elder dove with outstretched wings shouting encouragement to frightened cute baby doves, warm amber rim lighting, 9:16 vertical",
      "sfx_cue": "[0.3s Frantic Wing Beats], [1.5s Brave Chirp Call]",
      "music_mood": "Building orchestral percussion, rising brass optimism"
    },
    {
      "scene_number": 3,
      "narration": "एक, दो, तीन! सबने एक ही पल में पंख फड़फड़ाए! 🦅💨 और चमत्कार हुआ—पूरा जाल बादलों में उड़ने लगा! ☁️✨",
      "narration_en": "One, two, three! Synchronized wings flapped together, and the entire net soared into the sky! ☁️✨",
      "visual": "Dynamic upward low-angle heroic action shot, united flock of doves flapping synchronized wings lifting the heavy net off the ground soaring into turquoise sky, swirling leaves, 9:16 vertical",
      "sfx_cue": "[0.0s 1-2-3 Countdown Riser], [1.0s Giant Wind Gust], [2.2s Magical Chime]",
      "music_mood": "Triumphant Indian flute melody, upbeat dholak groove (120 BPM)"
    },
    {
      "scene_number": 4,
      "narration": "शिकारी मुंह खोले देखता ही रह गया! 🏹😲 कबूतर सीधे अपने सच्चे मित्र, नन्हे चूहे मीकू के पास पहुंचे! 🐭⛰️",
      "narration_en": "The hunter watched in astonishment! 🏹😲 The doves flew straight to their true friend, Miku the mouse! 🐭⛰️",
      "visual": "Wide cinematic shot of the rustic Indian hunter standing frozen in shock with bow lowered, watching net fly toward a sunlit rocky hill where cute tiny mouse watches, 9:16 vertical",
      "sfx_cue": "[0.5s Comedic Cartoon Gulp], [1.8s Rapid Mouse Squeak]",
      "music_mood": "Playful pizzicato strings and playful tabla beats"
    },
    {
      "scene_number": 5,
      "narration": "नन्हे चूहे के तेज दांतों ने सारे फंदे पलक झपकते ही काट डाले! 🐭✂️ और जब भी कोई शिकारी जाल बिछाता है, वो भूल जाता है कि कैसे...",
      "narration_en": "Miku's sharp teeth sliced the ropes in an instant! 🐭✂️ And whenever a hunter spreads a net, he forgets that...",
      "visual": "Extreme close-up heroic shot of Miku the adorable field mouse happily gnawing the last thick rope, doves bursting into joyful flight into rainbow sunset sky, 9:16 vertical",
      "sfx_cue": "[0.2s Rapid Rope Snips], [1.4s Celebratory Chimes & Cheerful Dove Coos]",
      "music_mood": "Joyful crescendo, uplifting shehnai flourish looping into opening hook"
    }
  ]
}
```

---

## 4. Pre-Flight Validator Check & Mandatory User Approval 🛑

Always run the storyboard validator before requesting user approval:
```powershell
python -u backend/scripts/storyboard_validator.py --json "backend/output/<story_dir>/script.json"
```

### Pre-Flight Rule Checklist:
1. **Scene Count**: 5 to 6 scenes.
2. **Word Count**: 70 to 85 Hindi words (14–16 words/scene).
3. **No Banned Outros**: Zero lecturing phrases.
4. **Visual Safety**: 9:16 vertical, no banned text tokens, explicit camera and lighting signals.
5. **Approval Gateway**: Present validated report and wait for user confirmation before launching any image generation.

---

## 5. The 11-Item Content Package Deliverable 📦

Every completed creative story produces:
1. Viral Topic & Psychological Hook Angle
2. Hook Variants (A & B)
3. Full Narration Script (Devanagari Hindi)
4. English Captions (`narration_en`)
5. Character Anchor & Series Bible Update
6. 9:16 Visual Prompts (with lighting & camera cues)
7. Audio & SFX Cues (timestamped Foley + music mood)
8. YouTube Title (≤ 95 chars)
9. Top-of-Description Hashtag Cloud + 3-Sentence Summary
10. Competitor-Benchmarked 3-Tier Tags (≤ 380 chars)
11. Pinned Engagement Question Comment

---

## 6. Seasonal & Trend Calendar 🗓️

Plan festival stories **7 to 10 days ahead** of the observance window:

| Window | Cultural Festival / Event | Core Story Theme |
|---|---|---|
| **Late Oct / Early Nov** | Diwali & Dhanteras | Light vs darkness, humble pottery, golden diya, sharing sweets |
| **Early Nov** | Chhath Puja | Sun offering (*Arghya*), river purity, Thekua prasad, maternal devotion |
| **14 November** | Children's Day | Chintu's playful curiosity, bravery, kindness to animals |
| **Dec / Jan** | Winter & Makar Sankranti | Warmth, kite flying in village sky, sharing sesame sweets |
| **March** | Holi | Colors of friendship, forgiving enemies, joyous forest celebration |
| **Aug / Sep** | Krishna Janmashtami & Ganesh | Little Krishna's butter pot, wisdom of Ganesha, playful karma |
