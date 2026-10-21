import os
import sys
import io
import uuid
import threading

# Force UTF-8 encoding on standard output to prevent UnicodeEncodeError in Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_file, send_from_directory
# pyrefly: ignore [untyped-import]
from flask_cors import CORS

if sys.platform == "win32":
    import shutil
    # Check if FFmpeg is already available in the system PATH
    if not shutil.which("ffmpeg"):
        ffmpeg_bin_path = os.getenv("FFMPEG_PATH", r"C:\Users\vijay\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin")
        if os.path.exists(ffmpeg_bin_path):
            os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

# Initialize the persistent SQLite database store
from scripts.db_manager import SQLiteJobStore
db = SQLiteJobStore()

from concurrent.futures import ThreadPoolExecutor
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 2))
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)

jobs_lock = threading.Lock()
running_jobs = set()
active_jobs = []

# Create output directory for generated files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def cleanup_old_files():
    """
    Periodically deletes intermediate files from the output directory.
    - Final videos (_final.mp4): kept for 24 hours
    - All other files (audio, captions, images): deleted after 1 hour
    """
    import time
    while True:
        try:
            now = time.time()
            with jobs_lock:
                protected_job_ids = set(running_jobs).union(set(active_jobs))
                
            for filename in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, filename)
                if not os.path.isfile(file_path):
                    continue
                # Shield intermediate files for currently active or running jobs
                if any(filename.startswith(jid) for jid in protected_job_ids):
                    continue
                    
                age = now - os.path.getmtime(file_path)
                is_final_video = filename.endswith("_final.mp4")
                ttl = 86400 if is_final_video else 3600  # 24h for final, 1h for intermediates
                if age > ttl:
                    os.remove(file_path)
                    print(f"[cleanup] Purged {'final video' if is_final_video else 'intermediate'}: {filename}", flush=True)
        except Exception as e:
            print(f"[cleanup] Error during cleanup sweep: {e}", flush=True)
        time.sleep(600)  # Runs every 10 minutes

# Start the background cleanup daemon thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

# Initialize background music downloads on start
try:
    from scripts.music_downloader import init_music_assets
    init_music_assets(os.path.dirname(os.path.abspath(__file__)))
except Exception as e:
    print(f"Error starting music downloader: {e}", flush=True)

def update_job_status(job_id, **kwargs):
    """Updates the job status in the in-memory job store."""
    db.update_job(job_id, **kwargs)

def cleanup_intermediate_assets(job_id, audio_path, srt_path, image_paths):
    """
    Cleans up intermediate cached assets (audio, subtitles) leaving the final video.mp4,
    but PRESERVES the slide images and captions _segments.json to allow subsequent edits and re-compilations!
    """
    try:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            
        norm_audio = audio_path + "._norm.mp3" if audio_path else ""
        if norm_audio and os.path.exists(norm_audio):
            try: os.remove(norm_audio)
            except Exception: pass
            
        if srt_path and os.path.exists(srt_path):
            os.remove(srt_path)
            
        ass_path = srt_path.replace(".srt", ".ass") if srt_path else ""
        if ass_path and os.path.exists(ass_path):
            try: os.remove(ass_path)
            except Exception: pass
            
        print(f"[app] Successfully cleaned up intermediate audio/subtitles for job {job_id} (preserved images & timeline segments).", flush=True)
    except Exception as e:
        print(f"[app] Warning: failed to clean up intermediate assets for job {job_id}: {e}", flush=True)

