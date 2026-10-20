import { Music, Volume2, Sparkles, Users } from 'lucide-react';

export default function ConfigPanel({
  voiceAccent,
  setVoiceAccent,
  musicTrack,
  setMusicTrack,
  captionStyle,
  setCaptionStyle,
  musicVolume,
  setMusicVolume,
  videoResolution,
  setVideoResolution,
  isDialogueMode,
  setIsDialogueMode,
  voiceA,
  setVoiceA,
  voiceB,
  setVoiceB,
  transitionStyle,
  setTransitionStyle
}) {
  const voiceOptions = (
    <>
      <optgroup label="🇮🇳 Indian English">
        <option value="in_female">English (Female) — Neerja</option>
        <option value="in_male">English (Male) — Prabhat</option>
      </optgroup>
      <optgroup label="🗣️ Hindi">
        <option value="hi_female">Hindi (Female) — Swara</option>
        <option value="hi_male">Hindi (Male) — Madhur</option>
      </optgroup>
      <optgroup label="🗣️ Bengali">
        <option value="bn_female">Bengali (Female) — Tanishaa</option>
        <option value="bn_male">Bengali (Male) — Bashkar</option>
      </optgroup>
      <optgroup label="🗣️ Punjabi">
        <option value="pa_female">Punjabi (Female) — Vaani</option>
        <option value="pa_male">Punjabi (Male) — Ojas</option>
      </optgroup>
      <optgroup label="🗣️ Bhojpuri (Hindi base)">
        <option value="bho_female">Bhojpuri (Female)</option>
        <option value="bho_male">Bhojpuri (Male)</option>
      </optgroup>
      <optgroup label="👶 Child Tone">
        <option value="child_english">Child — English</option>
        <option value="child_hindi">Child — Hindi</option>
      </optgroup>
      <optgroup label="🎧 Embedded Storyteller (Offline CPU)">
        <option value="kittentts">KittenTTS — Warm Bedtime Story (English)</option>
      </optgroup>
    </>
  );

  return (
    <div className="space-y-6">
      {/* Dialogue Mode & Transition Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-6 border-t border-gray-800/80">
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-indigo-400" /> Narration Mode:
          </label>
          <div className="inline-flex rounded-xl p-1 bg-gray-950 border border-gray-800">
            <button
              type="button"
              onClick={() => setIsDialogueMode(false)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                !isDialogueMode
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              🎙️ Solo Voice
            </button>
            <button
              type="button"
              onClick={() => setIsDialogueMode(true)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                isDialogueMode
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              👥 2-Character Dialogue
            </button>
          </div>
        </div>

        {/* Transition Style Selector */}
        <div className="flex items-center gap-2">
          <label htmlFor="transition-style" className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Transitions:
          </label>
          <select
            id="transition-style"
            className="rounded-xl border-0 bg-gray-950 py-1.5 px-3 text-xs text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 cursor-pointer transition-all"
            value={transitionStyle}
            onChange={(e) => setTransitionStyle(e.target.value)}
          >
            <option value="dynamic">✨ Dynamic Auto-Mix</option>
            <option value="whip_pan">🚀 Whip Pan Sweep</option>
            <option value="dissolve">🌫️ Blur Crossfade</option>
            <option value="flash">⚡ Lens Impact Flash</option>
            <option value="slide">📲 Directional Slide</option>
            <option value="none">✂️ Hard Direct Cut</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-2">
        {/* Voice Selection: Solo vs Dialogue */}
        {!isDialogueMode ? (
          <div className="space-y-2">
            <label htmlFor="voice-accent" className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
              🎙️ Neural Character Voice
            </label>
            <select
              id="voice-accent"
              className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-4 text-sm text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 cursor-pointer transition-all"
              value={voiceAccent}
              onChange={(e) => setVoiceAccent(e.target.value)}
            >
              {voiceOptions}
            </select>
          </div>
        ) : (
          <div className="space-y-2 md:col-span-2 grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="voice-a" className="text-xs font-semibold tracking-wider uppercase text-cyan-400 flex items-center gap-1">
                👧 Character A (Female)
              </label>
              <select
                id="voice-a"
                className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-3 text-xs text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-cyan-500 cursor-pointer transition-all"
                value={voiceA}
                onChange={(e) => setVoiceA(e.target.value)}
              >
                {voiceOptions}
              </select>
            </div>
            <div>
              <label htmlFor="voice-b" className="text-xs font-semibold tracking-wider uppercase text-amber-400 flex items-center gap-1">
                👦 Character B (Male)
              </label>
              <select
                id="voice-b"
                className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-3 text-xs text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-amber-500 cursor-pointer transition-all"
                value={voiceB}
                onChange={(e) => setVoiceB(e.target.value)}
              >
                {voiceOptions}
              </select>
            </div>
          </div>
        )}

        {/* Background Music Track */}
        <div className="space-y-2">
          <label htmlFor="music-track" className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
            <Music className="w-3.5 h-3.5 text-gray-400" /> Soundtrack
          </label>
          <select
            id="music-track"
            className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-4 text-sm text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 cursor-pointer transition-all"
            value={musicTrack}
            onChange={(e) => setMusicTrack(e.target.value)}
          >
            <option value="none">🔇 Muted (Voice-Only)</option>
            <option value="lofi">🎵 Chilled Chill Lofi</option>
            <option value="upbeat">⚡ High Upbeat Energy</option>
          </select>
        </div>

        {/* Subtitle / Caption Style */}
        <div className="space-y-2">
          <label htmlFor="caption-style" className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
            💬 Subtitle Style
          </label>
          <select
            id="caption-style"
            className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-4 text-sm text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 cursor-pointer transition-all"
            value={captionStyle}
            onChange={(e) => setCaptionStyle(e.target.value)}
          >
            <option value="tiktok">💥 TikTok Word Highlight (Centered)</option>
            <option value="viral">🔥 Viral Hype (Alex Hormozi Style + Emojis)</option>
            <option value="elegant">📖 Elegant Bottom Block (Centered)</option>
          </select>
        </div>

        {/* Video Output Resolution */}
        <div className="space-y-2">
          <label htmlFor="video-resolution" className="text-xs font-semibold tracking-wider uppercase text-gray-400 flex items-center gap-1.5">
            🎬 Video Resolution
          </label>
          <select
            id="video-resolution"
            className="mt-1 block w-full rounded-2xl border-0 bg-gray-950 py-3.5 px-4 text-sm text-gray-200 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 cursor-pointer transition-all"
            value={videoResolution}
            onChange={(e) => setVideoResolution(e.target.value)}
          >
            <option value="1080p">📱 1080p Full HD (Fast)</option>
            <option value="4k">💎 4K Ultra HD (Master Quality)</option>
          </select>
        </div>
      </div>

      {/* Music Volume Control Slider */}
      {musicTrack !== 'none' && (
        <div className="pt-4 border-t border-gray-850 space-y-2">
          <div className="flex justify-between items-center text-xs font-semibold uppercase text-gray-400 tracking-wider">
            <span className="flex items-center gap-1.5">
              <Volume2 className="w-3.5 h-3.5 text-gray-400" /> Soundtrack Volume
            </span>
            <span className="text-indigo-400 font-bold bg-indigo-500/10 px-2 py-0.5 rounded-full">
              {Math.round(parseFloat(musicVolume) * 100)}%
            </span>
          </div>
          <input
            type="range"
            min="0.02"
            max="0.40"
            step="0.01"
            value={musicVolume}
            onChange={(e) => setMusicVolume(e.target.value)}
            className="w-full h-2 bg-gray-950 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
        </div>
      )}
    </div>
  );
}
