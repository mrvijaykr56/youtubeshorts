import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RefreshCw, Edit3, Check, X, Upload, Download,
  Share2, AlertCircle, CheckCircle2, Loader2,
  ChevronDown, ChevronUp, Copy, Sparkles, Film,
  Sliders, Music, Volume2, Users, Video, Play, ExternalLink
} from 'lucide-react';
import './App.css';

import VideoToVideoStudio from './components/VideoToVideoStudio';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// ── Voice Options ────────────────────────────────────────────────────────────
const VOICE_OPTIONS = [
  { value: 'in_female', label: 'English (Female) — Neerja', group: '🇮🇳 Indian English' },
  { value: 'in_male',   label: 'English (Male) — Prabhat',   group: '🇮🇳 Indian English' },
  { value: 'hi_female', label: 'Hindi (Female) — Swara',     group: '🗣️ Hindi' },
  { value: 'hi_male',   label: 'Hindi (Male) — Madhur',      group: '🗣️ Hindi' },
  { value: 'us',        label: 'US English — Professional',  group: '🇺🇸 English' },
  { value: 'bn_female', label: 'Bengali (Female) — Tanishaa', group: '🗣️ Regional' },
  { value: 'pa_female', label: 'Punjabi (Female) — Vaani',   group: '🗣️ Regional' },
  { value: 'child_english', label: 'Child Tone (English)',   group: '👶 Special' },
];

const ART_STYLES = [
  { id: 'cinematic',   name: 'Cinematic',   icon: '🎬', desc: 'Photorealistic, dramatic' },
  { id: 'pixar',       name: 'Pixar 3D',    icon: '🧸', desc: 'Vibrant soft clay' },
  { id: 'anime',       name: 'Anime',       icon: '🌸', desc: 'Makoto Shinkai style' },
  { id: 'cyberpunk',   name: 'Cyberpunk',   icon: '🌌', desc: 'Neon synthwave glow' },
  { id: 'oil_painting',name: 'Oil Paint',   icon: '🎨', desc: 'Classical canvas' },
];

const STORY_STARTERS = [
  { label: '🧠 Mind-Blowing Fact',  text: 'Did you know that honey never expires? Archaeologists have found 3000-year-old honey in Egyptian tombs — still perfectly edible. Why does honey last forever while everything else rots?' },
  { label: '📜 Ancient Mystery',    text: 'The Great Pyramid of Giza was built with over 2.3 million stone blocks, each weighing up to 80 tons. Modern engineers still cannot fully explain how ancient Egyptians transported and placed them with such precision.' },
  { label: '😂 Everyday Comedy',    text: 'आज सुबह जब मैंने अपना स्कूल बैग उठाया तो लगा जैसे उसमें किताबों के साथ-साथ सब्ज़ी मंडी भी रखी हो। बैग की ज़िप खोली तो अंदर से तीन पेंसिलें, दो रबर, और एक आधा खाया हुआ समोसा निकला!' },
  { label: '🚀 Future Tech',        text: 'Scientists are developing brain-computer interfaces that let paralyzed patients control computers with their thoughts alone. Within 10 years, we may be able to send emotions and memories directly from one brain to another.' },
];

const PIPELINE_STEPS = [
  { name: 'Script Polish', icon: '✍️' },
  { name: 'Voice Synth',   icon: '🎙️' },
  { name: 'Subtitles',     icon: '💬' },
  { name: 'Scene Art',     icon: '🖼️' },
  { name: 'Render',        icon: '🎬' },
];

function getActiveStep(status, progress) {
  if (status === 'generating_storyboard') return progress < 20 ? 0 : 3;
  if (progress < 35) return 1;
  if (progress < 60) return 2;
  if (progress < 65) return 3;
  return 4;
}

