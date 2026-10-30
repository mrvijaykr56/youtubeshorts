---
name: shorts-script-polisher
description: >-
  Specialized agentic skill to transform raw ideas, topics, articles, or rough drafts into
  high-retention viral YouTube Shorts storyboards for MagicalTalesKidz. Formats output as strict JSON with
  0-3s psychological hooks (banning "एक बार की बात है"), 70-85 Hindi words, rhythmic alternating lines,
  no moral outro, seamless grammatical loop, exact SFX/music cues, and 9:16 visual prompts.
---

# YouTube Shorts Script Polisher & Storyboard Director (MagicalTalesKidz)

This skill guides the agent in crafting high-retention, viral YouTube Shorts scripts and converting them into structured storyboard JSON compatible with the MyVideoWorkspace rendering pipeline for **@MagicalTalesKidz**.

---

## 1. Core Principles of YouTube Shorts Retention for Kids & Parents

### 1. The 3-Second Hook Rule (No Exposition, No "एक बार की बात है") 🛑
- **Strictly Banned Openers**: NEVER start with `"एक बार की बात है"`, `"बहुत समय पहले..."`, or slow character introductions (`"एक सुंदर जंगल में चीकू नाम का एक कबूतर रहता था..."`).
- **Immediate Sensory/Action Hook**: The first 3 seconds MUST drop the viewer into the middle of intense action, an astonishing dilemma, or an impossible mystery:
  - *Banned*: "एक जंगल में बहुत सारे कबूतर रहते थे और एक दिन शिकारी आया।"
  - *Viral (0–3s)*: "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️"
  - *Viral (0–3s)*: "जब नदी में गिरी कुल्हाड़ी, तो जलपरी ने सोने की कुल्हाड़ी क्यों निकाली? 🪓✨"

### 2. Word Count & Rhythmic Alternation (70–85 Hindi Words) 📜
- **Total Word Count**: Strictly **70 to 85 Hindi words** in pure Devanagari script (~30–38 seconds of spoken audio).
  - Fewer than 70 words feels empty and under-developed.
  - More than 85 words breaches comfortable reading speed and rushes the viewer.
- **Alternating Short and Long Lines**: Do not write monotone sentence lengths. Alternate punchy short lines (3–5 words) with descriptive rhythmic lines (9–14 words):
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

### 5. Original Retelling & Cultural Freshness ✍️
- Re-tell classic Panchatantra, Jataka, and folk stories using fresh, original dialogue, vivid sensory details, and child-safe humor.
- Never copy dialogue or scripts verbatim from competitor channels or copyrighted books.

### 6. Subtitle Emojis 🎭
- Embed 1–2 contextually relevant emojis in each narration line (`🕊️`, `🕸️`, `✨`, `🐭`). The rendering engine maps these into karaoke-style animated subtitles while TTS audio cleanly speaks the Hindi words.

---

## 2. Character DNA & World Consistency Framework 👥🌍

### 1. The Channel Mascot Anchor: Chintu the Monkey (चिंटू बंदर) 🐒✨
When the story features or is introduced by the channel mascot, enforce the immutable mascot anchor:
- **Character DNA**: `"Chintu, an adorable 3D Pixar-style golden-brown Indian monkey mascot, huge expressive warm amber eyes, soft cream-colored tummy and muzzle, wearing a tiny red festive vest with gold trim, bouncy curled tail, emotive floppy ears, lively and playful gestures."`

### 2. World & Lighting Anchor:
Every story must establish a shared atmospheric anchor prepended across prompts:
- *Example*: `"Ancient enchanted Indian forest, towering mossy banyan roots, golden morning sunbeams cutting through emerald leaves, soft glowing dust motes, 3D Pixar Disney aesthetic, 9:16 vertical composition, 8k resolution."`

---

## 3. Strict Storyboard Output Contract (Valid JSON Only) 🛡️

When polishing or generating a script, you MUST output **ONLY valid JSON** conforming to this exact schema. Do not prepend or append markdown conversational commentary outside the JSON block.

