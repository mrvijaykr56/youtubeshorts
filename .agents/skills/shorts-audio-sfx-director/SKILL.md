---
name: shorts-audio-sfx-director
description: >-
  Specialized agentic skill to direct, curate, and time scene-by-scene sound effects (SFX)
  and copyright-safe background music (BGM) for MagicalTalesKidz 3D Hindi YouTube Shorts and Reels.
  Integrates exact Foley timestamps, YouTube Audio Library safe track profiles, Indian instrument
  palettes, and broadcast audio ducking standards.
---

# YouTube Shorts Audio & SFX Director Skill (MagicalTalesKidz) 🎵🔊

This skill guides the agent in designing, timing, and curating scene-by-scene sound effects (SFX) and copyright-safe background music (BGM) for high-retention 3D animated YouTube Shorts and Instagram Reels on **@MagicalTalesKidz**.

---

## 1. Core Sound Design Principles for Kids Animation 🎧✨

Children's animated Shorts require tactile, responsive audio feedback to hold sensory attention. Passive or generic music-only shorts suffer high swipe-away rates.

### The 4 Golden Rules of Animation Sound:
1. **Hyper-Tactile Cartoon Physics**: Every physical action (a net dropping, wings flapping, a seed falling, eyes blinking in surprise) MUST have an accompanying sound effect.
2. **Kid-Safe Tone (No Jump Scares)**:
   - ❌ Never use harsh screeching horns, terrifying monster roars, or realistic gunshots/explosions.
   - ✅ Use playful cartoon gulps, wooden pops, bubbly water splashes, and gentle orchestral brass risers.
3. **Exact Timestamp Synchronization**:
   - Cues must specify precise scene-relative seconds (e.g. `[0.0s Net Whoosh]`, `[1.8s Fairy Sparkle Chime]`) so editors and FFmpeg filters can place audio clips with zero drift.
4. **Dialogue Primacy & Frequency Separation**:
   - Narration is king. SFX and music must occupy mid/high or low frequencies that never mask the female/child Hindi TTS voice frequencies (1 kHz – 3.5 kHz).

---

## 2. The 5 Essential SFX Sound Families for Panchatantra Stories 📦

| Sound Family | Typical Usage in Stories | Approved Foley Keywords |
| :--- | :--- | :--- |
| **1. Movement & Air** | Net drops, flying birds, monkey jumps, running animals | `heavy_net_whoosh.wav`, `rapid_wing_flutters.wav`, `bamboo_swoosh_fast.wav`, `comic_jump_boing.wav` |
| **2. Magic & Wonder** | Wish-granting relics, pots multiplying, divine light | `sparkling_glitter_chime.wav`, `enchanted_harp_glissando.wav`, `crystal_bell_ding.wav`, `glowing_stardust_shimmer.wav` |
| **3. Comic Reactions** | Hunter freezing, greedy villain stunned, animal plotting | `cartoon_gulp_bubble.wav`, `comic_eye_blink_pop.wav`, `wooden_jaw_drop_clack.wav`, `cute_monkey_squeak.wav` |
| **4. Tactile & Nature** | Grains falling, rope biting, axe in water, grinding mill | `wheat_seeds_scatter.wav`, `rope_fibers_snap.wav`, `hollow_water_splash.wav`, `ancient_millstone_grind.wav` |
| **5. Atmospheric Beds** | Forest dawn, twilight riverbank, quiet village | `morning_forest_birds_soft.wav`, `gentle_stream_water.wav`, `warm_crickets_night.wav` |

---

## 3. Copyright-Safe Music Curation (YouTube Audio Library) 🛡️🎶

To ensure 100% safety from YouTube Content ID claims, copyright strikes, and ad-revenue sharing penalties, all suggested tracks MUST come from the **YouTube Audio Library** or verified royalty-free Indian classical/folk public domain archives.