// ── VoiceSelect Component ───────────────────────────────────────────────────
function VoiceSelect({ id, value, onChange }) {
  const groups = [...new Set(VOICE_OPTIONS.map(v => v.group))];
  return (
    <select id={id} value={value} onChange={e => onChange(e.target.value)} className="lemon-input w-full">
      {groups.map(g => (
        <optgroup key={g} label={g}>
          {VOICE_OPTIONS.filter(v => v.group === g).map(v => (
            <option key={v.value} value={v.value}>{v.label}</option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}

// ── TopNav Header ────────────────────────────────────────────────────────────
function TopNav({ phase, onReset, studioTab, setStudioTab }) {
  const phases = ['01 Concept', '02 Storyboard', '03 Export'];
  const phaseIdx = phase === 'concept' ? 0 : phase === 'storyboard' ? 1 : 2;

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200 px-4 sm:px-8 py-3 flex items-center justify-between shadow-xs">
      {/* Brand Logo */}
      <div className="flex items-center gap-3">
        <div style={{ background: '#D4F84A', borderRadius: '12px', padding: '6px 10px', fontSize: '20px', lineHeight: 1 }}>
          🍋
        </div>
        <div>
          <span className="font-extrabold text-base text-slate-900 tracking-tight">
            Shorts Studio AI
          </span>
          <span className="ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 uppercase tracking-wider">
            Pro 4K/8K
          </span>
        </div>
      </div>

      {/* Mode Switcher Tabs */}
      <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
        <button
          onClick={() => setStudioTab('video_to_video')}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
            studioTab === 'video_to_video'
              ? 'bg-white text-slate-900 shadow-xs'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          <span>🎬</span>
          <span>Video-to-Video</span>
        </button>
        <button
          onClick={() => setStudioTab('image_to_video')}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
            studioTab === 'image_to_video'
              ? 'bg-white text-slate-900 shadow-xs'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          <span>🖼️</span>
          <span>Image-to-Video</span>
        </button>
      </div>

      {/* Phase Stepper (Image Mode) */}
      <div className="hidden md:flex items-center gap-3">
        {phases.map((p, idx) => (
          <div key={p} className="flex items-center gap-2">
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-lg transition-all ${
                phaseIdx === idx
                  ? 'bg-slate-900 text-white'
                  : phaseIdx > idx
                  ? 'text-emerald-700 bg-emerald-50 font-semibold'
                  : 'text-slate-400'
              }`}
            >
              {p}
            </span>
            {idx < phases.length - 1 && <span className="text-slate-300">/</span>}
          </div>
        ))}
      </div>

      {/* Reset */}
      <button
        onClick={onReset}
        className="text-xs font-semibold text-slate-500 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
      >
        New Project
      </button>
    </header>
  );
}

export default function App() {
  const [studioTab, setStudioTab] = useState('video_to_video'); // 'video_to_video' | 'image_to_video'
  const [script, setScript] = useState('');
  const [status, setStatus] = useState('idle'); // idle, generating_storyboard, storyboard_ready, compiling, completed, error
  const [jobId, setJobId] = useState(null);
  const [progressText, setProgressText] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [videoUrl, setVideoUrl] = useState(null);
  const [polishedScript, setPolishedScript] = useState(null);

  // Studio Settings
  const [voiceAccent, setVoiceAccent] = useState('in_female');
  const [musicTrack, setMusicTrack] = useState('lofi');
  const [musicVolume, setMusicVolume] = useState('0.12');
  const [captionStyle, setCaptionStyle] = useState('tiktok');
  const [artStyle, setArtStyle] = useState('cinematic');
  const [captionLang, setCaptionLang] = useState('English');
  const [videoMode, setVideoMode] = useState('shorts'); // 'shorts' | 'tutorial'
  const [videoResolution, setVideoResolution] = useState('4k'); // '1080p' | '4k' | '8k'
  const [transitionStyle, setTransitionStyle] = useState('dynamic');

  // Dialogue Mode
  const [isDialogueMode, setIsDialogueMode] = useState(false);
  const [voiceA, setVoiceA] = useState('in_female');
  const [voiceB, setVoiceB] = useState('in_male');

  // Storyboard editing
  const [storyboardScenes, setStoryboardScenes] = useState(null);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  const pollingTimeoutRef = useRef(null);

  // Determine current phase: 'concept' | 'storyboard' | 'export'
  const currentPhase =
    status === 'completed'
      ? 'export'
      : storyboardScenes && storyboardScenes.length > 0
      ? 'storyboard'
      : 'concept';

  const handleReset = () => {
    if (pollingTimeoutRef.current) clearTimeout(pollingTimeoutRef.current);
    setStatus('idle');
    setScript('');
    setJobId(null);
    setVideoUrl(null);
    setPolishedScript(null);
    setStoryboardScenes(null);
    setProgressPercent(0);
    setProgressText('');
  };

  // Poll Job Status
  const pollStatus = async (currentJobId) => {
    if (!currentJobId) return;
    try {
      const res = await axios.get(`${API_BASE_URL}/status/${currentJobId}`);
      const data = res.data;
      setProgressText(data.message || 'Processing...');
      if (data.progress !== undefined) setProgressPercent(data.progress);

      if (data.polished_script) {
        setPolishedScript(data.polished_script);
        try {
          const parsed = JSON.parse(data.polished_script);
          setStoryboardScenes(parsed.get ? parsed.get('scenes', parsed) : parsed);
        } catch { /* ignore */ }
      }

      if (data.state === 'storyboard_ready') {
        setStatus('storyboard_ready');
        setProgressPercent(100);
        return;
      } else if (data.state === 'completed') {
        setStatus('completed');
        setProgressPercent(100);
        setVideoUrl(`${API_BASE_URL}/download/${currentJobId}.mp4`);
        return;
      } else if (data.state === 'error') {
        setStatus('error');
        return;
      }

      pollingTimeoutRef.current = setTimeout(() => pollStatus(currentJobId), 2000);
    } catch (err) {
      console.warn('Poll error, retrying:', err);
      pollingTimeoutRef.current = setTimeout(() => pollStatus(currentJobId), 3000);
    }
  };

  // Generate Storyboard Draft
  const handleGenerateStoryboard = async () => {
    if (!script.trim()) return;
    setStatus('generating_storyboard');
    setProgressText('Polishing script and generating 9:16 background scenes...');
    setProgressPercent(10);
    setStoryboardScenes(null);

    try {
      const payload = {
        script: script.trim(),
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        voice_a: voiceA,
        voice_b: voiceB,
        transition_style: transitionStyle,
        music_track: musicTrack,
        caption_style: captionStyle,
        caption_lang: captionLang,
        art_style: artStyle,
        music_volume: parseFloat(musicVolume),
        video_mode: isDialogueMode ? 'dialogue' : videoMode,
        video_resolution: videoResolution
      };

      const res = await axios.post(`${API_BASE_URL}/storyboard`, payload);
      const newJobId = res.data.job_id;
      setJobId(newJobId);
      pollStatus(newJobId);
    } catch (err) {
      console.error(err);
      setStatus('error');
      setProgressText('Failed to start storyboard generation. Check backend.');
    }
  };

  // Compile Final Master Video
  const handleCompileVideo = async () => {
    if (!jobId || !storyboardScenes) return;
    setStatus('compiling');
    setProgressText('Compiling final video with audio sync, transitions, and subtitles...');
    setProgressPercent(20);

    try {
      const payload = {
        job_id: jobId,
        scenes: storyboardScenes,
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        music_track: musicTrack,
        caption_style: captionStyle,
        caption_lang: captionLang,
        music_volume: parseFloat(musicVolume),
        video_resolution: videoResolution,
        transition_style: transitionStyle
      };

      await axios.post(`${API_BASE_URL}/compile`, payload);
      pollStatus(jobId);
    } catch (err) {
      console.error(err);
      setStatus('error');
      setProgressText('Failed to compile video.');
    }
  };

  // Regenerate Single Scene Image
  const handleRegenerateScene = async (idx, prompt) => {
    setRegeneratingIndex(idx);
    try {
      const res = await axios.post(`${API_BASE_URL}/regenerate-image`, {
        job_id: jobId,
        scene_index: idx,
        prompt: prompt,
        art_style: artStyle
      });
      if (res.data.success) {
        const updated = [...storyboardScenes];
        updated[idx].image_url = `${API_BASE_URL}${res.data.image_url}?t=${Date.now()}`;
        setStoryboardScenes(updated);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to regenerate image.');
    } finally {
      setRegeneratingIndex(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <TopNav
        phase={currentPhase}
        onReset={handleReset}
        studioTab={studioTab}
        setStudioTab={setStudioTab}
      />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8 space-y-8">
        {/* Render Video-to-Video Studio when tab is active */}
        {studioTab === 'video_to_video' ? (
          <VideoToVideoStudio />
        ) : (
          /* Image-to-Video Studio */
          <div className="space-y-8">
            {/* Phase 01: Concept & Setup */}
            {currentPhase === 'concept' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Hero Banner */}
                <div className="text-center space-y-2 py-4">
                  <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                    Create High-Retention YouTube Shorts
                  </h1>
                  <p className="text-sm text-slate-500 max-w-xl mx-auto">
                    Turn any raw idea or topic into a viral 9:16 vertical short powered by Neural TTS, 
                    AI scene art, and TikTok kinetic subtitles.
                  </p>
                </div>

                {/* Story Starters */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                    Quick Story Starters
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {STORY_STARTERS.map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() => setScript(s.text)}
                        className="p-2.5 rounded-xl bg-white border border-slate-200 hover:border-slate-400 text-left transition-all cursor-pointer shadow-xs hover:shadow-sm"
                      >
                        <span className="text-xs font-bold text-slate-900 block truncate">{s.label}</span>
                        <p className="text-[11px] text-slate-500 line-clamp-2 mt-1 leading-snug">{s.text}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Main Script Box */}
                <div className="lemon-card p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-bold text-slate-900">Script / Topic Draft</label>
                    <span className="text-xs text-slate-400 font-medium">
                      {script.trim().split(/\s+/).filter(Boolean).length} words
                    </span>
                  </div>

                  <textarea
                    rows={4}
                    value={script}
                    onChange={(e) => setScript(e.target.value)}
                    placeholder="Enter your short story, facts, or topic draft here (English, Hindi, or Hinglish)..."
                    className="w-full lemon-input resize-none text-sm leading-relaxed"
                  />

                  {/* Mode & Voice Controls */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                    {/* Voice Selection */}
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <label className="text-xs font-bold text-slate-700">Narrator Voice</label>
                        <button
                          type="button"
                          onClick={() => setIsDialogueMode(!isDialogueMode)}
                          className={`text-[11px] font-bold px-2 py-0.5 rounded cursor-pointer transition-colors ${
                            isDialogueMode ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          👥 {isDialogueMode ? 'Dialogue Active' : 'Enable Dialogue'}
                        </button>
                      </div>

                      {isDialogueMode ? (
                        <div className="grid grid-cols-2 gap-2">
                          <VoiceSelect id="voiceA" value={voiceA} onChange={setVoiceA} />
                          <VoiceSelect id="voiceB" value={voiceB} onChange={setVoiceB} />
                        </div>
                      ) : (
                        <VoiceSelect id="voiceSelect" value={voiceAccent} onChange={setVoiceAccent} />
                      )}
                    </div>

                    {/* Format Toggle */}
                    <div className="space-y-1.5">
                      <label className="text-xs font-bold text-slate-700">Format</label>
                      <div className="flex rounded-xl bg-slate-100 p-1 border border-slate-200">
                        <button
                          onClick={() => { setVideoMode('shorts'); setCaptionStyle('tiktok'); }}
                          className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                            videoMode === 'shorts' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500'
                          }`}
                        >
                          ⚡ Viral Shorts (9:16)
                        </button>
                        <button
                          onClick={() => { setVideoMode('tutorial'); setCaptionStyle('elegant'); }}
                          className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                            videoMode === 'tutorial' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500'
                          }`}
                        >
                          📚 Slide Deck
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Art Styles */}
                  <div className="space-y-2 pt-2">
                    <label className="text-xs font-bold text-slate-700">Visual Art Style</label>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                      {ART_STYLES.map((st) => (
                        <button
                          key={st.id}
                          type="button"
                          onClick={() => setArtStyle(st.id)}
                          className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                            artStyle === st.id
                              ? 'border-slate-900 bg-slate-900 text-white shadow-xs'
                              : 'border-slate-200 bg-white hover:border-slate-300 text-slate-900'
                          }`}
                        >
                          <span className="text-lg block mb-1">{st.icon}</span>
                          <span className="text-xs font-bold block">{st.name}</span>
                          <span className={`text-[10px] block line-clamp-1 ${artStyle === st.id ? 'text-slate-300' : 'text-slate-500'}`}>
                            {st.desc}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Advanced Settings Drawer */}
                  <div className="pt-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                      className="text-xs font-bold text-slate-500 hover:text-slate-900 flex items-center gap-1.5 cursor-pointer py-1"
                    >
                      <Sliders className="w-3.5 h-3.5" />
                      <span>{showAdvancedSettings ? 'Hide Studio Settings' : 'Advanced Studio Settings (4K/8K, Subtitles, BGM, Transitions)'}</span>
                      {showAdvancedSettings ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {showAdvancedSettings && (
                      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-3">
                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-slate-600">Resolution</label>
                          <select
                            value={videoResolution}
                            onChange={(e) => setVideoResolution(e.target.value)}
                            className="w-full lemon-input"
                          >
                            <option value="1080p">1080p Full HD</option>
                            <option value="4k">4K Ultra HD (Recommended)</option>
                            <option value="8k">8K Master</option>
                          </select>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-slate-600">Scene Transition</label>
                          <select
                            value={transitionStyle}
                            onChange={(e) => setTransitionStyle(e.target.value)}
                            className="w-full lemon-input"
                          >
                            <option value="dynamic">Dynamic Mix</option>
                            <option value="dissolve">Cinematic Dissolve</option>
                            <option value="whip_pan">Whip Pan</option>
                            <option value="flash">Flash to Black</option>
                            <option value="none">Hard Cut</option>
                          </select>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-slate-600">Subtitle Style</label>
                          <select
                            value={captionStyle}
                            onChange={(e) => setCaptionStyle(e.target.value)}
                            className="w-full lemon-input"
                          >
                            <option value="tiktok">TikTok Kinetic Pop</option>
                            <option value="karaoke">Karaoke Yellow Glow</option>
                            <option value="elegant">Cinematic Clean Bottom</option>
                          </select>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-slate-600">Background Music</label>
                          <select
                            value={musicTrack}
                            onChange={(e) => setMusicTrack(e.target.value)}
                            className="w-full lemon-input"
                          >
                            <option value="lofi">Lo-Fi Ambient (Ducked)</option>
                            <option value="upbeat">Upbeat Energy</option>
                            <option value="none">Zero BGM (Clean Voice)</option>
                          </select>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Submit Button */}
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={handleGenerateStoryboard}
                      disabled={!script.trim()}
                      className="w-full lemon-btn-primary py-3.5 text-sm"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>Generate Storyboard Draft</span>
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Generating Storyboard State */}
            {status === 'generating_storyboard' && (
              <div className="lemon-card p-8 text-center space-y-4">
                <Loader2 className="w-8 h-8 animate-spin text-slate-900 mx-auto" />
                <h3 className="font-bold text-base text-slate-900">{progressText}</h3>
                <div className="max-w-md mx-auto w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-slate-900 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>
            )}

            {/* Phase 02: Interactive Storyboard */}
            {currentPhase === 'storyboard' && storyboardScenes && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">Interactive Storyboard Draft</h2>
                    <p className="text-xs text-slate-500">Edit narration sentences or regenerate scene backgrounds before compiling.</p>
                  </div>
                  <button
                    onClick={handleCompileVideo}
                    disabled={status === 'compiling'}
                    className="lemon-btn-primary px-6 py-2.5 text-xs font-bold"
                  >
                    {status === 'compiling' ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" /> Compiling...
                      </>
                    ) : (
                      <>
                        <Film className="w-4 h-4" /> Compile Final Video
                      </>
                    )}
                  </button>
                </div>

                {status === 'compiling' && (
                  <div className="lemon-card p-4 space-y-2 border-emerald-300 bg-emerald-50/50">
                    <div className="flex justify-between text-xs font-bold text-emerald-900">
                      <span>{progressText}</span>
                      <span>{progressPercent}%</span>
                    </div>
                    <div className="w-full bg-emerald-200/60 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-emerald-600 h-full transition-all duration-300 rounded-full"
                        style={{ width: `${progressPercent}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Scene Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {storyboardScenes.map((scene, idx) => (
                    <div key={idx} className="lemon-card p-4 space-y-3 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-extrabold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                            Scene {idx + 1}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            {scene.narration ? scene.narration.split(' ').length : 0} words
                          </span>
                        </div>

                        {/* Image Preview */}
                        <div className="aspect-[9/16] max-h-48 rounded-xl bg-slate-100 overflow-hidden border border-slate-200 relative">
                          <img
                            src={scene.image_url || `${API_BASE_URL}/output/${jobId}_scene_${String(idx).padStart(2, '0')}.jpg`}
                            alt={`Scene ${idx + 1}`}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        </div>

                        {/* Editable Narration */}
                        <div>
                          <label className="text-[10px] font-bold text-slate-500 block mb-1">Narration:</label>
                          <textarea
                            rows={2}
                            value={scene.narration || ''}
                            onChange={(e) => {
                              const updated = [...storyboardScenes];
                              updated[idx].narration = e.target.value;
                              setStoryboardScenes(updated);
                            }}
                            className="w-full lemon-input text-xs p-2 resize-none"
                          />
                        </div>
                      </div>

                      {/* Regenerate Button */}
                      <button
                        onClick={() => handleRegenerateScene(idx, scene.visual || '')}
                        disabled={regeneratingIndex === idx}
                        className="w-full py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                      >
                        {regeneratingIndex === idx ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <RefreshCw className="w-3.5 h-3.5" />
                        )}
                        <span>Regenerate Background</span>
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Phase 03: Export & Publishing */}
            {currentPhase === 'export' && videoUrl && (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="lemon-card p-6 md:p-8 space-y-6 max-w-2xl mx-auto"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-slate-900 font-extrabold text-lg">
                    <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                    <span>Your Master Short is Ready!</span>
                  </div>
                  <a
                    href={videoUrl}
                    download="master_short.mp4"
                    className="lemon-btn-primary px-5 py-2 text-xs"
                  >
                    <Download className="w-3.5 h-3.5" /> Download MP4
                  </a>
                </div>

                <div className="aspect-[9/16] max-h-[500px] mx-auto rounded-2xl overflow-hidden bg-black shadow-xl border border-slate-200">
                  <video src={videoUrl} controls autoPlay className="w-full h-full object-cover" />
                </div>
              </motion.div>
            )}

            {status === 'error' && (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold">
                {progressText || 'An error occurred during generation.'}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
