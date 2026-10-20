import { useState } from 'react';
import { PlayCircle, Download, Share2, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const YoutubeIcon = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.508 9.388.508 9.388.508s7.518 0 9.388-.508a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
  </svg>
);

export default function ResultDisplay({ videoUrl, originalScript, polishedScript, jobId, apiBaseUrl }) {
  const [uploadTitle, setUploadTitle] = useState('My AI Short');
  const [uploadDesc, setUploadDesc] = useState('Auto-generated using Shorts Studio AI');
  const [uploadTags, setUploadTags] = useState('shorts, ai, generated');
  
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadError, setUploadError] = useState('');
  const [youtubeVideoId, setYoutubeVideoId] = useState('');
  const [manualPack, setManualPack] = useState(null);

  const handleDownload = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    try {
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `shorts_${jobId}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Fetch download failed, falling back to direct link", error);
      window.open(videoUrl, '_blank');
    }
  };

  const getParsedScenes = () => {
    if (!polishedScript) return [];
    try {
      const parsed = JSON.parse(polishedScript);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    } catch {
      // legacy delimiter format fallback
    }

    const scenes = [];
    const blocks = polishedScript.split('---SCENE---');
    blocks.forEach((block) => {
      const trimText = block.trim();
      if (!trimText) return;
      const narrationMatch = trimText.match(/NARRATION:\s*(.*?)(?=VISUAL:|$)/si);
      const narration = narrationMatch ? narrationMatch[1].trim() : trimText;
      const visualMatch = trimText.match(/VISUAL:\s*(.*?)$/si);
      const visual = visualMatch ? visualMatch[1].trim() : '';
      scenes.push({ narration, visual });
    });
    return scenes;
  };

  const handleYoutubeUpload = async () => {
    setUploadStatus('uploading');
    setUploadError('');
    setManualPack(null);
    try {
      const response = await axios.post(`${apiBaseUrl}/upload/${jobId}`, {
        title: uploadTitle,
        description: uploadDesc,
        tags: uploadTags
      });
      if (response.data.requires_manual) {
        setUploadStatus('success');
        setManualPack({
          title: response.data.title,
          description: response.data.description,
          tags: response.data.tags,
          message: response.data.message
        });
      } else if (response.data.success) {
        setUploadStatus('success');
        setYoutubeVideoId(response.data.video_id);
      } else {
        setUploadStatus('error');
        setUploadError(response.data.error || 'Failed to upload video.');
      }
    } catch (err) {
      console.error(err);
      setUploadStatus('error');
      setUploadError(err.response?.data?.error || 'Failed to reach backend for YouTube upload.');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.97, y: 15 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="rounded-3xl bg-gray-950/60 p-6 flex flex-col items-center space-y-8 border border-emerald-500/20 shadow-inner"
    >
      <div className="flex items-center space-x-2.5 text-emerald-400 font-bold bg-emerald-500/10 px-5 py-2 rounded-full border border-emerald-500/20 tracking-wider text-sm uppercase">
        <PlayCircle className="w-5 h-5 animate-pulse" />
        <span>Short Successfully Synthesized!</span>
      </div>
      
      <div className="w-full flex flex-col md:flex-row items-center md:items-start justify-center gap-8">
        
        {/* Visual Video Playback */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative group rounded-2xl overflow-hidden shadow-2xl border border-gray-800 bg-black aspect-[9/16] w-[240px] max-w-full">
            <video 
              controls 
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-full object-cover"
              src={videoUrl}
            />
          </div>
          
          <motion.button
            onClick={handleDownload}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            className="inline-flex items-center justify-center rounded-2xl bg-emerald-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 hover:shadow-emerald-500/25 transition-all w-full tracking-wide cursor-pointer border-0"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Video
          </motion.button>
        </div>

        {/* Right Side: Script Storyboard Visualizer */}
        {polishedScript && (
          <div className="flex-1 w-full flex flex-col space-y-4 text-left">
            <div className="bg-gray-950/40 p-5 rounded-2xl border border-gray-850">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Your Original Concept</span>
              <p className="mt-2 text-sm text-gray-400 leading-relaxed max-h-[100px] overflow-y-auto italic">"{originalScript}"</p>
            </div>
            
            <div className="bg-indigo-950/15 p-5 rounded-2xl border border-indigo-500/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-indigo-500/10 text-indigo-400 text-[9px] font-extrabold px-3 py-1.5 rounded-bl-xl uppercase tracking-wider border-l border-b border-indigo-500/10">
                Storyboard Winner
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Polished Script & Sceneprompts</span>
              <div className="mt-3 text-sm text-gray-200 font-medium leading-relaxed max-h-[220px] overflow-y-auto space-y-4 pr-1">
                {getParsedScenes().map((scene, idx) => (
                  <motion.div 
                    key={idx} 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.08 }}
                    className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-850 space-y-2"
                  >
                    <div className="text-[10px] font-extrabold uppercase text-indigo-500 tracking-wider">Scene {idx + 1}</div>
                    <p className="text-gray-100 font-semibold">"{scene.narration}"</p>
                    {scene.visual && (
                      <p className="text-[11px] text-gray-400 bg-gray-900/60 p-2 rounded-lg border border-gray-850 italic font-normal">
                        <span className="font-bold text-gray-500 not-italic">Visual AI:</span> {scene.visual}
                      </p>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* YouTube Upload Card */}
      <div className="w-full pt-8 border-t border-gray-800/80 text-left">
        <div className="bg-gradient-to-br from-gray-950/80 to-gray-900/60 p-6 rounded-2xl border border-indigo-500/10 shadow-inner">
          <h4 className="text-sm font-bold uppercase tracking-wider text-gray-300 flex items-center gap-2">
            <YoutubeIcon className="w-5 h-5 text-red-500 animate-pulse" /> Publish to YouTube
          </h4>
          <p className="text-xs text-gray-500 mt-1">
            Publish this Short directly to your YouTube channel. A Google OAuth verification prompt will open to authorize the upload.
          </p>

          {uploadStatus === 'success' && manualPack ? (
            <motion.div 
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 space-y-6"
            >
              <div className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5 animate-bounce" />
                <div>
                  <h5 className="text-sm font-bold text-indigo-400">AI SEO Publishing Package Generated!</h5>
                  <p className="text-xs text-gray-300 mt-1 leading-relaxed">{manualPack.message}</p>
                </div>
              </div>
              
              <div className="space-y-4 pt-4 border-t border-gray-800/80">
                {/* Clickable Download Video Option */}
                <div className="flex items-center justify-between bg-gray-950 p-4 rounded-xl border border-gray-800">
                  <div>
                    <h6 className="text-xs font-bold text-gray-200">1. Download Your 4K Video File</h6>
                    <p className="text-[10px] text-gray-400 mt-0.5">Save the vertical short directly to your system.</p>
                  </div>
                  <button 
                    onClick={handleDownload}
                    className="px-4 py-2 bg-emerald-650 hover:bg-emerald-600 text-white font-bold text-xs rounded-lg cursor-pointer transition-all border-0 uppercase tracking-wider"
                  >
                    Download File
                  </button>
                </div>

                {/* Optimized SEO Title */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">2. Optimized Title</span>
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(manualPack.title);
                        alert("Title copied to clipboard!");
                      }}
                      className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded cursor-pointer border-0"
                    >
                      Copy Title
                    </button>
                  </div>
                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-850 text-xs text-gray-200 font-mono">
                    {manualPack.title}
                  </div>
                </div>

                {/* Optimized Description (with Timestamps) */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">3. Description with Timeline Chapters</span>
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(manualPack.description);
                        alert("Description copied to clipboard!");
                      }}
                      className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded cursor-pointer border-0"
                    >
                      Copy Description
                    </button>
                  </div>
                  <textarea
                    readOnly
                    rows={6}
                    value={manualPack.description}
                    className="block w-full rounded-xl border-0 bg-gray-950 py-3 px-3.5 text-xs text-gray-200 ring-1 ring-inset ring-gray-800 font-mono focus:ring-0 resize-none"
                  />
                </div>

                {/* Optimized Tags */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">4. Tags / Keywords</span>
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(manualPack.tags);
                        alert("Tags copied to clipboard!");
                      }}
                      className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded cursor-pointer border-0"
                    >
                      Copy Tags
                    </button>
                  </div>
                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-850 text-xs text-gray-200 font-mono">
                    {manualPack.tags}
                  </div>
                </div>
              </div>
              
              <div className="flex justify-center pt-2">
                <button 
                  onClick={() => {
                    setUploadStatus('idle');
                    setManualPack(null);
                  }}
                  className="px-5 py-2.5 bg-gray-850 hover:bg-gray-800 text-gray-300 font-bold text-xs rounded-xl cursor-pointer transition-all border-0 uppercase tracking-wider"
                >
                  Back to Form
                </button>
              </div>
            </motion.div>
          ) : uploadStatus === 'success' ? (
            <motion.div 
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-start space-x-3"
            >
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <h5 className="text-sm font-bold text-emerald-400">Successfully Uploaded!</h5>
                <p className="text-xs text-gray-400 mt-1">Your short is now live (as private/draft) on YouTube.</p>
                <a 
                  href={`https://youtu.be/${youtubeVideoId}`} 
                  target="_blank" 
                  rel="noreferrer"
                  className="inline-flex items-center text-xs font-bold text-indigo-400 hover:text-indigo-300 mt-3 underline cursor-pointer"
                >
                  View Video on YouTube ↗
                </a>
              </div>
            </motion.div>
          ) : (
            <div className="mt-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">YouTube Title</label>
                  <input
                    type="text"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    disabled={uploadStatus === 'uploading'}
                    className="block w-full rounded-xl border-0 bg-gray-950 py-2.5 px-3 text-xs text-white ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500"
                    placeholder="Short Title"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={uploadTags}
                    onChange={(e) => setUploadTags(e.target.value)}
                    disabled={uploadStatus === 'uploading'}
                    className="block w-full rounded-xl border-0 bg-gray-950 py-2.5 px-3 text-xs text-white ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500"
                    placeholder="shorts, ai, marketing"
                  />
                </div>
              </div>
              
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Description</label>
                <textarea
                  value={uploadDesc}
                  onChange={(e) => setUploadDesc(e.target.value)}
                  disabled={uploadStatus === 'uploading'}
                  rows={2}
                  className="block w-full rounded-xl border-0 bg-gray-950 py-2.5 px-3 text-xs text-white ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500"
                  placeholder="Short Description"
                />
              </div>

              {uploadStatus === 'error' && (
                <div className="p-3 rounded-xl bg-red-950/20 border border-red-500/20 flex items-start space-x-2 text-xs text-red-400 leading-normal">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{uploadError}</span>
                </div>
              )}

              <motion.button
                type="button"
                onClick={handleYoutubeUpload}
                disabled={uploadStatus === 'uploading' || !uploadTitle.trim()}
                whileHover={uploadStatus !== 'uploading' ? { scale: 1.02 } : {}}
                whileTap={uploadStatus !== 'uploading' ? { scale: 0.98 } : {}}
                className="inline-flex items-center justify-center rounded-xl bg-red-650 px-5 py-3 text-xs font-bold text-white shadow-lg hover:bg-red-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all w-full sm:w-auto cursor-pointer border border-red-500/20 uppercase tracking-wider"
              >
                {uploadStatus === 'uploading' ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Uploading & Authenticating...
                  </>
                ) : (
                  <>
                    <Share2 className="w-4 h-4 mr-2" />
                    Authorize & Upload to YouTube
                  </>
                )}
              </motion.button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