### A. Approved Instrumentation Palette:
* **Wonder & Emotion**: Bansuri (North Indian bamboo flute), soft Sarod, or Acoustic Flute.
* **Tension & Comic Pacing**: Light Tabla, Mridangam, or Upbeat Dholak combined with pizzicato cellos and bassoons.
* **Celebration & Triumph**: Shehnai flourish, vibrant Sitar, acoustic guitar strums, and brass stabs.

### B. The 3-Part Short Music Arc (30–38 Seconds Total):
* **Phase 1: The Disruption (0s – 5s)**: Immediate intrigue with light pizzicato strings and a sharp bansuri trill. Tempo: **112–122 BPM**.
* **Phase 2: The Struggle / Climax (5s – 25s)**: Dynamic rhythmic rise with rolling tabla grooves and building horn stabs.
* **Phase 3: The Triumph & Seamless Loop (25s – 35s)**: Upbeat melodic resolution that smoothly cascades back to neutral pitch, ensuring the audio loops naturally into Phase 1.

### Recommended YouTube Audio Library Track Prototypes:
* *Prototype A (Magical / Wonder)*: "Sneaky Snooper" / "Fairytale Waltz" (Orchestral Pizzicato + Woodwinds, 115 BPM).
* *Prototype B (Jungle Adventure / Chase)*: "Village Festival" / "Tabla Groove Express" (Folk Percussion + Bansuri, 120 BPM).
* *Prototype C (Moral / Uplifting)*: "Sunrise at the River" (Acoustic Guitar + Sitar + Flute, 110 BPM).

---

## 4. Audio Ducking & Mastering Standards 🎚️

When assembling audio streams via FFmpeg:
1. **Dialogue Track**: Mastered at `0 dB` (Integrated target ~ `-14 LUFS`).
2. **Background Music Track**:
   - Ducked to `-18 dB` to `-22 dB` while Hindi narration is active.
   - Allowed to swell to `-10 dB` during scene transitions or the final 1.5s loop beat.
3. **SFX Track**:
   - Mixed at `-6 dB` to `-8 dB` so cartoon impacts pop without causing clipping.
4. **Master Limiting**:
   - Filter: `loudnorm=I=-16:TP=-1.5:LRA=11` (matches YouTube Shorts mobile broadcast profile).

---

## 5. Output Format: Scene Audio Cue Sheet

Every production audio plan must output structured JSON conforming to this schema:

```json
{
  "story_title": "Story Title",
  "recommended_bgm_track": "Track Title from YouTube Audio Library",
  "music_genre_and_bpm": "Indian Folk Fusion / 118 BPM",
  "master_instruments": ["Bansuri", "Tabla", "Pizzicato Strings"],
  "ducking_profile": "Speech 0dB, BGM -20dB, SFX -6dB",
  "audio_scenes": [
    {
      "scene_number": 1,
      "time_window": "0.0s - 7.5s",
      "voice_line_hindi": "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️",
      "sfx_events": [
        {"timestamp": "0.0s", "sound": "heavy_hemp_net_whoosh.wav", "description": "Loud cartoon whoosh of falling net"},
        {"timestamp": "1.2s", "sound": "frantic_dove_flutter.wav", "description": "Rapid wing flutters inside enclosed mesh"}
      ],
      "music_transition": "Sudden suspenseful string drop, bansuri trill entering at 1.5s"
    }
  ]
}
```

---

## 6. Example Output 1: Hunter and Pigeons (शिकारी और कबूतर)

