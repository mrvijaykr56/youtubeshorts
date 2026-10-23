import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Video, Sparkles, Upload, Copy, Check, Play, Pause,
  Trash2, RefreshCw, Wand2, ArrowRight, ExternalLink,
  Film, Settings2, Sliders, Volume2, Music, CheckCircle2
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function VideoToVideoStudio() {
  // Directing State
  const [topic, setTopic] = useState('');
  const [promptLanguage, setPromptLanguage] = useState('English');
  const [isDirecting, setIsDirecting] = useState(false);
  const [scenes, setScenes] = useState([
    {
      scene_number: 1,
      narration: 'Deep beneath the ocean lies a hidden realm that science cannot explain. 🌊',
      video_prompt: 'Vertical 9:16 ratio. Cinematic slow drone descent into a dark bioluminescent oceanic trench. Glowing cyan crystal towers emit pulsing light. Photorealistic 8K, volumetric lighting, 24fps.'
    },
    {
      scene_number: 2,
      narration: 'In twenty twenty-six, autonomous probes detected rhythmic light pulses miles underwater. 🔬',
      video_prompt: 'Vertical 9:16 ratio. Orbital 360 camera sweep around a futuristic titanium underwater submarine with headlights cutting through dark water. 8K, cinematic volumetric depth.'
    },
    {
      scene_number: 3,
      narration: 'Massive organic structures moved in intelligent geometric harmony. ✨',
      video_prompt: 'Vertical 9:16 ratio. Macro slow-motion shot of iridescent underwater tentacles pulsing with golden electric sparks. Realistic fluid simulation, 8K, 24fps.'
    },
    {
      scene_number: 4,
      narration: 'Every pulse transmitted synchronized energy across the entire seafloor. ⚡',
      video_prompt: 'Vertical 9:16 ratio. Dramatic low-angle tilt up revealing an enormous glowing underwater citadel. Shockwaves of blue energy rippling outward across the sand.'
    },
    {
      scene_number: 5,
      narration: 'Are these ancient earthly guardians, or something beyond our world? Subscribe for part two! 🔔',
      video_prompt: 'Vertical 9:16 ratio. Cinematic slow camera pull back into misty blue deep waters as ancient structures glow brightly in the distance. 8K, motion blur, 24fps.'
    }
  ]);

  // Uploaded Clips (Indexed by scene 0..4)
  const [clips, setClips] = useState([null, null, null, null, null]);
  const [copiedIndex, setCopiedIndex] = useState(null);

  // Settings
  const [resolution, setResolution] = useState('4k');
  const [durationMode, setDurationMode] = useState('speed_ramp');
  const [transitionStyle, setTransitionStyle] = useState('dynamic');
  const [voiceAccent, setVoiceAccent] = useState('in_female');
  const [captionStyle, setCaptionStyle] = useState('tiktok');
  const [captionLang, setCaptionLang] = useState('English');
  const [musicTrack, setMusicTrack] = useState('lofi');

  // Assembly & Job State
  const [isAssembling, setIsAssembling] = useState(false);
  const [assemblyProgress, setAssemblyProgress] = useState(0);
  const [assemblyMessage, setAssemblyMessage] = useState('');
  const [jobId, setJobId] = useState(null);
  const [finalVideoUrl, setFinalVideoUrl] = useState(null);
  const [errorText, setErrorText] = useState(null);

  const fileInputRefs = useRef([]);

  // Copy helper
  const handleCopyPrompt = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  // Generate Prompts with Gemini Pro
  const handleGeneratePrompts = async () => {
    if (!topic.trim()) return;
    setIsDirecting(true);
    setErrorText(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/generate-video-prompts`, {
        topic: topic.trim(),
        language: promptLanguage
      });
      if (res.data?.scenes && Array.isArray(res.data.scenes)) {
        setScenes(res.data.scenes);
      }
    } catch (err) {
      console.error('Failed to generate prompts:', err);
      setErrorText('Failed to direct prompts. Check backend connection.');
    } finally {
      setIsDirecting(false);
    }
  };

  // Handle single file upload per slot
  const handleFileChange = (e, slotIdx) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const newClips = [...clips];
    newClips[slotIdx] = {
      file,
      name: file.name,
      sizeMb: (file.size / (1024 * 1024)).toFixed(1),
      previewUrl: URL.createObjectURL(file)
    };
    setClips(newClips);
  };

  // Batch drop files
  const handleBatchDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('video/'));
    if (files.length === 0) return;

    const newClips = [...clips];
    files.slice(0, 5).forEach((file, i) => {
      newClips[i] = {
        file,
        name: file.name,
        sizeMb: (file.size / (1024 * 1024)).toFixed(1),
        previewUrl: URL.createObjectURL(file)
      };
    });
    setClips(newClips);
  };

  // Remove clip
  const handleRemoveClip = (slotIdx) => {
    const newClips = [...clips];
    if (newClips[slotIdx]?.previewUrl) {
      URL.revokeObjectURL(newClips[slotIdx].previewUrl);
    }
    newClips[slotIdx] = null;
    setClips(newClips);
  };

  // Polling Job Status
  const pollStatus = async (currentJobId) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/status/${currentJobId}`);
      const data = res.data;
      setAssemblyProgress(data.progress || 10);
      setAssemblyMessage(data.message || 'Processing video layers...');

      if (data.state === 'completed') {
        setIsAssembling(false);
        setAssemblyProgress(100);
        setFinalVideoUrl(`${API_BASE_URL}/download/${currentJobId}?t=${Date.now()}`);
      } else if (data.state === 'error') {
        setIsAssembling(false);
        setErrorText(data.message || 'Assembly encountered an error.');
      } else {
        setTimeout(() => pollStatus(currentJobId), 1500);
      }
    } catch (err) {
      console.error('Error polling status:', err);
      setTimeout(() => pollStatus(currentJobId), 2000);
    }
  };

  // Submit Assembly Job
  const handleAssemble = async () => {
    const validClips = clips.filter(Boolean);
    if (validClips.length === 0) {
      setErrorText('Please upload at least 1 video clip before assembling.');
      return;
    }

    setIsAssembling(true);
    setAssemblyProgress(10);
    setAssemblyMessage('Uploading clips and configuring timeline...');
    setFinalVideoUrl(null);
    setErrorText(null);

    try {
      const formData = new FormData();
      validClips.forEach((c, idx) => {
        formData.append(`clip_${idx}`, c.file);
      });

      formData.append('script', JSON.stringify(scenes));
      formData.append('voice_accent', voiceAccent);
      formData.append('caption_style', captionStyle);
      formData.append('caption_lang', captionLang);
      formData.append('music_track', musicTrack);
      formData.append('video_resolution', resolution);
      formData.append('transition_style', transitionStyle);
      formData.append('duration_mode', durationMode);

      const res = await axios.post(`${API_BASE_URL}/upload-video-clips`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const newJobId = res.data.job_id;
      setJobId(newJobId);
      pollStatus(newJobId);
    } catch (err) {
      console.error('Assembly submission failed:', err);
      setIsAssembling(false);
      setErrorText('Failed to start assembly job. Ensure backend is running.');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner (Lemon Accent) */}
      <div className="lemon-card p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 border-slate-200">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-800 text-xs font-bold uppercase tracking-wider">
            <span style={{ color: '#0F172A' }}>✨</span>
            <span>Generative Video-to-Video Engine</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
            Multi-Clip AI Video Studio <span style={{ color: '#0F172A', background: '#D4F84A', padding: '2px 8px', borderRadius: '8px' }}>(4K / 8K)</span>
          </h1>
          <p className="text-sm text-slate-500 max-w-xl leading-relaxed">
            Direct and stitch 5 AI video clips (Google Veo, VideoFX, Luma, Kling) into an ultra-high-definition, 
            cinematic YouTube Short or Reel with seamless transitions, TTS voiceover, and kinetic captions.
          </p>
        </div>

        <a
          href="https://labs.google/fx/tools/video-fx"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition-all shadow-sm shrink-0"
        >
          <span>Open Google VideoFX</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* STEP 1: Gemini Pro Video Prompt Director */}
      <div className="lemon-card p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div style={{ background: '#D4F84A' }} className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-900 font-extrabold text-sm">
              1
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Direct 5-Scene Storyboard with Gemini Pro</h2>
              <p className="text-xs text-slate-400">Generates synchronized narration and Google Veo / VideoFX camera prompts.</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={promptLanguage}
              onChange={(e) => setPromptLanguage(e.target.value)}
              className="lemon-input py-1.5 px-3 text-xs"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Hinglish">Hinglish</option>
            </select>

            <button
              onClick={handleGeneratePrompts}
              disabled={isDirecting || !topic.trim()}
              className="lemon-btn-primary py-2 px-4 text-xs"
            >
              {isDirecting ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Directing...
                </>
              ) : (
                <>
                  <Wand2 className="w-3.5 h-3.5" /> Direct Storyboard
                </>
              )}
            </button>
          </div>
        </div>

        <div>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. Mysterious ancient glowing city discovered in deepest oceanic trench..."
            className="w-full lemon-input text-sm"
          />
        </div>

        {/* 5 Generated Scene Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-1">
          {scenes.map((s, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-slate-200 bg-slate-50/60 p-3 flex flex-col justify-between space-y-2.5 hover:border-slate-300 transition-colors"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-slate-200/80 text-slate-800">
                    Scene {s.scene_number || idx + 1}
                  </span>
                  <button
                    onClick={() => handleCopyPrompt(s.video_prompt, idx)}
                    className="text-slate-400 hover:text-slate-900 p-1 rounded hover:bg-slate-200/60 transition-colors cursor-pointer"
                    title="Copy Veo prompt"
                  >
                    {copiedIndex === idx ? (
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-500 block mb-1">Narration:</label>
                  <textarea
                    rows={2}
                    value={s.narration}
                    onChange={(e) => {
                      const updated = [...scenes];
                      updated[idx].narration = e.target.value;
                      setScenes(updated);
                    }}
                    className="w-full lemon-input text-[11px] p-2 resize-none leading-snug"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-500 block mb-1">Veo / VideoFX Prompt:</label>
                  <div className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded p-2 max-h-24 overflow-y-auto leading-relaxed select-all">
                    {s.video_prompt}
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleCopyPrompt(s.video_prompt, idx)}
                className="w-full text-center text-[10px] py-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-800 border border-slate-200 transition-all font-bold flex items-center justify-center gap-1.5 cursor-pointer shadow-2xs"
              >
                {copiedIndex === idx ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-600" /> Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" /> Copy Prompt
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* STEP 2: Drag & Drop 5 Video Clips */}
      <div className="lemon-card p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <div style={{ background: '#D4F84A' }} className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-900 font-extrabold text-sm">
              2
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Upload Generated AI Video Clips (Up to 5)</h2>
              <p className="text-xs text-slate-400">Drag and drop your 9:16 clips from Google Veo, VideoFX, or Luma.</p>
            </div>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleBatchDrop}
            className="text-xs text-slate-700 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium"
          >
            <Upload className="w-3.5 h-3.5" /> Drag all 5 clips here
          </div>
        </div>

        {/* 5 Slot Upload Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          {[0, 1, 2, 3, 4].map((slotIdx) => {
            const clip = clips[slotIdx];
            return (
              <div
                key={slotIdx}
                className={`relative rounded-xl border-2 transition-all p-3 flex flex-col justify-between items-center min-h-[200px] ${
                  clip
                    ? 'border-slate-800 bg-slate-50'
                    : 'border-dashed border-slate-200 bg-slate-50/50 hover:border-slate-300'
                }`}
              >
                <div className="w-full flex items-center justify-between text-[11px] text-slate-500 mb-1.5">
                  <span className="font-bold text-slate-800">Clip #{slotIdx + 1}</span>
                  {clip && (
                    <button
                      onClick={() => handleRemoveClip(slotIdx)}
                      className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors cursor-pointer"
                      title="Remove clip"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {clip ? (
                  <div className="w-full flex flex-col items-center space-y-2">
                    <div className="w-full aspect-[9/16] max-h-36 rounded-lg overflow-hidden bg-black border border-slate-200 relative">
                      <video
                        src={clip.previewUrl}
                        className="w-full h-full object-cover"
                        controls
                        muted
                      />
                    </div>
                    <div className="w-full text-center">
                      <p className="text-[11px] text-slate-800 font-semibold truncate w-full" title={clip.name}>
                        {clip.name}
                      </p>
                      <span className="text-[10px] text-slate-400">{clip.sizeMb} MB</span>
                    </div>
                  </div>
                ) : (
                  <div
                    onClick={() => fileInputRefs.current[slotIdx]?.click()}
                    className="w-full flex-1 flex flex-col items-center justify-center gap-2 cursor-pointer p-3 text-center group"
                  >
                    <div className="w-9 h-9 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-400 group-hover:text-slate-800 group-hover:border-slate-400 transition-colors shadow-2xs">
                      <Upload className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-[11px] font-bold text-slate-600 group-hover:text-slate-900 transition-colors">
                      Select Clip #{slotIdx + 1}
                    </span>
                    <span className="text-[9px] text-slate-400">.mp4 (9:16)</span>
                  </div>
                )}

                <input
                  ref={(el) => (fileInputRefs.current[slotIdx] = el)}
                  type="file"
                  accept="video/*"
                  className="hidden"
                  onChange={(e) => handleFileChange(e, slotIdx)}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* STEP 3: Studio Customization & Assembly Settings */}
      <div className="lemon-card p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div style={{ background: '#D4F84A' }} className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-900 font-extrabold text-sm">
            3
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Timeline, Audio & Mastering Controls</h2>
            <p className="text-xs text-slate-400">Configure resolution, duration speed-ramping, transitions, and audio sync.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1">
          {/* Resolution */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Target Resolution</label>
            <select
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              className="w-full lemon-input"
            >
              <option value="1080p">1080p Full HD</option>
              <option value="4k">4K Ultra HD (Recommended)</option>
              <option value="8k">8K Master</option>
            </select>
          </div>

          {/* Duration Mode */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Duration Adaptation</label>
            <select
              value={durationMode}
              onChange={(e) => setDurationMode(e.target.value)}
              className="w-full lemon-input"
            >
              <option value="speed_ramp">Speed-Ramp (Preserve motion)</option>
              <option value="trim">Clean Trim (Cut to voice)</option>
            </select>
          </div>

          {/* Transitions */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Scene Transitions</label>
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

          {/* Voiceover Accent */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Narration Voice</label>
            <select
              value={voiceAccent}
              onChange={(e) => setVoiceAccent(e.target.value)}
              className="w-full lemon-input"
            >
              <option value="in_female">Indian English — Female (Neerja)</option>
              <option value="in_male">Indian English — Male (Prabhat)</option>
              <option value="hi_female">Hindi — Female (Swara)</option>
              <option value="hi_male">Hindi — Male (Madhur)</option>
              <option value="us">US English — Professional</option>
            </select>
          </div>

          {/* Captions Style */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Captions Style</label>
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

          {/* Captions Language */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Subtitle Language</label>
            <select
              value={captionLang}
              onChange={(e) => setCaptionLang(e.target.value)}
              className="w-full lemon-input"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
            </select>
          </div>

          {/* Background Music */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-700">Background Music</label>
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

        {/* Action Button */}
        <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-500">
            Clips ready:{' '}
            <span className="font-bold text-slate-900">
              {clips.filter(Boolean).length} of 5 selected
            </span>
          </div>

          <button
            onClick={handleAssemble}
            disabled={isAssembling || clips.filter(Boolean).length === 0}
            className="w-full sm:w-auto lemon-btn-primary py-3 px-8 text-xs font-bold"
          >
            {isAssembling ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Assembling Video Short...
              </>
            ) : (
              <>
                <Film className="w-4 h-4" /> Assemble Ultra Video Short
              </>
            )}
          </button>
        </div>
      </div>

      {/* Assembly Progress & Output Display */}
      {isAssembling && (
        <div className="lemon-card p-6 border-slate-300 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-slate-900">
            <span>{assemblyMessage}</span>
            <span>{assemblyProgress}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-slate-900 h-full transition-all duration-300 rounded-full"
              style={{ width: `${assemblyProgress}%` }}
            />
          </div>
        </div>
      )}

      {errorText && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold">
          {errorText}
        </div>
      )}

      {finalVideoUrl && (
        <div className="lemon-card p-6 md:p-8 space-y-6 max-w-2xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-900 font-extrabold text-lg">
              <CheckCircle2 className="w-6 h-6 text-emerald-500" />
              <span>Master Video Ready!</span>
            </div>
            <a
              href={finalVideoUrl}
              download="master_video_short.mp4"
              className="lemon-btn-primary px-5 py-2 text-xs"
            >
              <Download className="w-3.5 h-3.5" /> Download MP4
            </a>
          </div>

          <div className="max-w-md mx-auto aspect-[9/16] rounded-2xl overflow-hidden bg-black border border-slate-200 shadow-xl">
            <video src={finalVideoUrl} controls autoPlay className="w-full h-full object-cover" />
          </div>
        </div>
      )}
    </div>
  );
}
