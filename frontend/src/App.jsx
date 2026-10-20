import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { RefreshCw, Video, Clapperboard, Edit, Check, X, Upload } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Editor, { createButton, Toolbar, BtnBold, BtnItalic, BtnUnderline, BtnBulletList, BtnLink, BtnClearFormatting, BtnUndo, BtnRedo } from 'react-simple-wysiwyg';

// Define custom alignment buttons using the library's utility
const BtnAlignLeft = createButton('Left align', '⬅️', 'justifyLeft');
const BtnAlignCenter = createButton('Center align', '🟰', 'justifyCenter');
const BtnAlignRight = createButton('Right align', '➡️', 'justifyRight');

// Import modular components
import ScriptInput from './components/ScriptInput';
import StyleSelector from './components/StyleSelector';
import ConfigPanel from './components/ConfigPanel';
import RenderStepper from './components/RenderStepper';
import ResultDisplay from './components/ResultDisplay';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

function App() {
  const [script, setScript] = useState('');
  const [status, setStatus] = useState('idle'); // idle, generating_storyboard, storyboard_ready, compiling, completed, error
  const [jobId, setJobId] = useState(null);
  const [progressText, setProgressText] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [videoUrl, setVideoUrl] = useState(null);
  const [polishedScript, setPolishedScript] = useState(null);
  
  // Custom Studio Upgrades States
  const [voiceAccent, setVoiceAccent] = useState('in_female');
  const [musicTrack, setMusicTrack] = useState('lofi');
  const [musicVolume, setMusicVolume] = useState('0.12');
  const [captionStyle, setCaptionStyle] = useState('tiktok');
  const [artStyle, setArtStyle] = useState('cinematic');
  const [videoMode, setVideoMode] = useState('shorts'); // 'shorts' | 'tutorial'
  const [videoResolution, setVideoResolution] = useState('1080p'); // '1080p' | '4k'

  // Multi-Character Dialogue & Transition States
  const [isDialogueMode, setIsDialogueMode] = useState(false);
  const [voiceA, setVoiceA] = useState('in_female');
  const [voiceB, setVoiceB] = useState('in_male');
  const [transitionStyle, setTransitionStyle] = useState('dynamic');

  // Storyboard editing states
  const [storyboardScenes, setStoryboardScenes] = useState(null);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);
  const [uploadingIndex, setUploadingIndex] = useState(null);
  const pollingTimeoutRef = useRef(null);

  const artStyles = [
    { id: 'cinematic', name: 'Cinematic Film', description: 'Photorealistic, dramatic lighting', icon: '🎬', gradient: 'from-amber-400 to-orange-500' },
    { id: 'cyberpunk', name: 'Cyberpunk', description: 'Neon synthwave glow', icon: '🌌', gradient: 'from-fuchsia-500 to-indigo-500' },
    { id: 'pixar', name: 'Pixar 3D', description: 'Vibrant, soft clay rendering', icon: '🧸', gradient: 'from-sky-400 to-blue-500' },
    { id: 'anime', name: 'Anime', description: 'Makoto Shinkai hand-drawn art', icon: '🌸', gradient: 'from-emerald-400 to-teal-500' },
    { id: 'oil_painting', name: 'Oil Painting', description: 'Canvas textures, classical style', icon: '🎨', gradient: 'from-rose-500 to-red-600' }
  ];

  const pipelineSteps = [
    { name: 'Script Polishing', desc: 'AI Storyboarding' },
    { name: 'Neural Voiceover', desc: 'Synthesizing voice' },
    { name: 'ASS Subtitles', desc: 'Whisper word-timestamps' },
    { name: 'Scene Art', desc: 'Generating background scenes' },
    { name: 'Video Render', desc: 'Concatenating & mixing audio' }
  ];

  const getActiveStepIndex = () => {
    if (status === 'generating_storyboard') {
      if (progressPercent < 20) return 0;  // Script polishing
      return 3;                             // Scene Art (Generating draft images)
    }
    // During compilation phase:
    if (progressPercent < 35) return 1;    // Neural Voiceover
    if (progressPercent < 60) return 2;    // ASS Subtitles
    if (progressPercent < 65) return 3;    // Scene Art (Proactive auto-recovery/checks)
    return 4;                               // Video render (FFmpeg stitching & burning)
  };

  const handleGenerateStoryboard = async () => {
    if (status === 'completed' || status === 'error') {
      if (pollingTimeoutRef.current) {
        clearTimeout(pollingTimeoutRef.current);
        pollingTimeoutRef.current = null;
      }
      setStatus('idle');
      setScript('');
      setVideoUrl(null);
      setPolishedScript(null);
      setStoryboardScenes(null);
      return;
    }

    if (!script.trim()) return;

    // Validate minimum word count — too few words produce poor storyboards
    const wordCount = script.trim().split(/\s+/).filter(Boolean).length;
    if (videoMode === 'shorts' && wordCount < 10) {
      setStatus('error');
      setProgressText(`Script too short (${wordCount} words). Please enter at least 10 words for a meaningful Short.`);
      return;
    }
    
    setStatus('generating_storyboard');
    setProgressText('Polishing script and building storyboard visual drafts...');
    setProgressPercent(5);
    setVideoUrl(null);
    setPolishedScript(null);
    setStoryboardScenes(null);

    try {
      const effectiveMode = isDialogueMode ? 'dialogue' : videoMode;
      const response = await axios.post(`${API_BASE_URL}/storyboard`, { 
        script,
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        voice_a: voiceA,
        voice_b: voiceB,
        transition_style: transitionStyle,
        music_track: musicTrack,
        caption_style: captionStyle,
        art_style: artStyle,
        music_volume: parseFloat(musicVolume),
        video_mode: effectiveMode,
        video_resolution: videoResolution
      });
      const newJobId = response.data.job_id;
      setJobId(newJobId);
      pollStatus(newJobId);
    } catch (error) {
      console.error(error);
      setStatus('error');
      setProgressText('Failed to initialize storyboard draft generation.');
    }
  };

  const handleRegenerateSceneImage = async (index, customPrompt, slideData = {}) => {
    setRegeneratingIndex(index);
    try {
      const response = await axios.post(`${API_BASE_URL}/regenerate-image`, {
        job_id: jobId,
        scene_index: index,
        prompt: customPrompt,
        art_style: artStyle,
        ...slideData
      });
      
      if (response.data.success) {
        const updatedScenes = [...storyboardScenes];
        // Append a cache-buster query parameter to force dynamic image reload in browser
        // eslint-disable-next-line react-hooks/purity
        const cacheBuster = `?t=${Date.now()}`;
        updatedScenes[index].image_url = `${API_BASE_URL}${response.data.image_url}${cacheBuster}`;
        updatedScenes[index].visual = customPrompt;
        
        // Sync updated slide metadata back to local state
        if (slideData.slide_title !== undefined) updatedScenes[index].slide_title = slideData.slide_title;
        if (slideData.bullets !== undefined) updatedScenes[index].bullets = slideData.bullets;
        if (slideData.code_snippet !== undefined) updatedScenes[index].code_snippet = slideData.code_snippet;
        if (slideData.narration !== undefined) updatedScenes[index].narration = slideData.narration;
        if (slideData.font_family !== undefined) updatedScenes[index].font_family = slideData.font_family;
        if (slideData.font_size !== undefined) updatedScenes[index].font_size = slideData.font_size;
        if (slideData.font_color !== undefined) updatedScenes[index].font_color = slideData.font_color;
        if (slideData.alignment !== undefined) updatedScenes[index].alignment = slideData.alignment;
        if (slideData.line_height !== undefined) updatedScenes[index].line_height = slideData.line_height;
        if (slideData.bg_color !== undefined) updatedScenes[index].bg_color = slideData.bg_color;
        if (slideData.slide_style !== undefined) updatedScenes[index].slide_style = slideData.slide_style;
        
        setStoryboardScenes(updatedScenes);
      }
    } catch (error) {
      console.error("Failed to regenerate image", error);
      alert("Failed to regenerate scene background. Please try again.");
    } finally {
      setRegeneratingIndex(null);
    }
  };

  const handleUploadSceneImage = async (sceneIdx, file) => {
    if (!jobId) return;
    
    setUploadingIndex(sceneIdx);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('job_id', jobId);
    formData.append('scene_index', sceneIdx);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload-scene-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      if (response.data.success) {
        const updatedScenes = [...storyboardScenes];
        updatedScenes[sceneIdx].image_url = `${API_BASE_URL}${response.data.image_url}`;
        setStoryboardScenes(updatedScenes);
      }
    } catch (error) {
      console.error('Failed to upload custom image:', error);
      alert('Failed to upload custom image. Please try again.');
    } finally {
      setUploadingIndex(null);
    }
  };

  const handleCompileVideo = async () => {
    setStatus('compiling');
    setProgressText('Voice synthesizers and video compilers standing by...');
    setProgressPercent(5);
    
    try {
      const effectiveMode = isDialogueMode ? 'dialogue' : videoMode;
      await axios.post(`${API_BASE_URL}/compile`, {
        job_id: jobId,
        voice_accent: isDialogueMode ? voiceA : voiceAccent,
        voice_a: voiceA,
        voice_b: voiceB,
        transition_style: transitionStyle,
        caption_style: captionStyle,
        music_track: musicTrack,
        music_volume: parseFloat(musicVolume),
        art_style: artStyle,
        video_mode: effectiveMode,
        video_resolution: videoResolution
      });
      pollStatus(jobId);
    } catch (error) {
      console.error(error);
      setStatus('error');
      setProgressText('Video compilation render failed.');
    }
  };

  function pollStatus(currentJobId, pollingMode = 'fast') {
    // Clear any active polling timer before initiating a new sequence
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }

    // Adaptive polling: 2s when storyboard generating (fast), 5s during long image/video render
    const fastInterval = 2000;
    const slowInterval = 5000;
    let currentDelay = pollingMode === 'fast' ? fastInterval : slowInterval;

    const doPoll = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/status/${currentJobId}`);
        const { state, message, polished_script, progress } = response.data;
        
        setProgressText(message);
        if (progress !== undefined) setProgressPercent(progress);
        if (polished_script) {
          setPolishedScript(polished_script);
          try { setStoryboardScenes(JSON.parse(polished_script)); } catch { /* Ignore storyboard parsing errors */ }
        }
        
        // Switch to slow polling when in the heavy image/video render phase (progress > 60%)
        if (progress > 60 && currentDelay === fastInterval) {
          currentDelay = slowInterval;
        }

        if (state === 'storyboard_ready') {
          setStatus('storyboard_ready');
          setProgressPercent(100);
          return; // Stop polling
        } else if (state === 'completed') {
          setStatus('completed');
          setProgressPercent(100);
          setVideoUrl(`${API_BASE_URL}/download/${currentJobId}.mp4`);
          return; // Stop polling
        } else if (state === 'error') {
          setStatus('error');
          setProgressPercent(0);
          return; // Stop polling
        }

        // Continue polling
        pollingTimeoutRef.current = setTimeout(doPoll, currentDelay);
      } catch {
        setStatus('error');
        setProgressText('Lost connection to server.');
      }
    };

    pollingTimeoutRef.current = setTimeout(doPoll, currentDelay);
  }

  // Save session state to localStorage when changes occur
  useEffect(() => {
    if (jobId) {
      localStorage.setItem('active_job_id', jobId);
      localStorage.setItem('active_job_status', status);
    } else {
      localStorage.removeItem('active_job_id');
      localStorage.removeItem('active_job_status');
    }
  }, [jobId, status]);

  useEffect(() => {
    if (script) localStorage.setItem('active_script', script);
    else localStorage.removeItem('active_script');
  }, [script]);

  useEffect(() => {
    localStorage.setItem('active_voice_accent', voiceAccent);
  }, [voiceAccent]);

  useEffect(() => {
    localStorage.setItem('active_music_track', musicTrack);
  }, [musicTrack]);

  useEffect(() => {
    localStorage.setItem('active_caption_style', captionStyle);
  }, [captionStyle]);

  useEffect(() => {
    localStorage.setItem('active_art_style', artStyle);
  }, [artStyle]);

  useEffect(() => {
    localStorage.setItem('active_video_mode', videoMode);
  }, [videoMode]);

  useEffect(() => {
    localStorage.setItem('active_video_resolution', videoResolution);
  }, [videoResolution]);

  // Auto-restore active session from localStorage on initial load
  useEffect(() => {
    const savedJobId = localStorage.getItem('active_job_id');
    const savedStatus = localStorage.getItem('active_job_status');
    const savedScript = localStorage.getItem('active_script');
    
    const savedVoice = localStorage.getItem('active_voice_accent');
    const savedMusic = localStorage.getItem('active_music_track');
    const savedCaption = localStorage.getItem('active_caption_style');
    const savedArt = localStorage.getItem('active_art_style');
    const savedMode = localStorage.getItem('active_video_mode');
    const savedRes = localStorage.getItem('active_video_resolution');

    if (savedScript) setScript(savedScript);
    if (savedVoice) {
      // Validate against current voice keys — discard stale keys from previous versions
      const VALID_VOICES = new Set([
        'in_female','in_male',
        'hi_female','hi_male',
        'bn_female','bn_male',
        'pa_female','pa_male',
        'bho_female','bho_male',
        'child_english','child_hindi',
      ]);
      if (VALID_VOICES.has(savedVoice)) setVoiceAccent(savedVoice);
      else localStorage.removeItem('active_voice_accent');
    }
    if (savedMusic) setMusicTrack(savedMusic);
    if (savedCaption) setCaptionStyle(savedCaption);
    if (savedArt) setArtStyle(savedArt);
    if (savedMode) setVideoMode(savedMode);
    if (savedRes) setVideoResolution(savedRes);

    if (savedJobId && savedStatus && savedStatus !== 'completed' && savedStatus !== 'idle') {
      setJobId(savedJobId);
      setStatus(savedStatus);
      pollStatus(savedJobId);
    }
  }, []);

  const getSceneImageUrl = (index) => {
    if (storyboardScenes && storyboardScenes[index] && storyboardScenes[index].image_url) {
      return storyboardScenes[index].image_url;
    }
    return `${API_BASE_URL}/output/${jobId}_scene_${String(index).padStart(2, '0')}.jpg`;
  };

  const activeStepIdx = getActiveStepIndex();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950 text-gray-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-10">
        
        {/* Header Block */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <motion.div 
              initial={{ scale: 0.9, opacity: 0.8 }}
              animate={{ scale: [0.9, 1.05, 0.9], opacity: [0.8, 1, 0.8] }}
              transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
              className="p-4 bg-indigo-600/10 rounded-3xl shadow-xl shadow-indigo-500/5 border border-indigo-500/20"
            >
              <Clapperboard className="w-14 h-14 text-indigo-400" />
            </motion.div>
          </div>
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl font-extrabold tracking-tight sm:text-6xl bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
          >
            Shorts Studio AI
          </motion.h1>
          <p className="mt-2 text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Overhaul raw scripts into dynamic YouTube Shorts. Powered by lifelike Neural TTS, contextual image storyboarding, and high-retention word highlights.
          </p>
        </div>

        {/* Studio Panel */}
        <div className="bg-gray-900/60 backdrop-blur-md shadow-2xl rounded-3xl overflow-hidden border border-gray-800 p-6 sm:p-8 space-y-8">
          
          {(status === 'idle' || status === 'error') && (
            <div className="space-y-6 animate-fadeIn">

              {/* Mode Toggle */}
              <div className="flex rounded-2xl overflow-hidden border border-gray-800 bg-gray-950/60 p-1 gap-1">
                <button
                  onClick={() => { setVideoMode('shorts'); setCaptionStyle('tiktok'); }}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all duration-200 cursor-pointer ${
                    videoMode === 'shorts'
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <span className="text-base">⚡</span>
                  <span>Viral Shorts</span>
                </button>
                <button
                  onClick={() => { setVideoMode('tutorial'); setCaptionStyle('elegant'); }}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all duration-200 cursor-pointer ${
                    videoMode === 'tutorial'
                      ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/20'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <span className="text-base">📚</span>
                  <span>Tutorial / How-To</span>
                </button>
              </div>

              {/* Mode description chip */}
              <div className={`text-xs px-4 py-2.5 rounded-xl border leading-relaxed ${
                videoMode === 'tutorial'
                  ? 'bg-emerald-950/30 border-emerald-800/40 text-emerald-300/80'
                  : 'bg-indigo-950/30 border-indigo-800/40 text-indigo-300/80'
              }`}>
                {videoMode === 'tutorial'
                  ? '📚 Tutorial Mode — AI structures your topic into numbered steps (Introduction + Step 1→N + Summary). Step labels shown on each scene. Calm instructional tone, 60–90 seconds.'
                  : '⚡ Viral Shorts Mode — AI rewrites your script into a punchy hook-first Short (5–7 scenes, 30 seconds, emoji subtitles, cinematic visuals).'}
              </div>

              {/* Input Area */}
              <ScriptInput 
                script={script} 
                setScript={setScript} 
                disabled={status.includes('generating')}
                placeholder={videoMode === 'tutorial'
                  ? 'Describe your tutorial topic... e.g. "How to make perfect scrambled eggs" or "Step-by-step Python list comprehensions"'
                  : 'Write your script idea... e.g. "Did you know honey never expires? Ancient Egyptians used it in tombs..."'}
              />

              {/* Visual Art Presets Selectors */}
              <StyleSelector 
                artStyle={artStyle} 
                setArtStyle={setArtStyle} 
                artStyles={artStyles} 
              />

              {/* Advanced Configurations */}
              <ConfigPanel 
                voiceAccent={voiceAccent}
                setVoiceAccent={setVoiceAccent}
                musicTrack={musicTrack}
                setMusicTrack={setMusicTrack}
                captionStyle={captionStyle}
                setCaptionStyle={setCaptionStyle}
                musicVolume={musicVolume}
                setMusicVolume={setMusicVolume}
                videoResolution={videoResolution}
                setVideoResolution={setVideoResolution}
                isDialogueMode={isDialogueMode}
                setIsDialogueMode={setIsDialogueMode}
                voiceA={voiceA}
                setVoiceA={setVoiceA}
                voiceB={voiceB}
                setVoiceB={setVoiceB}
                transitionStyle={transitionStyle}
                setTransitionStyle={setTransitionStyle}
              />
            </div>
          )}

          {/* Interactive Storyboard fine-tuning grid */}
          {status === 'storyboard_ready' && storyboardScenes && (
            <div className="space-y-6 animate-fadeIn">
              <div className="flex flex-col md:flex-row justify-between md:items-center border-b border-gray-800 pb-4 gap-4">
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent flex items-center">
                    🎨 Storyboard Fine-Tuning
                  </h2>
                  <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                    Review and modify visual prompts, regenerate scene art, and customize scripts prior to compilation.
                  </p>
                </div>
                <div className="flex gap-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      localStorage.clear();
                      setStatus('idle');
                      setJobId(null);
                      setScript('');
                      setStoryboardScenes(null);
                      setPolishedScript(null);
                      setVideoUrl(null);
                    }}
                    className="px-4 py-3.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold text-sm border border-gray-700 shadow-xl flex items-center justify-center cursor-pointer uppercase tracking-wider"
                  >
                    <X className="w-4 h-4 mr-2 text-red-400" />
                    Reset
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleCompileVideo}
                    className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-sm shadow-xl flex items-center justify-center cursor-pointer uppercase tracking-wider"
                  >
                    <Clapperboard className="w-4 h-4 mr-2" />
                    Render Final Video
                  </motion.button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {storyboardScenes.map((scene, idx) => (
                  <SceneCard 
                    key={idx}
                    idx={idx}
                    scene={scene}
                    imgUrl={getSceneImageUrl(idx)}
                    onRegenerate={(prompt, slideData) => handleRegenerateSceneImage(idx, prompt, slideData)}
                    isRegenerating={regeneratingIndex === idx}
                    onUploadImage={handleUploadSceneImage}
                    isUploading={uploadingIndex === idx}
                    videoMode={videoMode}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Pipeline Active Loader with Stepper */}
          <AnimatePresence>
            {(status === 'generating_storyboard' || status === 'compiling') && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.4 }}
                className="overflow-hidden"
              >
                <RenderStepper 
                  progressText={progressText} 
                  progressPercent={progressPercent} 
                  pipelineSteps={pipelineSteps} 
                  activeStepIdx={activeStepIdx} 
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Completed State Display */}
          <AnimatePresence>
            {status === 'completed' && videoUrl && (
              <ResultDisplay 
                videoUrl={videoUrl} 
                originalScript={script} 
                polishedScript={polishedScript} 
                jobId={jobId}
                apiBaseUrl={API_BASE_URL}
              />
            )}
          </AnimatePresence>

          {/* Action Trigger Button */}
          {(status === 'idle' || status === 'completed' || status === 'error') && (
            <motion.button
              type="button"
              onClick={handleGenerateStoryboard}
              disabled={status === 'idle' && !script.trim()}
              whileHover={status === 'idle' && !script.trim() ? {} : { scale: 1.02, boxShadow: "0 10px 25px -5px rgba(99,102,241,0.3)" }}
              whileTap={status === 'idle' && !script.trim() ? {} : { scale: 0.98 }}
              className="flex w-full justify-center items-center rounded-2xl bg-indigo-600 px-6 py-4 text-sm font-bold text-white shadow-xl hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all uppercase tracking-widest border border-indigo-500/20 cursor-pointer"
            >
              {status === 'completed' || status === 'error' ? (
                <>
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin-reverse" />
                  Generate New Video
                </>
              ) : (
                <>
                  <Video className="w-5 h-5 mr-2 animate-pulse" />
                  Create Storyboard Draft
                </>
              )}
            </motion.button>
          )}

          {/* Error Message Box */}
          {status === 'error' && (
            <div className="rounded-2xl bg-red-950/20 border border-red-500/30 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider">Pipeline Render Failed</h3>
                  <div className="mt-2 text-xs text-red-300/80 leading-relaxed">
                    <p>{progressText}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}

function SceneCard({ idx, scene, imgUrl, onRegenerate, isRegenerating, onUploadImage, isUploading, videoMode }) {
  const isSlide = videoMode === 'tutorial';
  
  const getSafeBulletsArray = (bulletsVal) => {
    if (Array.isArray(bulletsVal)) {
      return bulletsVal.map(b => {
        if (b && typeof b === 'object') {
          return `${b.title || ''}: ${b.description || ''}`;
        }
        return String(b);
      });
    }
    if (typeof bulletsVal === 'string') {
      return bulletsVal.split('\n').map(b => b.trim()).filter(Boolean);
    }
    return [];
  };
  
  const getSafeBulletsHTML = (bulletsVal) => {
    if (typeof bulletsVal === 'string' && bulletsVal.includes('<li')) {
      return bulletsVal;
    }
    const list = getSafeBulletsArray(bulletsVal);
    if (list.length === 0) return '';
    return '<ul>' + list.map(b => `<li>${b}</li>`).join('') + '</ul>';
  };
  
  const parseBulletsHTMLToArray = (htmlStr) => {
    if (!htmlStr) return [];
    const matchLi = /<li[^>]*>([\s\S]*?)<\/li>/gi;
    const items = [];
    let match;
    while ((match = matchLi.exec(htmlStr)) !== null) {
      const val = match[1].trim();
      if (val) {
        items.push(val);
      }
    }
    if (items.length > 0) return items;
    return htmlStr.split(/<br\s*\/?>/i).map(b => b.trim()).filter(Boolean);
  };

  const [editedPrompt, setEditedPrompt] = useState((scene && scene.visual) || '');
  const [editedTitle, setEditedTitle] = useState((scene && scene.slide_title) || '');
  const [editedBulletsHTML, setEditedBulletsHTML] = useState(getSafeBulletsHTML(scene && scene.bullets));
  const [editedCode, setEditedCode] = useState((scene && scene.code_snippet) || '');
  const [editedNarration, setEditedNarration] = useState((scene && scene.narration) || '');
  
  // Custom Typography & Slide Styling Overrides
  const [editedFontFamily, setEditedFontFamily] = useState(scene.font_family || 'sans');
  const [editedFontSize, setEditedFontSize] = useState(scene.font_size || 72);
  const [editedFontColor, setEditedFontColor] = useState(scene.font_color || '#1C1B1A');
  const [editedAlignment, setEditedAlignment] = useState(scene.alignment || 'left');
  const [editedLineHeight, setEditedLineHeight] = useState(scene.line_height || 1.35);
  const [editedBgColor, setEditedBgColor] = useState(scene.bg_color || '#F9F6F0');
  const [editedSlideStyle, setEditedSlideStyle] = useState(scene.slide_style || 'cinematic');
  
  const [isEditing, setIsEditing] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  // Sync state values when the parent updates scene object
  useEffect(() => {
    if (!scene) return;
    setEditedPrompt(scene.visual || '');
    setEditedTitle(scene.slide_title || '');
    setEditedBulletsHTML(getSafeBulletsHTML(scene.bullets));
    setEditedCode(scene.code_snippet || '');
    setEditedNarration(scene.narration || '');
    setEditedFontFamily(scene.font_family || 'sans');
    setEditedFontSize(scene.font_size || 72);
    setEditedFontColor(scene.font_color || '#1C1B1A');
    setEditedAlignment(scene.alignment || 'left');
    setEditedLineHeight(scene.line_height || 1.35);
    setEditedBgColor(scene.bg_color || '#F9F6F0');
    setEditedSlideStyle(scene.slide_style || 'cinematic');
  }, [scene]);

  if (!scene) return null;

  return (
    <div className="bg-gray-950/40 rounded-2xl border border-gray-800 overflow-hidden flex flex-col h-full shadow-lg">
      <div className="relative aspect-[9/16] max-h-[300px] bg-gray-950 overflow-hidden group flex items-center justify-center border-b border-gray-900">
        {/* Shimmer skeleton shown while image is loading */}
        {!imgLoaded && !isRegenerating && !isUploading && (
          <div className="absolute inset-0 bg-gray-900 animate-pulse">
            <div className="h-full w-full bg-gradient-to-br from-gray-800/60 via-gray-900 to-gray-800/40" />
          </div>
        )}
        <img 
          src={imgUrl} 
          alt={`Scene ${idx + 1}`} 
          className={`w-full h-full object-cover transition-all duration-500 group-hover:scale-102 ${imgLoaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={() => setImgLoaded(true)}
          onError={(e) => {
            setImgLoaded(true);
            e.target.src = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80";
          }}
        />
        <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold border border-gray-800/80 text-amber-400 z-10 flex items-center gap-1.5">
          <span>{isSlide ? `Slide ${idx + 1}` : `Scene ${idx + 1}`}</span>
          {scene.speaker && (
            <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-black tracking-wider ${
              scene.voice_gender === 'female' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}>
              🗣️ {scene.speaker}
            </span>
          )}
        </div>
        
        {/* Custom File Upload Hover Overlay */}
        {!isRegenerating && !isUploading && (
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center gap-2 z-10">
            <label className="p-3.5 rounded-full bg-indigo-600/90 hover:bg-indigo-500 text-white cursor-pointer shadow-xl transition-all hover:scale-110 flex items-center justify-center border border-indigo-400/20 active:scale-95">
              <Upload className="w-5 h-5" />
              <input 
                type="file" 
                accept="image/*" 
                className="hidden" 
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file && onUploadImage) {
                    onUploadImage(idx, file);
                  }
                }}
              />
            </label>
          </div>
        )}

        {isRegenerating && (
          <div className="absolute inset-0 bg-black/85 backdrop-blur-sm flex flex-col items-center justify-center space-y-3 z-10">
            <RefreshCw className="w-8 h-8 text-amber-400 animate-spin" />
            <p className="text-xs text-amber-400 font-bold uppercase tracking-wider animate-pulse">Regenerating Slide...</p>
          </div>
        )}

        {isUploading && (
          <div className="absolute inset-0 bg-black/85 backdrop-blur-sm flex flex-col items-center justify-center space-y-3 z-10">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs text-indigo-400 font-bold uppercase tracking-wider animate-pulse">Uploading Image...</p>
          </div>
        )}
      </div>
      
      <div className="p-5 flex-1 flex flex-col space-y-4 justify-between">
        <div className="space-y-4">
          
          {/* Spoken Voiceover Narration */}
          <div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Spoken voiceover script</span>
            {isEditing ? (
              <textarea
                value={editedNarration}
                onChange={(e) => setEditedNarration(e.target.value)}
                className="w-full text-xs bg-gray-950 border border-gray-800 rounded-xl p-3 text-gray-300 focus:outline-none focus:border-indigo-500/50 min-h-[50px] resize-none leading-relaxed"
                placeholder="Narration script spoken by neural TTS..."
              />
            ) : (
              <p className="text-xs text-gray-200 leading-relaxed font-semibold bg-gray-950/60 p-3 rounded-xl border border-gray-800/60 shadow-inner">
                {scene.narration}
              </p>
            )}
          </div>

          {/* Slide Title & Bullets */}
          {isSlide && (
            <div className="space-y-3 bg-indigo-950/10 border border-indigo-900/30 rounded-xl p-3.5 shadow-inner">
              <div className="flex items-center gap-2 mb-2 border-b border-indigo-950/40 pb-1.5">
                <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">Slide Design Layout</span>
              </div>
              
              {isEditing ? (
                <div className="space-y-3">
                  <div>
                    <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Slide Heading</label>
                    <input
                      type="text"
                      value={editedTitle}
                      onChange={(e) => setEditedTitle(e.target.value)}
                      className="w-full text-xs bg-gray-950 border border-gray-800 rounded-lg px-2.5 py-1.5 text-gray-300 focus:outline-none focus:border-indigo-500/50"
                      placeholder="Slide title"
                    />
                  </div>
                  <div>
                    <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Bullet Points & Content (Rich WYSIWYG Editor)</label>
                    <div className="rich-editor-wrapper text-xs text-gray-200 bg-gray-950 border border-gray-800 rounded-lg overflow-hidden">
                      <Editor value={editedBulletsHTML} onChange={(e) => setEditedBulletsHTML(e.target.value)}>
                        <Toolbar>
                          <BtnBold />
                          <BtnItalic />
                          <BtnUnderline />
                          <BtnBulletList />
                          <BtnAlignLeft />
                          <BtnAlignCenter />
                          <BtnAlignRight />
                          <BtnClearFormatting />
                        </Toolbar>
                      </Editor>
                    </div>
                  </div>
                  
                  {/* PPT Typography & Design Overrides Toolbar */}
                  <div className="bg-gray-900/60 rounded-xl p-3 border border-gray-800 space-y-3">
                    <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest block border-b border-gray-850 pb-1">
                      🎨 Slide Canvas & PPT Styles
                    </span>
                    
                    {/* PPT Template Override */}
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">PPT Slide Theme</label>
                        <select
                          value={editedSlideStyle}
                          onChange={(e) => setEditedSlideStyle(e.target.value)}
                          className="w-full text-[11px] bg-gray-950 border border-gray-850 rounded-lg p-1.5 text-gray-300 focus:outline-none focus:border-indigo-500/50"
                        >
                          <option value="cinematic">Cinematic Cream</option>
                          <option value="cyberpunk">Cyberpunk Neon</option>
                          <option value="pixar">Cozy Pixar</option>
                          <option value="anime">Anime Sky</option>
                          <option value="oil_painting">Oil Painting Gold</option>
                        </select>
                      </div>
                      
                      {/* Font Family Selection */}
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Font Family</label>
                        <select
                          value={editedFontFamily}
                          onChange={(e) => setEditedFontFamily(e.target.value)}
                          className="w-full text-[11px] bg-gray-950 border border-gray-855 rounded-lg p-1.5 text-gray-300 focus:outline-none focus:border-indigo-500/50"
                        >
                          <option value="sans">Sans-Serif (Modern)</option>
                          <option value="serif">Serif (Classical)</option>
                          <option value="mono">Monospace (Code)</option>
                        </select>
                      </div>
                    </div>

                    {/* Font Size & Line Height Sliders */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Font Size: {editedFontSize}px</label>
                        <input
                          type="range"
                          min="40"
                          max="120"
                          value={editedFontSize}
                          onChange={(e) => setEditedFontSize(parseInt(e.target.value))}
                          className="w-full h-1.5 bg-gray-950 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Line Height: {editedLineHeight}</label>
                        <input
                          type="range"
                          min="1"
                          max="2"
                          step="0.05"
                          value={editedLineHeight}
                          onChange={(e) => setEditedLineHeight(parseFloat(e.target.value))}
                          className="w-full h-1.5 bg-gray-950 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                        />
                      </div>
                    </div>

                    {/* Background & Text Color pickers */}
                    <div className="grid grid-cols-2 gap-3 border-t border-gray-850/40 pt-2">
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Slide Canvas Color</label>
                        <div className="flex items-center gap-1.5">
                          <input
                            type="color"
                            value={editedBgColor.startsWith('#') ? editedBgColor : '#F9F6F0'}
                            onChange={(e) => setEditedBgColor(e.target.value)}
                            className="w-6 h-6 rounded-md cursor-pointer border border-gray-800 bg-transparent"
                          />
                          <input
                            type="text"
                            value={editedBgColor}
                            onChange={(e) => setEditedBgColor(e.target.value)}
                            className="flex-1 text-[10px] bg-gray-950 border border-gray-855 rounded-lg px-2 py-0.5 text-gray-300 focus:outline-none"
                            placeholder="#F9F6F0"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Typographic Color</label>
                        <div className="flex items-center gap-1.5">
                          <input
                            type="color"
                            value={editedFontColor.startsWith('#') ? editedFontColor : '#1C1B1A'}
                            onChange={(e) => setEditedFontColor(e.target.value)}
                            className="w-6 h-6 rounded-md cursor-pointer border border-gray-800 bg-transparent"
                          />
                          <input
                            type="text"
                            value={editedFontColor}
                            onChange={(e) => setEditedFontColor(e.target.value)}
                            className="flex-1 text-[10px] bg-gray-950 border border-gray-855 rounded-lg px-2 py-0.5 text-gray-300 focus:outline-none"
                            placeholder="#1C1B1A"
                          />
                        </div>
                      </div>
                    </div>
                    
                    {/* Horizontal Alignment Option Selector */}
                    <div className="flex items-center justify-between border-t border-gray-850/40 pt-2">
                      <span className="text-[9px] font-bold text-gray-400 uppercase">Text Alignment</span>
                      <div className="flex bg-gray-950 p-0.5 rounded-lg border border-gray-850">
                        {['left', 'center', 'right'].map((align) => (
                          <button
                            key={align}
                            type="button"
                            onClick={() => setEditedAlignment(align)}
                            className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase transition-all ${
                              editedAlignment === align
                                ? 'bg-indigo-600 text-white shadow-sm'
                                : 'text-gray-400 hover:text-gray-300'
                            }`}
                          >
                            {align}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-[9px] font-bold text-gray-400 uppercase block mb-1">Optional Code Box (Single or Multi-line)</label>
                    <textarea
                      value={editedCode}
                      onChange={(e) => setEditedCode(e.target.value)}
                      className="w-full text-xs font-mono bg-gray-950 border border-gray-800 rounded-lg p-2 text-emerald-400 focus:outline-none focus:border-indigo-500/50 min-h-[50px] resize-none leading-relaxed"
                      placeholder="my_var = [1, 2, 3]"
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <span className="text-[10px]">📌</span>
                    <span>{scene.slide_title}</span>
                  </div>
                  
                  {/* Rich HTML slide bullets preview safely formatted */}
                  <div 
                    className="text-[11px] text-gray-300 leading-relaxed rich-bullets-preview"
                    dangerouslySetInnerHTML={{ __html: getSafeBulletsHTML(scene.bullets) }}
                  />
                  
                  {/* PPT Settings Override Badge Pills */}
                  <div className="flex flex-wrap gap-1.5 pt-2 mt-1 border-t border-indigo-950/40">
                    {scene.slide_style && (
                      <span className="text-[8px] font-bold bg-indigo-950/30 text-indigo-400 px-2 py-0.5 rounded-md uppercase tracking-wider">
                        Theme: {scene.slide_style}
                      </span>
                    )}
                    {scene.bg_color && (
                      <span className="text-[8px] font-bold bg-amber-950/30 text-amber-400 px-2 py-0.5 rounded-md uppercase tracking-wider flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ backgroundColor: scene.bg_color }} />
                        BG: {scene.bg_color}
                      </span>
                    )}
                    {scene.font_family && (
                      <span className="text-[8px] font-bold bg-teal-950/30 text-teal-400 px-2 py-0.5 rounded-md uppercase tracking-wider">
                        Font: {scene.font_family}
                      </span>
                    )}
                    {scene.alignment && (
                      <span className="text-[8px] font-bold bg-fuchsia-950/30 text-fuchsia-400 px-2 py-0.5 rounded-md uppercase tracking-wider">
                        Align: {scene.alignment}
                      </span>
                    )}
                  </div>

                  {scene.code_snippet && (
                    <div className="mt-2 text-[10px] font-mono bg-black/60 text-emerald-400 p-2 rounded-lg border border-gray-850 shadow-inner overflow-x-auto whitespace-pre">
                      {scene.code_snippet}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Background Visual Art Prompt */}
          <div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">
              {isSlide ? "Slide Illustration Icon Prompt" : "Visual Art Prompt"}
            </span>
            {isEditing ? (
              <textarea
                value={editedPrompt}
                onChange={(e) => setEditedPrompt(e.target.value)}
                className="w-full text-xs bg-gray-950 border border-gray-800 rounded-xl p-3 text-gray-300 focus:outline-none focus:border-indigo-500/50 min-h-[60px] resize-none leading-relaxed"
              />
            ) : (
              <p className="text-xs text-gray-400 leading-relaxed bg-gray-950/20 p-3 rounded-xl border border-gray-855/30 italic">
                {scene.visual}
              </p>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex space-x-2 pt-2 border-t border-gray-850/40">
          {isEditing ? (
            <>
              <button
                onClick={() => {
                  setIsEditing(false);
                  const bulletsList = parseBulletsHTMLToArray(editedBulletsHTML);
                  
                  onRegenerate(editedPrompt, {
                    slide_title: editedTitle,
                    bullets: bulletsList,
                    code_snippet: editedCode,
                    narration: editedNarration,
                    font_family: editedFontFamily,
                    font_size: editedFontSize,
                    font_color: editedFontColor,
                    alignment: editedAlignment,
                    line_height: editedLineHeight,
                    bg_color: editedBgColor,
                    slide_style: editedSlideStyle
                  });
                }}
                className="flex-1 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-black font-bold text-xs shadow-md transition-all cursor-pointer flex items-center justify-center space-x-1"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save & Redraw Slide</span>
              </button>
              <button
                onClick={() => {
                  setEditedPrompt(scene.visual || '');
                  setEditedTitle(scene.slide_title || '');
                  setEditedBulletsHTML(getSafeBulletsHTML(scene.bullets));
                  setEditedCode(scene.code_snippet || '');
                  setEditedNarration(scene.narration || '');
                  setEditedFontFamily(scene.font_family || 'sans');
                  setEditedFontSize(scene.font_size || 72);
                  setEditedFontColor(scene.font_color || '#1C1B1A');
                  setEditedAlignment(scene.alignment || 'left');
                  setEditedLineHeight(scene.line_height || 1.35);
                  setEditedBgColor(scene.bg_color || '#F9F6F0');
                  setEditedSlideStyle(scene.slide_style || 'cinematic');
                  setIsEditing(false);
                }}
                className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold text-xs transition-all cursor-pointer flex items-center justify-center"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="w-full py-2.5 rounded-xl bg-gray-800/40 hover:bg-gray-800/80 text-gray-300 font-bold text-xs border border-gray-800/50 transition-all flex items-center justify-center space-x-1 cursor-pointer"
            >
              <Edit className="w-3.5 h-3.5 mr-1 text-gray-400" />
              <span>Modify Slide Details</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