def generate_video_task(job_id, script, voice_accent="us", caption_style="elegant", music_track="none", art_style="cinematic", music_volume=0.12, video_mode="shorts", video_resolution="1080p", transition_style="dynamic", voice_a="in_female", voice_b="in_male"):
    """
    Background task to generate the shorts video.
    Pipeline:
      Phase 0 — AI Script Polishing (Pollinations.ai text)
      Phase 1 — Text-to-Speech (gTTS / Edge TTS / Dialogue)
      Phase 2 — Captions (Whisper)
      Phase 3 — AI Background Images (Pollinations.ai image)
      Phase 4 — Video Assembly + Subtitle Burn (FFmpeg)
    """
    with jobs_lock:
        running_jobs.add(job_id)
    try:
        # Resolve target resolution early to avoid UnboundLocalError
        stored_resolution = str(video_resolution).lower().strip() if video_resolution else "1080p"
        if "4k" in stored_resolution:
            width, height = 2160, 3840
        else:
            width, height = 1080, 1920

        update_job_status(job_id, state='generating', message='Polishing script with AI...', progress=5)

        # Phase 0: AI Script Polishing (free via Pollinations.ai / Gemini)
        from scripts.script_polisher import polish_script
        from scripts.tts_generator import VOICE_LANGUAGE_MAP
        script_language = VOICE_LANGUAGE_MAP.get(str(voice_accent).lower().strip(), "English")
        polished_script = polish_script(script, mode=video_mode, language=script_language)
        update_job_status(job_id, polished_script=polished_script, progress=15)

        import json
        try:
            scenes = json.loads(polished_script)
        except Exception:
            scenes = []

        update_job_status(job_id, message='Generating audio (TTS)...', progress=20)

        # Audio synthesis: check for dialogue mode
        if video_mode == 'dialogue' or any(s.get('speaker') for s in scenes):
            from scripts.tts_generator import generate_dialogue_speech
            audio_path = generate_dialogue_speech(scenes, voice_a=voice_a, voice_b=voice_b, output_path=os.path.join(OUTPUT_DIR, f"{job_id}_audio.mp3"))
        else:
            from scripts.tts_generator import generate_audio
            audio_path = generate_audio(scenes if scenes else polished_script, os.path.join(OUTPUT_DIR, f"{job_id}_audio.mp3"), tld=voice_accent)
        update_job_status(job_id, progress=40)

        update_job_status(job_id, message='Generating captions (Whisper)...', progress=45)

        # Phase 2: Captions via Whisper with custom style, 3-second hook card, and 2-second outro card
        # Phase 2: Captions via Whisper / Bilingual Synthesizer
        from scripts.caption_generator import generate_captions
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        total_duration = len(audio) / 1000.0
        cta_text = "FOLLOW TO LEARN MORE! 🎓" if video_mode == 'tutorial' else "SUBSCRIBE FOR MORE! 🔔"
        hook_title = ""  # Permanently disabled: no top title banners

        is_hindi = "hi" in str(voice_accent).lower() or "bho" in str(voice_accent).lower()
        ass_path = os.path.join(OUTPUT_DIR, f"{job_id}_captions.ass")

        if is_hindi and scenes:
            from scripts.caption_generator import generate_bilingual_ass
            srt_path = generate_bilingual_ass(
                scenes=scenes,
                total_duration=total_duration,
                output_ass_path=ass_path,
                style=caption_style,
                width=width,
                height=height,
                cta_text=cta_text,
                display_lang="English"
            )
        else:
            srt_path = generate_captions(
                audio_path,
                os.path.join(OUTPUT_DIR, f"{job_id}_captions.srt"),
                style=caption_style,
                hook_title=hook_title,
                total_duration=total_duration,
                cta_text=cta_text,
                script_language=script_language,
                width=width,
                height=height
            )
        update_job_status(job_id, progress=60)

        update_job_status(job_id, message='Generating AI images for each scene...', progress=65)

        def on_video_image_progress(current_count, total_count, status="generating"):
            pct = 65 + int((current_count / max(total_count, 1)) * 15)
            if status == "generating":
                msg = f"Generating AI image {current_count + 1} of {total_count}..."
            else:
                msg = f"Generated AI image {current_count} of {total_count}..."
            update_job_status(job_id, message=msg, progress=pct)

        # Phase 3: Generate AI images per scene
        if video_mode == 'tutorial':
            from scripts.tutorial_image_generator import generate_scene_images as generate_tutorial_images
            image_paths = generate_tutorial_images(scenes if scenes else polished_script, OUTPUT_DIR, job_id=job_id, art_style=art_style, width=width, height=height, progress_callback=on_video_image_progress)
        else:
            from scripts.image_generator import generate_scene_images
            image_paths = generate_scene_images(scenes if scenes else polished_script, OUTPUT_DIR, job_id=job_id, art_style=art_style, width=width, height=height, progress_callback=on_video_image_progress)
        update_job_status(job_id, progress=80)

        update_job_status(job_id, message='Rendering video with AI backgrounds and subtitles...', progress=85)

        # Assemble video — extract tutorial step labels if in tutorial mode
        tutorial_steps = None
        if video_mode == 'tutorial' and scenes:
            tutorial_steps = [s.get('step_title', f'Step {i+1}') for i, s in enumerate(scenes)]
            print(f"[app] generate_video_task Tutorial mode: step labels = {tutorial_steps}", flush=True)

        # Phase 4: Assemble video with zoompan, audio mix, and style mapping
        if video_mode == 'tutorial':
            from scripts.tutorial_video_generator import generate_video as generate_tutorial_video
            final_video_path = generate_tutorial_video(
                audio_path,
                srt_path,
                os.path.join(OUTPUT_DIR, f"{job_id}_final.mp4"),
                image_paths=image_paths,
                music_track=music_track,
                caption_style=caption_style,
                music_volume=music_volume,
                script=scenes if scenes else polished_script,
                tutorial_steps=tutorial_steps,
                resolution=stored_resolution
            )
        else:
            from scripts.video_generator import generate_video
            final_video_path = generate_video(
                audio_path,
                srt_path,
                os.path.join(OUTPUT_DIR, f"{job_id}_final.mp4"),
                image_paths=image_paths,
                music_track=music_track,
                caption_style=caption_style,
                music_volume=music_volume,
                script=scenes if scenes else polished_script,
                resolution=stored_resolution,
                transition_style=transition_style
            )

        update_job_status(
            job_id,
            state='completed',
            message='Generation complete!',
            file=final_video_path,
            polished_script=polished_script,
            progress=100
        )
        cleanup_intermediate_assets(job_id, audio_path, srt_path, image_paths)
    except Exception as e:
        import traceback
        traceback.print_exc()
        update_job_status(job_id, state='error', message=str(e), progress=0)
    finally:
        with jobs_lock:
            running_jobs.discard(job_id)
            if job_id in active_jobs:
                active_jobs.remove(job_id)

