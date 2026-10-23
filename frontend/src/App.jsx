import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RefreshCw, Edit3, Check, X, Upload, Download,
  Share2, AlertCircle, CheckCircle2, Loader2,
  ChevronDown, ChevronUp, Copy
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

// ── VoiceSelect ──────────────────────────────────────────────────────────────
function VoiceSelect({ id, value, onChange }) {
  const groups = [...new Set(VOICE_OPTIONS.map(v => v.group))];
  return (
    <select id={id} value={value} onChange={e => onChange(e.target.value)} className="lemon-input">
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

// ── TopNav ───────────────────────────────────────────────────────────────────
function TopNav({ phase, onReset, studioTab, setStudioTab }) {
  const phases = ['01 Concept', '02 Storyboard', '03 Export'];
  const phaseIdx = phase === 'concept' ? 0 : phase === 'storyboard' ? 1 : phase === 'export' ? 2 : 0;

  return (
    <header style={{ background: '#FFFFFF', borderBottom: '1.5px solid #E3EAE0' }}
      className="sticky top-0 z-50 px-4 sm:px-8 py-3 flex items-center justify-between shadow-sm">
      {/* Logo + Mode Switcher */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div style={{ background: '#D4F84A', borderRadius: '10px', padding: '6px 10px', fontSize: '20px', lineHeight: 1 }}>🍋</div>
          <div>
            <span style={{ fontWeight: 800, fontSize: '15px', color: '#0F172A', letterSpacing: '-0.02em' }}>
              Shorts Studio
            </span>
            <span style={{ marginLeft: '6px', background: '#F2F7EE', border: '1px solid #E3EAE0', borderRadius: '99px',
              fontSize: '10px', fontWeight: 700, color: '#526658', padding: '2px 7px' }}>AI v2</span>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="seg-control hidden sm:inline-flex">
          <button
            type="button"
            className={`seg-btn ${studioTab === 'video_to_video' ? 'active' : ''}`}
            onClick={() => setStudioTab('video_to_video')}
          >
            🎬 Video-to-Video (5x AI Clips)
          </button>
          <button
            type="button"
            className={`seg-btn ${studioTab === 'image_to_video' ? 'active' : ''}`}
            onClick={() => setStudioTab('image_to_video')}
          >
            🖼️ Image-to-Video
          </button>
        </div>
      </div>

      {/* Step Indicator (when in image_to_video mode) */}
      {studioTab === 'image_to_video' ? (
        <div className="hidden lg:flex items-center gap-1">
          {phases.map((label, i) => (
            <div key={i} className="flex items-center gap-1">
              <div style={{
                padding: '5px 13px', borderRadius: '99px',
                background: i === phaseIdx ? '#D4F84A' : '#F2F7EE',
                border: '1.5px solid',
                borderColor: i === phaseIdx ? '#C4EE33' : '#E3EAE0',
                color: i === phaseIdx ? '#0F172A' : '#8FAE97',
                fontSize: '11px', fontWeight: i === phaseIdx ? 800 : 600,
                transition: 'all 0.2s ease',
              }}>
                {label}
              </div>
              {i < phases.length - 1 && (
                <div style={{ width: '20px', height: '1px', background: '#E3EAE0' }} />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="hidden lg:flex items-center gap-2">
          <span style={{
            padding: '5px 13px', borderRadius: '99px',
            background: '#D4F84A', border: '1.5px solid #C4EE33',
            color: '#0F172A', fontSize: '11px', fontWeight: 800
          }}>
            ⚡ 5-Scene Veo / Kling / VideoFX Pipeline
          </span>
        </div>
      )}

      {/* Right side: Mobile switcher + Reset */}
      <div className="flex items-center gap-2">
        <div className="seg-control sm:hidden">
          <button
            type="button"
            className={`seg-btn ${studioTab === 'video_to_video' ? 'active' : ''}`}
            onClick={() => setStudioTab('video_to_video')}
            style={{ padding: '4px 8px', fontSize: '11px' }}
          >
            🎬 5x Clips
          </button>
          <button
            type="button"
            className={`seg-btn ${studioTab === 'image_to_video' ? 'active' : ''}`}
            onClick={() => setStudioTab('image_to_video')}
            style={{ padding: '4px 8px', fontSize: '11px' }}
          >
            🖼️ Image
          </button>
        </div>

        <button className="btn-ghost" style={{ fontSize: '12px', padding: '7px 14px' }} onClick={onReset}>
          <RefreshCw size={13} /> New Project
        </button>
      </div>
    </header>
  );
}

// ── Shared sub-components (declared at module scope to avoid react-hooks/static-components errors) ──
function SettingsLabel({ children }) {
  return (
    <div style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase',
      letterSpacing: '0.07em', marginBottom: '5px' }}>
      {children}
    </div>
  );
}

function AccordionCard({ title, icon, isOpen, onToggle, children }) {
  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <button onClick={onToggle}
        style={{ width: '100%', padding: '14px 18px', display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', background: 'none', border: 'none', cursor: 'pointer' }}>
        <span style={{ fontWeight: 700, fontSize: '13px', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>{icon}</span> {title}
        </span>
        {isOpen ? <ChevronUp size={15} color="#8FAE97" /> : <ChevronDown size={15} color="#8FAE97" />}
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.22 }}
            style={{ overflow: 'hidden' }}>
            <div style={{ padding: '0 18px 18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── SettingsDrawer ───────────────────────────────────────────────────────────
function SettingsDrawer({
  voiceAccent, setVoiceAccent, captionStyle, setCaptionStyle,
  captionLang, setCaptionLang, videoResolution, setVideoResolution,
  isDialogueMode, setIsDialogueMode, voiceA, setVoiceA, voiceB, setVoiceB,
  transitionStyle, setTransitionStyle,
}) {
  const [voiceOpen, setVoiceOpen] = useState(true);
  const [formatOpen, setFormatOpen] = useState(true);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Voice & Narration */}
      <AccordionCard title="Voice & Narration" icon="🎙️" isOpen={voiceOpen} onToggle={() => setVoiceOpen(v => !v)}>
        <div>
          <SettingsLabel>Narration Mode</SettingsLabel>
          <div className="seg-control" style={{ width: '100%' }}>
            <button className={`seg-btn${!isDialogueMode ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setIsDialogueMode(false)}>🎙️ Solo</button>
            <button className={`seg-btn${isDialogueMode ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setIsDialogueMode(true)}>👥 Dialogue</button>
          </div>
        </div>

        {!isDialogueMode ? (
          <div>
            <SettingsLabel>Character Voice</SettingsLabel>
            <VoiceSelect id="voice-accent" value={voiceAccent} onChange={setVoiceAccent} />
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <SettingsLabel>👧 Character A</SettingsLabel>
              <VoiceSelect id="voice-a" value={voiceA} onChange={setVoiceA} />
            </div>
            <div>
              <SettingsLabel>👦 Character B</SettingsLabel>
              <VoiceSelect id="voice-b" value={voiceB} onChange={setVoiceB} />
            </div>
          </div>
        )}

        <div>
          <SettingsLabel>Scene Transitions</SettingsLabel>
          <select id="transition-style" className="lemon-input" value={transitionStyle}
            onChange={e => setTransitionStyle(e.target.value)}>
            <option value="dynamic">✨ Dynamic Auto-Mix</option>
            <option value="whip_pan">🚀 Whip Pan Sweep</option>
            <option value="dissolve">🌫️ Blur Crossfade</option>
            <option value="flash">⚡ Lens Impact Flash</option>
            <option value="slide">📲 Directional Slide</option>
            <option value="none">✂️ Hard Cut</option>
          </select>
        </div>
      </AccordionCard>

      {/* Captions & Format */}
      <AccordionCard title="Captions & Format" icon="💬" isOpen={formatOpen} onToggle={() => setFormatOpen(v => !v)}>

        <div>
          <SettingsLabel>Caption Style</SettingsLabel>
          <select id="caption-style" className="lemon-input" value={captionStyle}
            onChange={e => setCaptionStyle(e.target.value)}>
            <option value="tiktok">💥 TikTok Highlight</option>
            <option value="viral">🔥 Viral Hype (Emojis)</option>
            <option value="elegant">📖 Elegant Block</option>
          </select>
        </div>

        <div>
          <SettingsLabel>Caption Language</SettingsLabel>
          <div className="seg-control" style={{ width: '100%' }}>
            <button className={`seg-btn${captionLang === 'English' ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setCaptionLang('English')}>🇬🇧 English</button>
            <button className={`seg-btn${captionLang === 'Hindi' ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setCaptionLang('Hindi')}>🇮🇳 Hindi</button>
          </div>
        </div>

        <div>
          <SettingsLabel>Resolution</SettingsLabel>
          <div className="seg-control" style={{ width: '100%' }}>
            <button className={`seg-btn${videoResolution === '1080p' ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setVideoResolution('1080p')}>📱 1080p</button>
            <button className={`seg-btn${videoResolution === '4k' ? ' active' : ''}`} style={{ flex: 1 }}
              onClick={() => setVideoResolution('4k')}>💎 4K</button>
          </div>
        </div>
      </AccordionCard>
    </div>
  );
}

// ── Phase1: ConceptPanel ─────────────────────────────────────────────────────
function ConceptPanel({ script, setScript, artStyle, setArtStyle, onGenerate, status, error, isDialogueMode, setIsDialogueMode, ...settingsProps }) {
  const wordCount = script.trim().split(/\s+/).filter(Boolean).length;
  const isReady = wordCount >= 10;

  return (
    <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', flexWrap: 'wrap' }}>

      {/* Left: Creator Canvas */}
      <div style={{ flex: '1 1 360px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* Story Starters */}
        <div className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A', marginBottom: '4px', letterSpacing: '-0.02em' }}>
            What is your Short about?
          </h2>
          <p style={{ fontSize: '13px', color: '#526658', marginBottom: '14px' }}>
            Paste your script, or pick a starter below ↓
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
            {STORY_STARTERS.map(s => (
              <button key={s.label} onClick={() => setScript(s.text)}
                style={{ padding: '7px 13px', borderRadius: '99px', fontSize: '12px', fontWeight: 600,
                  background: '#F2F7EE', border: '1.5px solid #E3EAE0', color: '#526658',
                  cursor: 'pointer', transition: 'all 0.15s ease', whiteSpace: 'nowrap' }}
                onMouseEnter={e => { e.target.style.background = '#D4F84A'; e.target.style.borderColor = '#C4EE33'; e.target.style.color = '#0F172A'; }}
                onMouseLeave={e => { e.target.style.background = '#F2F7EE'; e.target.style.borderColor = '#E3EAE0'; e.target.style.color = '#526658'; }}>
                {s.label}
              </button>
            ))}
          </div>

          {/* Textarea */}
          <div style={{ position: 'relative' }}>
            <textarea
              id="script"
              rows={6}
              value={script}
              onChange={e => setScript(e.target.value)}
              placeholder="E.g., Did you know honey never expires? Ancient Egyptians stored it in tombs for thousands of years..."
              style={{ width: '100%', resize: 'none', border: '1.5px solid',
                borderColor: isReady ? '#84CC16' : '#E3EAE0', borderRadius: '14px',
                padding: '14px', fontSize: '14px', color: '#0F172A', lineHeight: '1.6',
                outline: 'none', fontFamily: 'inherit', transition: 'border-color 0.2s ease',
                background: '#FAFCF9' }}
              onFocus={e => e.target.style.borderColor = '#84CC16'}
              onBlur={e => e.target.style.borderColor = isReady ? '#84CC16' : '#E3EAE0'}
            />
            <div style={{ position: 'absolute', bottom: '12px', right: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '11px', fontWeight: 700,
                color: isReady ? '#84CC16' : '#8FAE97' }}>
                {wordCount} words
              </span>
              {isReady && <CheckCircle2 size={13} color="#84CC16" />}
            </div>
          </div>
        </div>

        {/* Art Style */}
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase',
            letterSpacing: '0.07em', marginBottom: '12px' }}>🎬 Background Art Style</div>
          <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
            {ART_STYLES.map(s => (
              <button key={s.id} onClick={() => setArtStyle(s.id)}
                style={{ flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center',
                  gap: '6px', padding: '12px 16px', borderRadius: '14px', cursor: 'pointer',
                  border: '2px solid', transition: 'all 0.18s ease',
                  borderColor: artStyle === s.id ? '#2D3B31' : '#E3EAE0',
                  background: artStyle === s.id ? '#F2F7EE' : '#FFFFFF',
                  boxShadow: artStyle === s.id ? '0 0 0 4px rgba(212,248,74,0.25)' : 'none' }}>
                <span style={{ fontSize: '22px' }}>{s.icon}</span>
                <span style={{ fontSize: '11px', fontWeight: 700, color: artStyle === s.id ? '#0F172A' : '#526658',
                  whiteSpace: 'nowrap' }}>{s.name}</span>
                <span style={{ fontSize: '10px', color: '#8FAE97', textAlign: 'center', maxWidth: '72px',
                  lineHeight: '1.3' }}>{s.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {status === 'error' && error && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            style={{ padding: '14px 16px', borderRadius: '14px', background: '#FEF2F2',
              border: '1.5px solid #FCA5A5', display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
            <AlertCircle size={16} color="#EF4444" style={{ flexShrink: 0, marginTop: '1px' }} />
            <p style={{ fontSize: '13px', color: '#DC2626', fontWeight: 500, lineHeight: '1.5' }}>{error}</p>
          </motion.div>
        )}

        {/* CTA */}
        <motion.button className="btn-lemon" style={{ width: '100%', fontSize: '15px', padding: '16px' }}
          onClick={onGenerate}
          disabled={!isReady && status !== 'completed' && status !== 'error'}
          whileHover={isReady ? { y: -2 } : {}}
          whileTap={isReady ? { scale: 0.98 } : {}}>
          <span style={{ fontSize: '18px' }}>✨</span>
          Generate Storyboard Drafts
        </motion.button>
      </div>

      {/* Right: Settings Drawer */}
      <div style={{ flex: '0 1 280px', minWidth: '240px' }}>
        <SettingsDrawer isDialogueMode={isDialogueMode} setIsDialogueMode={setIsDialogueMode} {...settingsProps} />
      </div>
    </div>
  );
}

// ── RenderProgress ───────────────────────────────────────────────────────────
function RenderProgress({ progressText, progressPercent, status }) {
  const activeIdx = getActiveStep(status, progressPercent);
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      className="card" style={{ padding: '32px', textAlign: 'center' }}>
      {/* Spinner */}
      <div style={{ position: 'relative', display: 'inline-flex', marginBottom: '20px' }}>
        <div style={{ width: '64px', height: '64px', borderRadius: '50%',
          border: '3px solid #E3EAE0', borderTopColor: '#D4F84A',
          animation: 'spin 1s linear infinite' }} />
        <div style={{ position: 'absolute', inset: '12px', borderRadius: '50%', background: '#FAFCF9',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>
          {PIPELINE_STEPS[activeIdx]?.icon}
        </div>
      </div>

      <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0F172A', marginBottom: '8px' }}>
        {status === 'generating_storyboard' ? 'Building Storyboard...' : 'Rendering Your Video...'}
      </h3>
      <p style={{ fontSize: '13px', color: '#526658', background: '#F2F7EE', display: 'inline-block',
        padding: '6px 14px', borderRadius: '99px', marginBottom: '28px', fontWeight: 500 }}>
        {progressText}
      </p>

      {/* Progress Bar */}
      <div style={{ maxWidth: '380px', margin: '0 auto 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Progress</span>
          <span style={{ fontSize: '12px', fontWeight: 800, color: '#2D3B31', background: '#D4F84A',
            borderRadius: '99px', padding: '1px 9px' }}>{progressPercent}%</span>
        </div>
        <div style={{ height: '8px', background: '#E3EAE0', borderRadius: '99px', overflow: 'hidden' }}>
          <motion.div initial={{ width: '0%' }} animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            style={{ height: '100%', background: 'linear-gradient(90deg, #84CC16, #D4F84A)', borderRadius: '99px' }} />
        </div>
      </div>

      {/* Steps */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
        {PIPELINE_STEPS.map((step, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px',
            padding: '6px 12px', borderRadius: '99px', fontSize: '11px', fontWeight: 700,
            background: i < activeIdx ? '#F2F7EE' : i === activeIdx ? '#D4F84A' : '#FAFCF9',
            color: i < activeIdx ? '#84CC16' : i === activeIdx ? '#0F172A' : '#8FAE97',
            border: '1.5px solid', transition: 'all 0.2s ease',
            borderColor: i < activeIdx ? '#C8DABB' : i === activeIdx ? '#C4EE33' : '#E3EAE0' }}>
            {i < activeIdx ? '✓' : step.icon} {step.name}
          </div>
        ))}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </motion.div>
  );
}

// ── SceneCard ────────────────────────────────────────────────────────────────
function SceneCard({ idx, scene, imgUrl, onRegenerate, isRegenerating, onUploadImage, isUploading }) {
  const [editedPrompt, setEditedPrompt] = useState(scene?.visual || '');
  const [editedNarration, setEditedNarration] = useState(scene?.narration || '');
  const [isEditing, setIsEditing] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  const [prevScene, setPrevScene] = useState(scene);
  if (scene !== prevScene) {
    setPrevScene(scene);
    setEditedPrompt(scene?.visual || '');
    setEditedNarration(scene?.narration || '');
  }
  if (!scene) return null;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.06 }} className="card animate-fadeUp"
      style={{ overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>

      {/* Thumbnail */}
      <div style={{ position: 'relative', aspectRatio: '9/16', maxHeight: '300px', overflow: 'hidden',
        background: '#F2F7EE', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        className="group">
        {!imgLoaded && !isRegenerating && !isUploading && (
          <div className="animate-shimmer" style={{ position: 'absolute', inset: 0 }} />
        )}
        <img src={imgUrl} alt={`Scene ${idx + 1}`}
          style={{ width: '100%', height: '100%', objectFit: 'cover',
            opacity: imgLoaded ? 1 : 0, transition: 'opacity 0.4s ease' }}
          onLoad={() => setImgLoaded(true)}
          onError={e => { setImgLoaded(true); e.target.src = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80'; }}
        />

        {/* Scene badge */}
        <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 10,
          background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)',
          borderRadius: '99px', padding: '4px 10px', fontSize: '11px', fontWeight: 800,
          color: '#0F172A', border: '1px solid rgba(0,0,0,0.07)' }}>
          Scene {idx + 1}
          {scene.speaker && <span style={{ marginLeft: '6px', color: '#526658' }}>· {scene.speaker}</span>}
        </div>

        {/* Hover overlay */}
        {!isRegenerating && !isUploading && (
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(15,23,42,0.45)',
            opacity: 0, transition: 'opacity 0.2s ease', display: 'flex', alignItems: 'center',
            justifyContent: 'center', zIndex: 10, backdropFilter: 'blur(2px)' }}
            className="group-hover:opacity-100">
            <label style={{ background: '#D4F84A', color: '#0F172A', borderRadius: '99px',
              padding: '10px 18px', fontSize: '12px', fontWeight: 800, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '6px', transition: 'transform 0.15s' }}
              title="Upload custom 9:16 image">
              <Upload size={14} /> Upload Image
              <input type="file" accept="image/*" className="hidden"
                onChange={e => { if (e.target.files[0]) onUploadImage(idx, e.target.files[0]); }} />
            </label>
          </div>
        )}

        {(isRegenerating || isUploading) && (
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.85)',
            backdropFilter: 'blur(4px)', display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', gap: '10px', zIndex: 10 }}>
            <Loader2 size={28} color="#84CC16" style={{ animation: 'spin 1s linear infinite' }} />
            <p style={{ fontSize: '12px', fontWeight: 700, color: '#2D3B31' }}>
              {isRegenerating ? 'Regenerating Art...' : 'Uploading...'}
            </p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}
      </div>

      {/* Body */}
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
        <div>
          <div style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase',
            letterSpacing: '0.07em', marginBottom: '6px' }}>🎙️ Narration</div>
          {isEditing ? (
            <textarea value={editedNarration} onChange={e => setEditedNarration(e.target.value)}
              className="lemon-input" style={{ minHeight: '70px', resize: 'none', lineHeight: '1.5', padding: '10px' }}
              placeholder="Spoken voiceover script..." />
          ) : (
            <p style={{ fontSize: '13px', color: '#0F172A', lineHeight: '1.55', fontWeight: 500,
              background: '#F8FAF6', borderRadius: '10px', padding: '10px',
              border: '1px solid #E3EAE0' }}>{scene.narration}</p>
          )}
        </div>

        <div>
          <div style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase',
            letterSpacing: '0.07em', marginBottom: '6px' }}>🖼️ Visual Prompt</div>
          {isEditing ? (
            <textarea value={editedPrompt} onChange={e => setEditedPrompt(e.target.value)}
              className="lemon-input" style={{ minHeight: '55px', resize: 'none', lineHeight: '1.5', padding: '10px' }} />
          ) : (
            <p style={{ fontSize: '12px', color: '#526658', lineHeight: '1.5', fontStyle: 'italic',
              background: '#FAFCF9', borderRadius: '10px', padding: '10px',
              border: '1px solid #E3EAE0' }}>{scene.visual}</p>
          )}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '8px', paddingTop: '4px' }}>
          {isEditing ? (
            <>
              <button onClick={() => { setIsEditing(false); onRegenerate(editedPrompt, editedNarration); }}
                className="btn-lemon" style={{ flex: 1, fontSize: '12px', padding: '9px 12px', borderRadius: '10px' }}>
                <Check size={13} /> Save & Redraw
              </button>
              <button onClick={() => { setEditedPrompt(scene.visual || ''); setEditedNarration(scene.narration || ''); setIsEditing(false); }}
                className="btn-ghost" style={{ padding: '9px 12px', borderRadius: '10px' }}>
                <X size={13} />
              </button>
            </>
          ) : (
            <button onClick={() => setIsEditing(true)}
              className="btn-ghost" style={{ flex: 1, fontSize: '12px', padding: '9px 12px',
                borderRadius: '10px', justifyContent: 'center' }}>
              <Edit3 size={13} /> Edit Scene
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ── Phase2: StoryboardPanel ──────────────────────────────────────────────────
function StoryboardPanel({ storyboardScenes, onCompile, onReset,
  regeneratingIndex, uploadingIndex, onRegenerate, onUpload, getImgUrl }) {
  const estimatedDuration = storyboardScenes ? Math.round(storyboardScenes.length * 8) : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div className="card" style={{ padding: '20px 24px', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em' }}>
            🎨 Storyboard Review
          </h2>
          <p style={{ fontSize: '13px', color: '#526658', marginTop: '2px' }}>
            {storyboardScenes?.length} Scenes · ~{estimatedDuration}s — Review & refine before rendering
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-ghost" style={{ fontSize: '13px' }} onClick={onReset}>
            <X size={14} /> Reset
          </button>
          <motion.button className="btn-lemon" style={{ fontSize: '13px', padding: '11px 22px' }}
            onClick={onCompile} whileHover={{ y: -1 }} whileTap={{ scale: 0.97 }}>
            🚀 Render Final Video
          </motion.button>
        </div>
      </div>

      {/* Scene Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
        {storyboardScenes?.map((scene, idx) => (
          <SceneCard key={idx} idx={idx} scene={scene} imgUrl={getImgUrl(idx)}
            onRegenerate={(p, n) => onRegenerate(idx, p, n)}
            isRegenerating={regeneratingIndex === idx}
            onUploadImage={onUpload} isUploading={uploadingIndex === idx} />
        ))}
      </div>

      {/* Sticky render CTA (mobile-friendly) */}
      <div style={{ position: 'sticky', bottom: '16px', zIndex: 20, display: 'flex', justifyContent: 'center' }}>
        <motion.button className="btn-lemon animate-lemon-pulse"
          style={{ fontSize: '15px', padding: '16px 40px', borderRadius: '99px' }}
          onClick={onCompile} whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}>
          🚀 Render Final Video ({storyboardScenes?.length} Scenes)
        </motion.button>
      </div>
    </div>
  );
}

// ── CopyButton ───────────────────────────────────────────────────────────────
function CopyButton({ text, label = 'Copy' }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={handleCopy} className="btn-ghost"
      style={{ fontSize: '11px', padding: '5px 11px', borderRadius: '8px', gap: '4px' }}>
      {copied ? <><CheckCircle2 size={11} color="#84CC16" /> Copied!</> : <><Copy size={11} /> {label}</>}
    </button>
  );
}

// ── Phase3: ExportPanel ──────────────────────────────────────────────────────
function ExportPanel({ videoUrl, polishedScript, jobId, apiBaseUrl, onReset }) {
  const [seoOpen, setSeoOpen] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('My AI Short');
  const [uploadDesc, setUploadDesc] = useState('Auto-generated using Shorts Studio AI');
  const [uploadTags, setUploadTags] = useState('shorts, ai, generated');
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [uploadError, setUploadError] = useState('');
  const [youtubeVideoId, setYoutubeVideoId] = useState('');
  const [manualPack, setManualPack] = useState(null);

  const handleDownload = async e => {
    if (e?.preventDefault) e.preventDefault();
    try {
      const resp = await fetch(videoUrl);
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `shorts_${jobId}.mp4`;
      document.body.appendChild(a); a.click(); a.remove();
      window.URL.revokeObjectURL(url);
    } catch { window.open(videoUrl, '_blank'); }
  };

  const handleYoutubeUpload = async () => {
    setUploadStatus('uploading'); setUploadError(''); setManualPack(null);
    try {
      const resp = await axios.post(`${apiBaseUrl}/upload/${jobId}`, {
        title: uploadTitle, description: uploadDesc, tags: uploadTags
      });
      if (resp.data.requires_manual) { setUploadStatus('success'); setManualPack(resp.data); }
      else if (resp.data.success) { setUploadStatus('success'); setYoutubeVideoId(resp.data.video_id); }
      else { setUploadStatus('error'); setUploadError(resp.data.error || 'Upload failed.'); }
    } catch (err) { setUploadStatus('error'); setUploadError(err.response?.data?.error || 'Network error.'); }
  };

  const getParsedScenes = () => {
    if (!polishedScript) return [];
    try { const p = JSON.parse(polishedScript); if (Array.isArray(p)) return p; } catch(_) { /* ignore */ }
    return [];
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

      {/* Success header */}
      <div className="card" style={{ padding: '20px 24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: '#D4F84A',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px', flexShrink: 0 }}>
          🎉
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0F172A' }}>Your Short is Ready!</h2>
          <p style={{ fontSize: '13px', color: '#526658', marginTop: '2px' }}>
            Download your video or publish it directly to YouTube.
          </p>
        </div>
        <button className="btn-ghost" style={{ fontSize: '12px' }} onClick={onReset}>
          <RefreshCw size={13} /> New Project
        </button>
      </div>

      {/* Main content */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', alignItems: 'flex-start' }}>

        {/* Video Player */}
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column',
          alignItems: 'center', gap: '16px', flex: '0 0 auto' }}>
          <div style={{ borderRadius: '16px', overflow: 'hidden', border: '2px solid #E3EAE0',
            aspectRatio: '9/16', width: '220px', background: '#000', flexShrink: 0 }}>
            <video controls autoPlay muted loop playsInline
              style={{ width: '100%', height: '100%', objectFit: 'cover' }} src={videoUrl} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
            <motion.button className="btn-lemon" style={{ width: '100%', fontSize: '13px', padding: '12px' }}
              onClick={handleDownload} whileHover={{ y: -1 }} whileTap={{ scale: 0.97 }}>
              <Download size={15} /> Download .MP4
            </motion.button>
            <button className="btn-ghost" style={{ width: '100%', fontSize: '13px', padding: '11px', justifyContent: 'center' }}
              onClick={() => { navigator.clipboard.writeText(videoUrl); }}>
              <Share2 size={13} /> Copy Video Link
            </button>
          </div>
        </div>

        {/* Scene breakdown + YouTube SEO */}
        <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Scene Breakdown */}
          {getParsedScenes().length > 0 && (
            <div className="card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#8FAE97', textTransform: 'uppercase',
                letterSpacing: '0.07em', marginBottom: '12px' }}>📋 Scene Breakdown</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '240px', overflowY: 'auto' }}>
                {getParsedScenes().map((scene, i) => (
                  <div key={i} style={{ padding: '10px 14px', borderRadius: '12px',
                    background: '#F8FAF6', border: '1px solid #E3EAE0' }}>
                    <div style={{ fontSize: '10px', fontWeight: 800, color: '#84CC16',
                      textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '4px' }}>
                      Scene {i + 1}
                    </div>
                    <p style={{ fontSize: '13px', color: '#0F172A', fontWeight: 500, lineHeight: '1.5' }}>
                      "{scene.narration}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* YouTube SEO Assistant */}
          <div className="card" style={{ overflow: 'hidden' }}>
            <button onClick={() => setSeoOpen(o => !o)}
              style={{ width: '100%', padding: '16px 20px', display: 'flex', alignItems: 'center',
                justifyContent: 'space-between', background: 'none', border: 'none', cursor: 'pointer' }}>
              <span style={{ fontWeight: 700, fontSize: '13px', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ background: '#FF0000', borderRadius: '6px', padding: '2px 5px',
                  color: 'white', fontWeight: 900, letterSpacing: '-0.03em', fontSize: '11px' }}>YT</span>
                YouTube SEO Assistant
              </span>
              {seoOpen ? <ChevronUp size={15} color="#8FAE97" /> : <ChevronDown size={15} color="#8FAE97" />}
            </button>

            <AnimatePresence initial={false}>
              {seoOpen && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.22 }}
                  style={{ overflow: 'hidden' }}>
                  <div style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {manualPack ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ padding: '12px', borderRadius: '12px', background: '#F2F7EE',
                          border: '1px solid #C8DABB', display: 'flex', gap: '8px' }}>
                          <CheckCircle2 size={16} color="#84CC16" style={{ flexShrink: 0, marginTop: '1px' }} />
                          <p style={{ fontSize: '12px', color: '#2D3B31', fontWeight: 500 }}>{manualPack.message}</p>
                        </div>
                        {[['Title', manualPack.title], ['Description', manualPack.description], ['Tags', manualPack.tags]].map(([label, val]) => (
                          <div key={label}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <span style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97',
                                textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</span>
                              <CopyButton text={val} label={`Copy ${label}`} />
                            </div>
                            <div style={{ background: '#F8FAF6', borderRadius: '10px', padding: '10px 12px',
                              border: '1px solid #E3EAE0', fontSize: '12px', color: '#0F172A',
                              fontFamily: 'monospace', whiteSpace: 'pre-wrap', maxHeight: '100px', overflowY: 'auto' }}>
                              {val}
                            </div>
                          </div>
                        ))}
                        <button className="btn-ghost" style={{ alignSelf: 'center', fontSize: '12px' }}
                          onClick={() => setManualPack(null)}>Back to Upload Form</button>
                      </div>
                    ) : uploadStatus === 'success' && youtubeVideoId ? (
                      <div style={{ padding: '14px', borderRadius: '12px', background: '#F0FDF4',
                        border: '1px solid #86EFAC', display: 'flex', gap: '10px' }}>
                        <CheckCircle2 size={16} color="#22C55E" style={{ flexShrink: 0 }} />
                        <div>
                          <p style={{ fontSize: '13px', fontWeight: 700, color: '#16A34A' }}>Uploaded Successfully!</p>
                          <a href={`https://youtu.be/${youtubeVideoId}`} target="_blank" rel="noreferrer"
                            style={{ fontSize: '12px', color: '#2563EB', fontWeight: 600, display: 'inline-flex',
                              alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                            View on YouTube ↗
                          </a>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                          <div>
                            <label style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97',
                              textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>
                              Title
                            </label>
                            <input type="text" value={uploadTitle} onChange={e => setUploadTitle(e.target.value)}
                              className="lemon-input" style={{ fontSize: '12px' }} placeholder="Short Title"
                              disabled={uploadStatus === 'uploading'} />
                          </div>
                          <div>
                            <label style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97',
                              textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>
                              Tags
                            </label>
                            <input type="text" value={uploadTags} onChange={e => setUploadTags(e.target.value)}
                              className="lemon-input" style={{ fontSize: '12px' }} placeholder="shorts, ai"
                              disabled={uploadStatus === 'uploading'} />
                          </div>
                        </div>
                        <div>
                          <label style={{ fontSize: '10px', fontWeight: 700, color: '#8FAE97',
                            textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>
                            Description
                          </label>
                          <textarea rows={2} value={uploadDesc} onChange={e => setUploadDesc(e.target.value)}
                            className="lemon-input" style={{ fontSize: '12px', resize: 'none' }}
                            disabled={uploadStatus === 'uploading'} />
                        </div>
                        {uploadStatus === 'error' && (
                          <div style={{ padding: '10px 14px', borderRadius: '10px', background: '#FEF2F2',
                            border: '1px solid #FCA5A5', display: 'flex', gap: '8px' }}>
                            <AlertCircle size={14} color="#EF4444" style={{ flexShrink: 0 }} />
                            <p style={{ fontSize: '12px', color: '#DC2626' }}>{uploadError}</p>
                          </div>
                        )}
                        <button onClick={handleYoutubeUpload}
                          disabled={uploadStatus === 'uploading' || !uploadTitle.trim()}
                          style={{ width: '100%', padding: '11px', borderRadius: '10px',
                            background: '#EF4444', color: '#FFF', fontWeight: 700, fontSize: '13px',
                            border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center',
                            justifyContent: 'center', gap: '8px', opacity: uploadStatus === 'uploading' ? 0.7 : 1,
                            transition: 'opacity 0.15s' }}>
                          {uploadStatus === 'uploading'
                            ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Uploading...</>
                            : <><Share2 size={14} /> Authorize & Upload to YouTube</>}
                        </button>
                        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                      </>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ── App (Root) ───────────────────────────────────────────────────────────────
function App() {
  const VALID_VOICES = new Set(['in_female', 'in_male', 'hi_female', 'hi_male']);

  const [script, setScript]           = useState(() => localStorage.getItem('active_script') || '');
  const [jobId, setJobId]             = useState(() => {
    const id = localStorage.getItem('active_job_id');
    const st = localStorage.getItem('active_job_status');
    return (id && st && st !== 'completed' && st !== 'idle') ? id : null;
  });
  const [status, setStatus]           = useState(() => {
    const id = localStorage.getItem('active_job_id');
    const st = localStorage.getItem('active_job_status');
    return (id && st && st !== 'completed' && st !== 'idle') ? st : 'idle';
  });
  const [progressText, setProgressText]     = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [videoUrl, setVideoUrl]         = useState(null);
  const [polishedScript, setPolishedScript] = useState(null);
  const [storyboardScenes, setStoryboardScenes] = useState(null);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);
  const [uploadingIndex, setUploadingIndex]       = useState(null);
  const [error, setError]               = useState('');

  // Settings
  const [voiceAccent, setVoiceAccent] = useState(() => {
    const v = localStorage.getItem('active_voice_accent');
    return (v && VALID_VOICES.has(v)) ? v : 'in_female';
  });
  const [captionStyle, setCaptionStyle] = useState(() => localStorage.getItem('active_caption_style') || 'tiktok');
  const [artStyle, setArtStyle]         = useState(() => localStorage.getItem('active_art_style') || 'cinematic');
  const [captionLang, setCaptionLang]   = useState('English');
  const [videoResolution, setVideoResolution] = useState(() => localStorage.getItem('active_video_resolution') || '1080p');
  const [isDialogueMode, setIsDialogueMode]   = useState(false);
  const [voiceA, setVoiceA] = useState('in_female');
  const [voiceB, setVoiceB] = useState('in_male');
  const [transitionStyle, setTransitionStyle] = useState('dynamic');
  const [studioTab, setStudioTab]             = useState(() => localStorage.getItem('active_studio_tab') || 'video_to_video');

  const pollingRef = useRef(null);

  // Persist settings
  useEffect(() => { localStorage.setItem('active_studio_tab', studioTab); }, [studioTab]);
  useEffect(() => { if (jobId) { localStorage.setItem('active_job_id', jobId); localStorage.setItem('active_job_status', status); } else { localStorage.removeItem('active_job_id'); localStorage.removeItem('active_job_status'); } }, [jobId, status]);
  useEffect(() => { if (script) localStorage.setItem('active_script', script); else localStorage.removeItem('active_script'); }, [script]);
  useEffect(() => { localStorage.setItem('active_voice_accent', voiceAccent); }, [voiceAccent]);
  useEffect(() => { localStorage.setItem('active_caption_style', captionStyle); }, [captionStyle]);
  useEffect(() => { localStorage.setItem('active_art_style', artStyle); }, [artStyle]);
  useEffect(() => { localStorage.setItem('active_video_resolution', videoResolution); }, [videoResolution]);

  // Resume session
  useEffect(() => {
    const id = localStorage.getItem('active_job_id');
    const st = localStorage.getItem('active_job_status');
    if (id && st && st !== 'completed' && st !== 'idle') pollStatus(id);
  }, []);

  const getSceneImageUrl = idx => {
    if (storyboardScenes?.[idx]?.image_url) return storyboardScenes[idx].image_url;
    return `${API_BASE_URL}/output/${jobId}_scene_${String(idx).padStart(2, '0')}.jpg`;
  };

  function pollStatus(jid, mode = 'fast') {
    if (pollingRef.current) { clearTimeout(pollingRef.current); pollingRef.current = null; }
    let delay = mode === 'fast' ? 2000 : 5000;
    let errors = 0;

    const tick = async () => {
      try {
        const { data } = await axios.get(`${API_BASE_URL}/status/${jid}`);
        errors = 0;
        const { state, message, polished_script, progress } = data;
        setProgressText(message);
        if (progress !== undefined) setProgressPercent(progress);
        if (polished_script) {
          setPolishedScript(polished_script);
          try { setStoryboardScenes(JSON.parse(polished_script)); } catch(_) { /* ignore */ }
        }
        if (progress > 60 && delay === 2000) delay = 5000;
        if (state === 'storyboard_ready') { setStatus('storyboard_ready'); setProgressPercent(100); return; }
        if (state === 'completed') { setStatus('completed'); setProgressPercent(100); setVideoUrl(`${API_BASE_URL}/download/${jid}.mp4`); return; }
        if (state === 'error') { setStatus('error'); setError(message || 'Pipeline error.'); setProgressPercent(0); return; }
        pollingRef.current = setTimeout(tick, delay);
      } catch (_) {
        if (++errors >= 5) { setStatus('error'); setError('Lost connection to server.'); return; }
        pollingRef.current = setTimeout(tick, 3000);
      }
    };
    pollingRef.current = setTimeout(tick, delay);
  }

  const handleGenerateStoryboard = async () => {
    if (status === 'completed' || status === 'error') { doReset(); return; }
    const wc = script.trim().split(/\s+/).filter(Boolean).length;
    if (wc < 10) { setError(`Script too short (${wc} words). Please enter at least 10 words for a meaningful Short.`); setStatus('error'); return; }
    setError('');
    setStatus('generating_storyboard');
    setProgressText('Polishing script and building storyboard drafts...');
    setProgressPercent(5);
    setVideoUrl(null); setPolishedScript(null); setStoryboardScenes(null);

    try {
      const { data } = await axios.post(`${API_BASE_URL}/storyboard`, {
        script,
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        voice_a: voiceA, voice_b: voiceB,
        transition_style: transitionStyle,
        music_track: 'none', caption_style: captionStyle,
        caption_lang: captionLang, art_style: artStyle,
        music_volume: 0,
        video_mode: isDialogueMode ? 'dialogue' : 'shorts',
        video_resolution: videoResolution,
      });
      setJobId(data.job_id);
      pollStatus(data.job_id);
    } catch {
      setStatus('error');
      setError('Failed to initialize storyboard generation.');
    }
  };

  const handleCompile = async () => {
    setStatus('compiling');
    setProgressText('Voice synthesizers and video compilers standing by...');
    setProgressPercent(5);
    try {
      await axios.post(`${API_BASE_URL}/compile`, {
        job_id: jobId,
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        voice_a: voiceA, voice_b: voiceB, transition_style: transitionStyle,
        caption_style: captionStyle, caption_lang: captionLang,
        music_track: 'none', music_volume: 0,
        art_style: artStyle, video_mode: isDialogueMode ? 'dialogue' : 'shorts',
        video_resolution: videoResolution,
      });
      pollStatus(jobId, 'fast');
    } catch {
      setStatus('error');
      setError('Video compilation failed. Please try again.');
    }
  };

  const handleRegenerateScene = async (idx, prompt, narration) => {
    setRegeneratingIndex(idx);
    try {
      const { data } = await axios.post(`${API_BASE_URL}/regenerate-image`, {
        job_id: jobId, scene_index: idx, prompt, art_style: artStyle, narration
      });
      if (data.success) {
        const updated = [...storyboardScenes];
        updated[idx] = { ...updated[idx], image_url: `${API_BASE_URL}${data.image_url}?t=${Date.now()}`, visual: prompt };
        if (narration) updated[idx].narration = narration;
        setStoryboardScenes(updated);
      }
    } catch { alert('Failed to regenerate scene. Please try again.'); }
    finally { setRegeneratingIndex(null); }
  };

  const handleUploadImage = async (idx, file) => {
    if (!jobId) return;
    setUploadingIndex(idx);
    const form = new FormData();
    form.append('image', file); form.append('job_id', jobId); form.append('scene_index', idx);
    try {
      const { data } = await axios.post(`${API_BASE_URL}/upload-scene-image`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
      if (data.success) {
        const updated = [...storyboardScenes];
        updated[idx] = { ...updated[idx], image_url: `${API_BASE_URL}${data.image_url}` };
        setStoryboardScenes(updated);
      }
    } catch { alert('Failed to upload image.'); }
    finally { setUploadingIndex(null); }
  };

  const doReset = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    localStorage.clear();
    setStatus('idle'); setJobId(null); setScript(''); setStoryboardScenes(null);
    setPolishedScript(null); setVideoUrl(null); setError(''); setProgressPercent(0);
  };

  const phase = status === 'completed' ? 'export'
    : status === 'storyboard_ready' ? 'storyboard'
    : 'concept';

  const settingsProps = {
    voiceAccent, setVoiceAccent,
    captionStyle, setCaptionStyle,
    captionLang, setCaptionLang, videoResolution, setVideoResolution,
    isDialogueMode, setIsDialogueMode, voiceA, setVoiceA, voiceB, setVoiceB,
    transitionStyle, setTransitionStyle,
  };

  return (
    <div style={{ minHeight: '100vh', background: '#F2F7EE' }}>
      <TopNav phase={phase} onReset={doReset} studioTab={studioTab} setStudioTab={setStudioTab} />

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '28px 20px 60px' }}>

        <AnimatePresence mode="wait">
          {studioTab === 'video_to_video' ? (
            <motion.div key="video_to_video" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <VideoToVideoStudio />
            </motion.div>
          ) : (
            <motion.div key="image_to_video" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {/* Phase 1: Concept */}
              {(phase === 'concept') && (
                <ConceptPanel
                  script={script} setScript={setScript}
                  artStyle={artStyle} setArtStyle={setArtStyle}
                  onGenerate={handleGenerateStoryboard}
                  status={status} error={error}
                  {...settingsProps}
                />
              )}

              {/* Generating (progress overlay) */}
              {(status === 'generating_storyboard' || status === 'compiling') && (
                <RenderProgress progressText={progressText} progressPercent={progressPercent} status={status} />
              )}

              {/* Phase 2: Storyboard */}
              {phase === 'storyboard' && storyboardScenes && (
                <StoryboardPanel
                  storyboardScenes={storyboardScenes}
                  jobId={jobId} apiBaseUrl={API_BASE_URL}
                  onCompile={handleCompile} onReset={doReset}
                  regeneratingIndex={regeneratingIndex} uploadingIndex={uploadingIndex}
                  onRegenerate={handleRegenerateScene} onUpload={handleUploadImage}
                  getImgUrl={getSceneImageUrl}
                />
              )}

              {/* Phase 3: Export */}
              {phase === 'export' && videoUrl && (
                <ExportPanel
                  videoUrl={videoUrl} originalScript={script}
                  polishedScript={polishedScript} jobId={jobId}
                  apiBaseUrl={API_BASE_URL} onReset={doReset}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