```json
{
  "story_title": "शिकारी का जाल उड़ा ले गए कबूतर! (Unity is Strength)",
  "recommended_bgm_track": "Playful Indian Quest (YouTube Audio Library - Royalty Free)",
  "music_genre_and_bpm": "Indian Classical Folk Fusion / 120 BPM",
  "master_instruments": ["Bansuri", "Dholak", "Pizzicato Strings", "Glockenspiel"],
  "ducking_profile": "Speech 0dB, BGM -20dB under voiceover, SFX -6dB, Master Loudnorm I=-16 LUFS",
  "audio_scenes": [
    {
      "scene_number": 1,
      "time_window": "0.0s - 7.0s",
      "voice_line_hindi": "जंगल में बिखरे सुनहरे दानों ने कबूतरों को भारी लोहे के जाल में फंसा दिया! 🌾🕸️",
      "sfx_events": [
        {"timestamp": "0.0s", "sound": "whoosh_net_drop.wav", "description": "Heavy rope net collapsing from above"},
        {"timestamp": "1.4s", "sound": "flock_panic_coo.wav", "description": "Cute panicked bird coos and wing flutter"}
      ],
      "music_transition": "Tense low cello strike followed by frantic bansuri flutter"
    },
    {
      "scene_number": 2,
      "time_window": "7.0s - 14.5s",
      "voice_line_hindi": "सब डर के मारे अलग-अलग भागने लगे! 😰 तभी चीकू चिल्लाया—'अकेले नहीं, एक साथ जोर लगाओ!' 🕊️✨",
      "sfx_events": [
        {"timestamp": "7.2s", "sound": "wing_struggle_fast.wav", "description": "Scattered wings thrashing ropes"},
        {"timestamp": "10.0s", "sound": "brave_whistle_call.wav", "description": "Chiku's noble sharp leader coo"}
      ],
      "music_transition": "Tabla kicks in at 120 BPM with steady determined rhythm"
    },
    {
      "scene_number": 3,
      "time_window": "14.5s - 22.0s",
      "voice_line_hindi": "एक, दो, तीन! सबने एक ही पल में पंख फड़फड़ाए! 🦅💨 और चमत्कार हुआ—पूरा जाल बादलों में उड़ने लगा! ☁️✨",
      "sfx_events": [
        {"timestamp": "14.6s", "sound": "cartoon_count_riser.wav", "description": "Quick 1-2-3 woodblock ascending pitch"},
        {"timestamp": "16.0s", "sound": "powerful_wind_gust.wav", "description": "Huge collective lift-off wind blast"},
        {"timestamp": "18.5s", "sound": "magical_sparkle_chime.wav", "description": "Glistening stardust bell as net airborne"}
      ],
      "music_transition": "Triumphant sitar and brass swell, celebratory full beat"
    },
    {
      "scene_number": 4,
      "time_window": "22.0s - 29.0s",
      "voice_line_hindi": "शिकारी मुंह खोले देखता ही रह गया! 🏹😲 कबूतर सीधे अपने सच्चे मित्र, नन्हे चूहे मीकू के पास पहुंचे! 🐭⛰️",
      "sfx_events": [
        {"timestamp": "22.3s", "sound": "comic_jaw_drop_clack.wav", "description": "Hunter's wooden bow clatters on ground with comic gulp"},
        {"timestamp": "25.5s", "sound": "cute_mouse_squeak_hello.wav", "description": "Cheerful friendly mouse chatter"}
      ],
      "music_transition": "Playful pizzicato strings and comedic bassoon steps"
    },
    {
      "scene_number": 5,
      "time_window": "29.0s - 36.0s",
      "voice_line_hindi": "नन्हे चूहे के तेज दांतों ने सारे फंदे पलक झपकते ही काट डाले! 🐭✂️ और जब भी कोई शिकारी जाल बिछाता है, वो भूल जाता है कि कैसे...",
      "sfx_events": [
        {"timestamp": "29.2s", "sound": "scissors_quick_snip_3x.wav", "description": "Three cartoon-fast rope snips"},
        {"timestamp": "32.0s", "sound": "sky_liberty_chimes.wav", "description": "Soaring magical chimes and happy cooing"}
      ],
      "music_transition": "Grand shehnai flourish resolving to a seamless suspense note that loops into Scene 1"
    }
  ]
}
```

---