@app.route('/output/<path:filename>', methods=['GET'])
def serve_output(filename):
    """Serves compiled videos and generated scene images securely from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/storyboard', methods=['POST'])
def generate_storyboard():
    """
    Lightweight endpoint to polish scripts and generate scene draft images.
    Returns immediately and runs in background to prevent HTTP timeouts.
    """
    import random
    import json
    data = request.json or {}
    script = data.get('script')
    voice_accent = data.get('voice_accent', 'us')
    caption_style = data.get('caption_style', 'elegant')
    music_track = data.get('music_track', 'none')
    art_style = data.get('art_style', 'cinematic')
    video_mode = data.get('video_mode', 'shorts')  # 'shorts', 'dialogue', or 'tutorial'
    video_resolution = data.get('video_resolution', '1080p')
    transition_style = data.get('transition_style', 'dynamic')
    voice_a = data.get('voice_a', voice_accent or 'in_female')
    voice_b = data.get('voice_b', 'in_male')
    
    if not script:
        return jsonify({'error': 'Script is required'}), 400
        
    job_id = str(uuid.uuid4())
    db.create_job(job_id, state='pending', message='Initializing storyboard generation...', art_style=art_style, video_mode=video_mode, video_resolution=video_resolution)
    
    def storyboard_task():
        with jobs_lock:
            running_jobs.add(job_id)
        try:
            if video_mode == "dialogue":
                mode_label = "Dialogue"
            elif video_mode == "tutorial":
                mode_label = "Tutorial"
            else:
                mode_label = "Shorts"
            update_job_status(job_id, state='generating_storyboard', message=f'Polishing script ({mode_label} mode) with AI...', progress=10)
            
            from scripts.script_polisher import polish_script, parse_storyboard
            from scripts.tts_generator import VOICE_LANGUAGE_MAP
            script_language = VOICE_LANGUAGE_MAP.get(str(voice_accent).lower().strip(), "English")
            polished = polish_script(script, mode=video_mode, language=script_language)
            scenes = parse_storyboard(polished)
            
            if not scenes:
                raise RuntimeError("Failed to generate storyboard scenes.")
                
            # Pre-flight storyboard validation
            try:
                from scripts.storyboard_validator import validate_storyboard
                val_rep = validate_storyboard(scenes)
                if not val_rep.get("valid", True):
                    print(f"[app] Storyboard validation warnings: {val_rep.get('warnings', [])}", flush=True)
            except Exception as val_err:
                print(f"[app] Storyboard validation notice: {val_err}", flush=True)
                
            total_scenes = len(scenes)
            # Store the parsed storyboard scenes in the in-memory job store
            update_job_status(job_id, polished_script=json.dumps(scenes, ensure_ascii=False), message=f'Preparing {total_scenes} scene draft images...', progress=30)
            
            # Standard vertical 1080x1920 for snappy, reliable storyboard draft previews
            width, height = 1080, 1920
            
            def on_storyboard_progress(current_count, total_count, status="generating"):
                pct = 30 + int((current_count / max(total_count, 1)) * 65)
                if status == "generating":
                    msg = f"Generating scene image {current_count + 1} of {total_count}..."
                else:
                    msg = f"Generated scene image {current_count} of {total_count} ({pct}% complete)..."
                update_job_status(job_id, message=msg, progress=pct)

            if video_mode == 'tutorial':
                from scripts.tutorial_image_generator import generate_scene_images
            else:
                from scripts.image_generator import generate_scene_images
                
            image_paths = generate_scene_images(
                script=json.dumps(scenes, ensure_ascii=False),
                output_dir=OUTPUT_DIR,
                job_id=job_id,
                art_style=art_style,
                width=width,
                height=height,
                progress_callback=on_storyboard_progress
            )
            
            update_job_status(
                job_id,
                state='storyboard_ready',
                message='Storyboard is ready for review!',
                progress=100
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            update_job_status(job_id, state='error', message=str(e), progress=0)
        finally:
            with jobs_lock:
                running_jobs.discard(job_id)
                if job_id in active_jobs:
                    active_jobs.remove(job_id)
            
    with jobs_lock:
        active_jobs.append(job_id)
    executor.submit(storyboard_task)
    
    return jsonify({'job_id': job_id})

@app.route('/regenerate-image', methods=['POST'])
def regenerate_image():
    """Regenerates a single scene's background image using a new random seed or prompt."""
    import random
    import json
    data = request.json or {}
    job_id = data.get('job_id')
    scene_index = data.get('scene_index')
    prompt = data.get('prompt')
    art_style = data.get('art_style', 'cinematic')
    
    if not job_id or scene_index is None or not prompt:
        return jsonify({'error': 'job_id, scene_index, and prompt are required'}), 400
        
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    try:
        scenes = json.loads(job['polished_script'])
        scene_idx = int(scene_index)
        if scene_idx < 0 or scene_idx >= len(scenes):
            return jsonify({'error': 'Invalid scene_index'}), 400
            
        # Update the visual prompt inside the cached storyboard JSON state
        scenes[scene_idx]['visual'] = prompt
        
        # Support slide metadata edits (title, bullets, code_snippet, narration)
        if 'slide_title' in data:
            scenes[scene_idx]['slide_title'] = data['slide_title'].strip()
        if 'bullets' in data:
            bullets = data['bullets']
            if isinstance(bullets, list):
                scenes[scene_idx]['bullets'] = [b.strip() for b in bullets if b.strip()]
            elif isinstance(bullets, str):
                scenes[scene_idx]['bullets'] = [b.strip() for b in bullets.split("\n") if b.strip()]
        if 'code_snippet' in data:
            scenes[scene_idx]['code_snippet'] = data['code_snippet'].strip()
        if 'narration' in data:
            scenes[scene_idx]['narration'] = data['narration'].strip()
            
        # Support custom typography style overrides (font size, color, family, alignment, bold, italic, underline, line height, background color, slide style preset)
        if 'font_family' in data:
            scenes[scene_idx]['font_family'] = data['font_family'].strip()
        if 'font_size' in data:
            try:
                scenes[scene_idx]['font_size'] = int(data['font_size'])
            except ValueError:
                pass
        if 'font_color' in data:
            scenes[scene_idx]['font_color'] = data['font_color'].strip()
        if 'alignment' in data:
            scenes[scene_idx]['alignment'] = data['alignment'].strip()
        if 'bold' in data:
            scenes[scene_idx]['bold'] = bool(data['bold'])
        if 'italic' in data:
            scenes[scene_idx]['italic'] = bool(data['italic'])
        if 'underline' in data:
            scenes[scene_idx]['underline'] = bool(data['underline'])
        if 'line_height' in data:
            try:
                scenes[scene_idx]['line_height'] = float(data['line_height'])
            except ValueError:
                pass
        if 'bg_color' in data:
            scenes[scene_idx]['bg_color'] = data['bg_color'].strip()
        if 'slide_style' in data:
            scenes[scene_idx]['slide_style'] = data['slide_style'].strip()
            
        # Download new image using a fresh, randomized seed offset and correct resolution
        video_mode = job.get('video_mode', 'shorts')
        if video_mode == 'tutorial':
            from scripts.tutorial_image_generator import download_single_image, STYLE_TEMPLATES, build_story_context
        else:
            from scripts.image_generator import download_single_image, STYLE_TEMPLATES, build_story_context
        style_key = str(art_style).lower().strip()
        style_template = STYLE_TEMPLATES.get(style_key, STYLE_TEMPLATES["cinematic"])
        seed_offset = random.randint(10000, 999999)
        
        # Standard vertical 1080x1920 for fast, reliable regeneration
        width, height = 1080, 1920
        
        # Derive story-coherence context from the full storyboard so the regenerated
        # image stays visually consistent with all other scenes in this job
        story_context = build_story_context(scenes)
        
        new_img_path = download_single_image(
            scene_idx, scenes[scene_idx], style_template, seed_offset, OUTPUT_DIR, job_id, art_style, width=width, height=height, story_context=story_context
        )
        
        # Save updated storyboard back to database
        db.update_job(job_id, polished_script=json.dumps(scenes, ensure_ascii=False))
        
        filename = os.path.basename(new_img_path)
        return jsonify({
            'success': True,
            'image_url': f"/output/{filename}",
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': f'Regeneration error: {str(e)}'}), 500

@app.route('/compile', methods=['POST'])
def compile_video():
    """Trigger the final video composition stages once the storyboard is verified."""
    import json
    data = request.json or {}
    job_id = data.get('job_id')
    voice_accent = data.get('voice_accent', 'us')
    caption_style = data.get('caption_style', 'elegant')
    music_track = data.get('music_track', 'none')
    video_mode = data.get('video_mode', 'shorts')  # forwarded from frontend
    video_resolution = data.get('video_resolution', '1080p')
    
    try:
        music_volume = float(data.get('music_volume', 0.12))
    except ValueError:
        music_volume = 0.12
        
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400
        
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    db.update_job(job_id, state='pending_compile', message='Initializing final video render...', progress=5, video_resolution=video_resolution)
    
    def compile_task():
        with jobs_lock:
            running_jobs.add(job_id)
        try:
            update_job_status(job_id, state='compiling_video', message='Generating audio (TTS)...', progress=10)
            
            # Fetch polished storyboard JSON
            scenes = json.loads(job['polished_script'])
            
            stored_mode = job_metadata.get('video_mode', video_mode) if job_metadata else video_mode
            is_dialogue = (stored_mode == 'dialogue') or any(s.get('speaker') for s in scenes)
            if is_dialogue:
                from scripts.tts_generator import generate_dialogue_speech
                v_a = data.get('voice_a', voice_accent or 'in_female')
                v_b = data.get('voice_b', 'in_male')
                audio_path = generate_dialogue_speech(scenes, voice_a=v_a, voice_b=v_b, output_path=os.path.join(OUTPUT_DIR, f"{job_id}_audio.mp3"))
            else:
                from scripts.tts_generator import generate_audio
                audio_path = generate_audio(scenes, os.path.join(OUTPUT_DIR, f"{job_id}_audio.mp3"), tld=voice_accent)
            update_job_status(job_id, progress=35)
            
            update_job_status(job_id, message='Generating captions (Whisper)...', progress=40)
            
            # Captions generation via Whisper / Bilingual Synthesizer
            from scripts.caption_generator import generate_captions
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            total_duration = len(audio) / 1000.0
            cta_text = "FOLLOW TO LEARN MORE! 🎓" if video_mode == 'tutorial' else "SUBSCRIBE FOR MORE! 🔔"
            hook_title = ""  # Permanently disabled: no top title banners

            from scripts.tts_generator import VOICE_LANGUAGE_MAP
            voice_key = str(voice_accent or 'in_female').lower().strip()
            script_lang = VOICE_LANGUAGE_MAP.get(voice_key, "English")
            is_hindi = "hi" in voice_key or "bho" in voice_key
            ass_path = os.path.join(OUTPUT_DIR, f"{job_id}_captions.ass")

            stored_resolution = job_metadata.get('video_resolution', video_resolution) if job_metadata else video_resolution
            w_comp, h_comp = (2160, 3840) if str(stored_resolution).lower().strip() == "4k" else (1080, 1920)

            if is_hindi and scenes:
                from scripts.caption_generator import generate_bilingual_ass
                srt_path = generate_bilingual_ass(
                    scenes=scenes,
                    total_duration=total_duration,
                    output_ass_path=ass_path,
                    style=caption_style,
                    width=w_comp,
                    height=h_comp,
                    cta_text=cta_text,
                    display_lang=data.get('caption_lang', 'English')
                )
            else:
                srt_path = generate_captions(
                    audio_path,
                    os.path.join(OUTPUT_DIR, f"{job_id}_captions.srt"),
                    style=caption_style,
                    hook_title=hook_title,
                    total_duration=total_duration,
                    cta_text=cta_text,
                    script_language=script_lang,
                    width=w_comp,
                    height=h_comp
                )
            update_job_status(job_id, progress=60)
            
            update_job_status(job_id, message='Stitching and rendering final video layers...', progress=70)
            
            # Gather scene images with proactive local slide recovery
            image_paths = []
            stored_mode = job_metadata.get('video_mode', video_mode) if job_metadata else video_mode
            for i in range(len(scenes)):
                img_path = os.path.join(OUTPUT_DIR, f"{job_id}_scene_{i:02d}.jpg")
                if not os.path.exists(img_path):
                    if stored_mode == 'tutorial':
                        from scripts.slide_renderer import render_slide
                        print(f"[app] Proactively auto-recovering missing tutorial slide frame {i+1}...", flush=True)
                        scenes[i]["art_style"] = job_metadata.get('art_style', 'cinematic') if job_metadata else 'cinematic'
                        render_slide(scenes[i], img_path, width=2160, height=3840)
                    else:
                        raise RuntimeError(f"Scene image {i+1} is missing. Please regenerate.")
                image_paths.append(img_path)
                
            # Respect user's selected resolution (4K Ultra HD vs 1080p Full HD)
            stored_resolution = job_metadata.get('video_resolution', video_resolution) if job_metadata else video_resolution
            if not stored_resolution:
                stored_resolution = '1080p'
            
            tutorial_steps = None
            stored_mode = job_metadata.get('video_mode', video_mode) if job_metadata else video_mode
            if stored_mode == 'tutorial':
                tutorial_steps = [s.get('step_title', f'Step {i+1}') for i, s in enumerate(scenes)]
                print(f"[app] Tutorial mode: step labels = {tutorial_steps}", flush=True)

            if stored_mode == 'tutorial':
                from scripts.tutorial_video_generator import generate_video as generate_tutorial_video
                final_video_path = generate_tutorial_video(
                    audio_path,
                    srt_path,
                    os.path.join(OUTPUT_DIR, f"{job_id}_final.mp4"),
                    image_paths=image_paths,
                    music_track=music_track,
                    caption_style=caption_style,
                    music_volume=music_volume,
                    script=scenes,
                    tutorial_steps=tutorial_steps,
                    resolution=stored_resolution
                )
            else:
                from scripts.video_generator import generate_video
                trans_style = data.get('transition_style', 'dynamic')
                final_video_path = generate_video(
                    audio_path,
                    srt_path,
                    os.path.join(OUTPUT_DIR, f"{job_id}_final.mp4"),
                    image_paths=image_paths,
                    music_track=music_track,
                    caption_style=caption_style,
                    music_volume=music_volume,
                    script=scenes,
                    resolution=stored_resolution,
                    transition_style=trans_style
                )
            
            update_job_status(
                job_id,
                state='completed',
                message='Compilation complete!',
                file=final_video_path,
                progress=100
            )
            cleanup_intermediate_assets(job_id, audio_path, srt_path, image_paths)
        except Exception as e:
            update_job_status(job_id, state='error', message=str(e), progress=0)
        finally:
            with jobs_lock:
                running_jobs.discard(job_id)
                if job_id in active_jobs:
                    active_jobs.remove(job_id)
            
    with jobs_lock:
        active_jobs.append(job_id)
    executor.submit(compile_task)
    
    return jsonify({'success': True})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    script = data.get('script')
    voice_accent = data.get('voice_accent', 'us')
    caption_style = data.get('caption_style', 'elegant')
    music_track = data.get('music_track', 'none')
    art_style = data.get('art_style', 'cinematic')
    video_mode = data.get('video_mode', 'shorts')
    video_resolution = data.get('video_resolution', '1080p')
    transition_style = data.get('transition_style', 'dynamic')
    voice_a = data.get('voice_a', voice_accent or 'in_female')
    voice_b = data.get('voice_b', 'in_male')
    
    try:
        music_volume = float(data.get('music_volume', 0.12))
    except ValueError:
        music_volume = 0.12
    
    if not script:
        return jsonify({'error': 'Script is required'}), 400
        
    job_id = str(uuid.uuid4())
    db.create_job(job_id, state='pending', message='Job submitted', art_style=art_style, video_mode=video_mode, video_resolution=video_resolution)
    
    with jobs_lock:
        active_jobs.append(job_id)
    executor.submit(
        generate_video_task, 
        job_id, script,
        voice_accent=voice_accent,
        caption_style=caption_style,
        music_track=music_track,
        art_style=art_style,
        music_volume=music_volume,
        video_mode=video_mode,
        video_resolution=video_resolution,
        transition_style=transition_style,
        voice_a=voice_a,
        voice_b=voice_b
    )
    
    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    state = job['state']
    message = job['message']
    progress = job.get('progress', 0)
    
    with jobs_lock:
        is_running = job_id in running_jobs
        is_active = job_id in active_jobs
        
    # If the job is active but not running, report it as queued!
    if state in ('pending', 'pending_compile') and not is_running:
        state = 'queued'
        try:
            with jobs_lock:
                running_count = len(running_jobs)
                if job_id in active_jobs:
                    queue_idx = active_jobs.index(job_id)
                    position = max(1, queue_idx - running_count + 1)
                    message = f"Queued at position {position}. Waiting for FFmpeg and AI workers..."
                else:
                    message = "Waiting in queue..."
        except Exception:
            message = "Waiting in queue..."
            
    response_data = {
        'state': state,
        'message': message,
        'progress': progress
    }
    if job.get('polished_script'):
        response_data['polished_script'] = job['polished_script']
        
    return jsonify(response_data)

@app.route('/download/<job_id>', methods=['GET'])
def download(job_id):
    # Strip .mp4 extension if present in the matched job_id
    clean_job_id = job_id
    if clean_job_id.endswith('.mp4'):
        clean_job_id = clean_job_id[:-4]
        
    job = db.get_job(clean_job_id)
    if not job or job.get('state') != 'completed':
        return jsonify({'error': 'Job not completed or not found'}), 404
        
    file_path = job.get('file')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
        
    response = send_file(file_path, as_attachment=True)
    response.headers["Content-Disposition"] = f'attachment; filename="shorts_{clean_job_id}.mp4"'
    return response

def query_seo_metadata(job_id, job, timeline_str):
    """
    Queries Gemini or the keyless Pollinations LLM to craft search-engine-optimized YouTube metadata.
    """
    import json
    from scripts.llm_client import query_llm, clean_json_string
    prompt = (
        f"You are a professional YouTube video optimizer and SEO expert.\n"
        f"Generate an highly engaging, click-worthy Title, an optimized Description, and search-relevant tags for an educational tutorial video.\n"
        f"Script topic: {job.get('script_topic', 'AI Tutorial')}\n\n"
        f"The description must include the following precise timeline chapters to make the video interactive and highly navigable:\n"
        f"{timeline_str}\n\n"
        f"Format your response as a valid JSON object with the following keys:\n"
        f"  \"title\": \"[SEO title under 60 characters]\",\n"
        f"  \"description\": \"[Engaging description paragraph summarizing the value of the video, followed by the timeline chapters above, and concluding with call-to-actions]\",\n"
        f"  \"tags\": \"[10-15 search tags separated by commas]\"\n"
        f"Return ONLY the raw JSON string with no markdown formatting."
    )
    
    fallback_data = {
        "title": f"Step-by-Step Tutorial on {job.get('script_topic', 'Topic')}",
        "description": f"Learn all about {job.get('script_topic', 'this topic')} in our detailed step-by-step educational walkthrough!\n\n{timeline_str}",
        "tags": f"education, howto, learn, {job.get('script_topic', 'topic')}"
    }

    try:
        print(f"[app] Generating optimized SEO metadata using central LLM client...", flush=True)
        response_text = query_llm(prompt, response_format_json=True, temperature=0.5, max_tokens=600)
        if response_text:
            cleaned = clean_json_string(response_text)
            parsed = json.loads(cleaned)
            if parsed.get("title") and parsed.get("description"):
                return parsed
    except Exception as e:
        print(f"[app] query_seo_metadata central LLM error: {e}", flush=True)
        
    return fallback_data

@app.route('/upload/<job_id>', methods=['POST'])
def upload(job_id):
    import json
    job = db.get_job(job_id)
    if not job or job.get('state') != 'completed':
        return jsonify({'error': 'Job not completed or not found'}), 404
        
    file_path = job.get('file')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # 1. Parse _segments.json to build highly accurate clickable timeline chapters
    timeline_str = "00:00 - Introduction\n"
    segments_path = os.path.join(OUTPUT_DIR, f"{job_id}_captions_segments.json")
    if os.path.exists(segments_path):
        try:
            with open(segments_path, "r", encoding="utf-8") as f:
                segs = json.load(f)
            scenes = json.loads(job.get('polished_script', '[]'))
            
            # Map scene list starting times
            for idx, scene in enumerate(scenes):
                if idx == 0:
                    continue
                start_sec = segs[idx]["start"] if idx < len(segs) else (idx * 5.0)
                mins = int(start_sec // 60)
                secs = int(start_sec % 60)
                time_lbl = f"{mins:02d}:{secs:02d}"
                title = scene.get("step_title", scene.get("slide_title", f"Step {idx}")).strip(" 🔑⚙️🛠️📌•")
                if not title:
                    title = f"Section {idx}"
                timeline_str += f"{time_lbl} - {title}\n"
        except Exception as e:
            print(f"[app] Timeline chapters parse failed: {e}", flush=True)

    client_secrets_file = os.path.join(os.path.dirname(__file__), "client_secret.json")
    if not os.path.exists(client_secrets_file):
        # Package and return optimized AI SEO metadata for manual copy-paste
        try:
            seo_data = query_seo_metadata(job_id, job, timeline_str)
            return jsonify({
                'requires_manual': True,
                'title': seo_data.get('title', f"How to understand {job.get('script_topic', 'Topic')}")[:100],
                'description': seo_data.get('description', f"A step-by-step educational walkthrough.\n\n{timeline_str}"),
                'tags': seo_data.get('tags', 'tutorial, education, learn'),
                'video_url': f"/download/{job_id}",
                'message': 'YouTube Client Secrets are not configured. We have automatically generated a fully optimized AI Publishing Package. You can download the video and copy-paste these fields directly into YouTube Studio!'
            })
        except Exception as e:
            print(f"[app] SEO Pack generation fallback error: {e}", flush=True)
            return jsonify({
                'requires_manual': True,
                'title': f"Step-by-Step {job.get('script_topic', 'Tutorial')}",
                'description': f"A comprehensive tutorial walkthrough.\n\n{timeline_str}",
                'tags': 'education, learning, how-to',
                'video_url': f"/download/{job_id}",
                'message': 'YouTube Client Secrets are not configured. Here is your timeline-grounded publishing package for manual upload.'
            })

    data = request.json or {}
    title = data.get('title', 'My AI Short')
    description = data.get('description', f"Auto-generated using Shorts Studio AI\n\n{timeline_str}")
    tags_raw = data.get('tags', 'shorts, ai, generated')
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

    try:
        from scripts.youtube_uploader import upload_video
        result_holder = {"video_id": None, "error": None}

        def _do_upload():
            try:
                result_holder["video_id"] = upload_video(file_path, title=title, description=description, tags=tags)
            except Exception as exc:
                result_holder["error"] = str(exc)

        upload_thread = threading.Thread(target=_do_upload)
        upload_thread.daemon = True
        upload_thread.start()
        upload_thread.join(timeout=180)  # Wait up to 3 minutes

        if result_holder["error"]:
            return jsonify({'error': f'YouTube upload error: {result_holder["error"]}'}), 500
        if result_holder["video_id"]:
            return jsonify({'success': True, 'video_id': result_holder["video_id"]})
        return jsonify({'error': 'Failed to upload video to YouTube.'}), 500
    except Exception as e:
        return jsonify({'error': f'YouTube upload error: {str(e)}'}), 500

@app.route('/upload-scene-image', methods=['POST'])
def upload_scene_image():
    """
    Accepts an uploaded image file for a given job_id and scene_index,
    transcodes it via Pillow into a standard high-quality RGB JPEG,
    saves it directly as the target scene visual frame, and injects a cache buster.
    """
    import time
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    
    file = request.files['image']
    job_id = request.form.get('job_id')
    scene_index = request.form.get('scene_index')
    
    if not job_id or scene_index is None:
        return jsonify({'error': 'Missing required fields job_id or scene_index'}), 400
        
    try:
        scene_idx = int(scene_index)
    except ValueError:
        return jsonify({'error': 'Invalid scene_index'}), 400
        
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return jsonify({'error': 'Invalid image format. Supported formats: PNG, JPG, JPEG, WEBP'}), 400
        
    target_filename = f"{job_id}_scene_{scene_idx:02d}.jpg"
    target_path = os.path.join(OUTPUT_DIR, target_filename)
    
    try:
        # Transcode via Pillow to standard RGB JPEG to keep FFMpeg processing happy
        try:
            from PIL import Image
            img = Image.open(file.stream)
            img = img.convert('RGB')
            img.save(target_path, 'JPEG', quality=95)
        except Exception as e:
            print(f"[app] Pillow transcode failed, falling back to direct save: {e}", flush=True)
            file.seek(0)
            file.save(target_path)
            
        # Update polished_script in database to inject a cache buster for the React rendering cycle
        cache_buster = int(time.time())
        if job.get('polished_script'):
            try:
                import json
                scenes = json.loads(job['polished_script'])
                if 0 <= scene_idx < len(scenes):
                    scenes[scene_idx]['image_url'] = f"/output/{target_filename}?t={cache_buster}"
                    db.update_job(job_id, polished_script=json.dumps(scenes, ensure_ascii=False))
            except Exception as e:
                print(f"[app] Error updating uploaded scene reference in DB: {e}", flush=True)
                
        return jsonify({
            'success': True, 
            'image_url': f'/output/{target_filename}?t={cache_buster}'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to save custom image: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Structured system telemetry and status health endpoint.
    Reports queue depth, disk usage, database health, network API connectivity,
    and platform architecture.
    """
    import shutil
    import platform
    import requests
    
    # 1. Disk usage of output directory
    total_bytes, used_bytes, free_bytes = shutil.disk_usage(OUTPUT_DIR)
    disk_usage = {
        "total_gb": round(total_bytes / (1024**3), 2),
        "used_gb": round(used_bytes / (1024**3), 2),
        "free_gb": round(free_bytes / (1024**3), 2),
        "percent_used": round((used_bytes / total_bytes) * 100, 1)
    }
    
    # Calculate output folder cache size
    cache_size_bytes = 0
    try:
        for f in os.listdir(OUTPUT_DIR):
            fpath = os.path.join(OUTPUT_DIR, f)
            if os.path.isfile(fpath):
                cache_size_bytes += os.path.getsize(fpath)
    except Exception:
        pass
    disk_usage["cache_size_mb"] = round(cache_size_bytes / (1024**2), 2)

    # 2. Concurrency executor statistics
    with jobs_lock:
        running = list(running_jobs)
        active = list(active_jobs)
        queued = [jid for jid in active if jid not in running]
        
    concurrency = {
        "max_workers": MAX_CONCURRENT_JOBS,
        "running_count": len(running),
        "running_job_ids": running,
        "queue_depth": len(queued),
        "queued_job_ids": queued
    }

    # 3. Database connectivity
    db_healthy = False
    db_mode = "SQLite"
    try:
        # Simple test query
        db.list_jobs()
        db_healthy = True
        if getattr(db, "fallback", None) is not None:
            db_mode = "InMemory Fallback"
    except Exception:
        pass

    # 4. External network API connectivity check
    pollinations_txt_reachable = False
    pollinations_img_reachable = False
    try:
        # Check text generation endpoint
        res = requests.get("https://text.pollinations.ai/", timeout=4)
        pollinations_txt_reachable = (res.status_code == 200)
    except Exception:
        pass
        
    try:
        # Check image generation endpoint
        res = requests.get("https://image.pollinations.ai/", timeout=4)
        pollinations_img_reachable = (res.status_code == 200)
    except Exception:
        pass

    # 5. OS and runtime platform telemetry
    platform_telemetry = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "cpu_arch": platform.machine()
    }
    
    # Check if psutil is available for precise RAM telemetry
    memory_pct = None
    try:
        import psutil
        memory_pct = psutil.virtual_memory().percent
    except Exception:
        pass
    platform_telemetry["ram_percent_used"] = memory_pct

    # Determine absolute system status
    status = "healthy"
    if not db_healthy:
        status = "degraded"
    elif not pollinations_txt_reachable:
        status = "network_issue"

    return jsonify({
        "status": status,
        "database": {
            "healthy": db_healthy,
            "mode": db_mode
        },
        "disk_usage": disk_usage,
        "concurrency": concurrency,
        "apis": {
            "pollinations_text": pollinations_txt_reachable,
            "pollinations_image": pollinations_img_reachable,
            "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
        },
        "platform": platform_telemetry
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