```json
{
  "title": "शिकारी का जाल उड़ा ले गए कबूतर! 🕊️🕸️ Unity is Strength | 3D Hindi Kahaniya #Shorts",
  "total_hindi_words": 76,
  "hook_type": "High-Stakes Crisis (Net Collapse)",
  "loop_connection": "Final sentence '...वो भूल जाता है कि कैसे' connects seamlessly into opening 'जंगल में बिखरे सुनहरे दानों ने...'",
  "character_anchor": "Chiku, a noble pearl-grey elder dove with shimmering emerald neck feathers, and Miku, an adorable nimble field mouse with oversized round ears",
  "world_anchor": "Ancient Indian banyan forest, mossy roots, glowing morning sunbeams, terracotta ground, vibrant 3D Pixar aesthetic, 9:16 vertical",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️",
      "visual": "A flock of adorable 3D Pixar-style pearl-grey doves landing on terracotta soil as a heavy dark hemp rope net suddenly drops over them, dramatic low-angle shot, golden morning sunbeams, 9:16 vertical framing, Octane render",
      "sfx_cue": "[0.0s Heavy Net Whoosh], [1.2s Fluttering Wing Panics]",
      "music_mood": "Sudden suspenseful string swell, fast tempo (115 BPM), tense bansuri trill"
    },
    {
      "scene_number": 2,
      "narration": "सब डर के मारे अलग-अलग भागने लगे! 😰 तभी चीकू चिल्लाया—'अकेले नहीं, एक साथ जोर लगाओ!' 🕊️✨",
      "visual": "Medium close-up inside the trapped net, Chiku the noble elder dove with outstretched wings shouting encouragement to frightened cute baby doves, warm amber rim lighting, 9:16 vertical",
      "sfx_cue": "[0.3s Frantic Wing Beats], [1.5s Brave Chirp Call]",
      "music_mood": "Building orchestral percussion, rising brass optimism"
    },
    {
      "scene_number": 3,
      "narration": "एक, दो, तीन! सबने एक ही पल में पंख फड़फड़ाए! 🦅💨 और चमत्कार हुआ—पूरा जाल बादलों में उड़ने लगा! ☁️✨",
      "visual": "Dynamic upward low-angle heroic action shot, united flock of doves flapping synchronized wings lifting the heavy net off the ground soaring into turquoise sky, swirling leaves, 9:16 vertical",
      "sfx_cue": "[0.0s 1-2-3 Countdown Riser], [1.0s Giant Wind Gust], [2.2s Magical Chime]",
      "music_mood": "Triumphant Indian flute melody, upbeat dholak groove (120 BPM)"
    },
    {
      "scene_number": 4,
      "narration": "शिकारी मुंह खोले देखता ही रह गया! 🏹😲 कबूतर सीधे अपने सच्चे मित्र, नन्हे चूहे मीकू के पास पहुंचे! 🐭⛰️",
      "visual": "Wide cinematic shot of the rustic Indian hunter standing frozen in shock with bow lowered, watching net fly toward a sunlit rocky hill where cute tiny mouse watches, 9:16 vertical",
      "sfx_cue": "[0.5s Comedic Cartoon Gulp], [1.8s Rapid Mouse Squeak]",
      "music_mood": "Playful pizzicato strings and playful tabla beats"
    },
    {
      "scene_number": 5,
      "narration": "नन्हे चूहे के तेज दांतों ने सारे फंदे पलक झपकते ही काट डाले! 🐭✂️ और जब भी कोई शिकारी जाल बिछाता है, वो भूल जाता है कि कैसे...",
      "visual": "Extreme close-up heroic shot of Miku the adorable field mouse happily gnawing the last thick rope, doves bursting into joyful flight into rainbow sunset sky, 9:16 vertical",
      "sfx_cue": "[0.2s Rapid Rope Snips], [1.4s Celebratory Chimes & Cheerful Dove Coos]",
      "music_mood": "Joyful crescendo, uplifting shehnai flourish looping into suspense"
    }
  ],
  "pinned_comment_question": "🕊️ क्या आपने कभी देखा है कि मिल-जुलकर काम करने से बड़ी मुसीबत हल हो गई? Comments में बताएं! 👇❤️",
  "self_declared_made_for_kids": false
}
```

---

## 4. Top 10 Competitor SEO & Metadata Package 🏆

Every storyboard generated for MagicalTalesKidz must also bundle competitor-benchmarked metadata:

### 1. Title Formula ($\le 95$ Characters)
`[Emotional Hook in Hindi + 1-2 Emojis] [English Name] | 3D Hindi Kahaniya #Shorts`
- *Example*: `शिकारी का जाल उड़ा ले गए कबूतर! 🕊️🕸️ Unity is Strength | 3D Hindi Kahaniya #Shorts` (89 chars)

### 2. Description Blueprint
```text
#Shorts #HindiKahaniya #MoralStories #Panchatantra #[StoryKeyword] #3DAnimation #HindiCartoon #BalKahani

[2-3 sentence engaging story summary in Hindi without moral lecture]

🎬 Watch All 3D Hindi Stories in Official Playlist:
https://www.youtube.com/playlist?list=PLJE6ifX-QD0A

🔔 Subscribe to @MagicalTalesKidz for Daily 3D Magical Stories:
https://www.youtube.com/@MagicalTalesKidz?sub_confirmation=1

#Shorts #HindiKahaniya #MoralStories #Panchatantra #KidsAnimation
```

### 3. Tag Architecture ($\le 380$ Characters)
1. **Story Tags (5–7)**: Story name, characters, transliterated Hindi.
2. **High-Volume Anchor Tags (8–10)**: `"Hindi Kahaniya"`, `"moral stories in hindi"`, `"panchatantra stories"`, `"kids moral stories"`, `"3d animated stories"`, `"hindi cartoon"`, `"bal kahaniya"`, `"jadui kahaniya"`, `"stories for kids"`, `"shorts"`, `"yt shorts"`.
3. **Devanagari Dual-Script Tags (4–5)**: `"हिंदी कहानियां"`, `"पंचतंत्र की कहानियां"`, `"नैतिक कहानियां"`, `"हिंदी कार्टून"`.