## 7. Example Output 2: The Magic Millstone (जादुई चक्की)

```json
{
  "story_title": "जादुई चक्की: जो मांगो वो निकले! (The Magic Millstone)",
  "recommended_bgm_track": "Mystical Bazaar (YouTube Audio Library - Royalty Free)",
  "music_genre_and_bpm": "Playful Mystery / 115 BPM",
  "master_instruments": ["Bansuri", "Tabla", "Santoor", "Pizzicato Strings"],
  "ducking_profile": "Speech 0dB, BGM -20dB, SFX -6dB, Master Loudnorm I=-16 LUFS",
  "audio_scenes": [
    {
      "scene_number": 1,
      "time_window": "0.0s - 7.0s",
      "voice_line_hindi": "जब पत्थर की पुरानी चक्की अपने आप घूमने लगी, तो लालची सेठ की आंखें फटी की फटी रह गईं! 🪨✨",
      "sfx_events": [
        {"timestamp": "0.0s", "sound": "ancient_stone_creak.wav", "description": "Heavy stone mill grinding on its own"},
        {"timestamp": "1.5s", "sound": "cartoon_eye_pop.wav", "description": "Funny cartoon pop for Seth's bulging eyes"}
      ],
      "music_transition": "Mysterious santoor tremolo with bouncy pizzicato rhythm"
    },
    {
      "scene_number": 2,
      "time_window": "7.0s - 14.0s",
      "voice_line_hindi": "सेठ चिल्लाया—'नमक निकाल!' और चक्की से नमकीन चांदी का फव्वारा फूट पड़ा! 🌊🧂",
      "sfx_events": [
        {"timestamp": "7.8s", "sound": "magic_activation_sparkle.wav", "description": "Shimmering glitter chime"},
        {"timestamp": "9.5s", "sound": "salt_stream_waterfall.wav", "description": "Cascading rush of pouring grains"}
      ],
      "music_transition": "Accelerating tabla groove building tension"
    },
    {
      "scene_number": 3,
      "time_window": "14.0s - 21.0s",
      "voice_line_hindi": "पर रुकने का मंत्र किसी को नहीं पता था! पूरी नाव नमक के भारी वजन से डगमगाने लगी! ⛵😱",
      "sfx_events": [
        {"timestamp": "14.5s", "sound": "boat_wood_creak_strain.wav", "description": "Strained wooden boat groaning under load"},
        {"timestamp": "17.0s", "sound": "water_slosh_heavy.wav", "description": "Waves splashing violently over deck"}
      ],
      "music_transition": "Urgent orchestral brass swells with dramatic drum rolls"
    },
    {
      "scene_number": 4,
      "time_window": "21.0s - 28.0s",
      "voice_line_hindi": "छपाक! चक्की सीधे समंदर की गहराई में समा गई और आज भी घूमती रही! 🌊🪨",
      "sfx_events": [
        {"timestamp": "21.2s", "sound": "giant_ocean_splash.wav", "description": "Deep resonant ocean splash with bubbly cartoon plunge"},
        {"timestamp": "24.0s", "sound": "underwater_muffled_grind.wav", "description": "Muffled underwater grinding with bubbles"}
      ],
      "music_transition": "Bubbly underwater filter, gentle flute reprise"
    },
    {
      "scene_number": 5,
      "time_window": "28.0s - 35.0s",
      "voice_line_hindi": "तभी तो समंदर का पानी खारा है! पर लालची लोग हमेशा सोचते हैं कि काश...",
      "sfx_events": [
        {"timestamp": "28.5s", "sound": "ocean_wave_murmur.wav", "description": "Peaceful rolling sea waves"},
        {"timestamp": "32.0s", "sound": "curiosity_chime_loop.wav", "description": "Tinkling bell that suspensefully leads back to Scene 1"}
      ],
      "music_transition": "Playful flute flutter with a suspended acoustic chord looping back into Scene 1"
    }
  ]
}
```
