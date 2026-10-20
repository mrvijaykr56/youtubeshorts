import os
import re
import sys
import io
import time
import requests

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def split_into_scenes(script: str) -> list[str]:
    """
    Splits a script into individual sentences to use as scene prompts.
    Each sentence becomes one AI-generated background image.
    """
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', script.strip())
    # Filter out very short fragments
    scenes = [s.strip() for s in sentences if len(s.strip()) > 10]
    # If no proper sentences found, split into ~50-char chunks
    if not scenes:
        words = script.split()
        chunk, scenes = [], []
        for word in words:
            chunk.append(word)
            if len(' '.join(chunk)) >= 50:
                scenes.append(' '.join(chunk))
                chunk = []
        if chunk:
            scenes.append(' '.join(chunk))
    return scenes


STYLE_TEMPLATES = {
    "cinematic": "Cinematic still, photorealistic, 8k resolution, highly detailed, 9:16 vertical portrait aspect ratio, dramatic rim lighting, moody atmosphere, shot on anamorphic lens, shallow depth of field, color graded, masterpiece: {prompt}",
    "cyberpunk": "Cyberpunk aesthetic, neon-infused street scene, high-tech low-life, rich glowing purple and cyan tones, cinematic vertical 9:16 portrait orientation, detailed rainy reflection, octane render, volumetric fog: {prompt}",
    "pixar": "Cute 3D digital clay illustration, Pixar style, charming character, soft warm lighting, claymation, octane render, tactile textures, vibrant pastel color palette, vertical 9:16 portrait orientation: {prompt}",
    "3d_art": "Cute 3D digital clay illustration, Pixar style, charming character, soft warm lighting, claymation, octane render, tactile textures, vibrant pastel color palette, vertical 9:16 portrait orientation: {prompt}",
    "anime": "Breathtaking anime style, rich colors, beautiful hand-drawn background, cinematic light rays, highly aesthetic, Makoto Shinkai and CoMix Wave Films vibe, vertical 9:16 portrait orientation: {prompt}",
    "painting": "Masterpiece oil painting on rough canvas, rich impasto brushstrokes, dramatic Chiaroscuro lighting, deep classical tones, Rembrandt style, gallery-grade quality, vertical 9:16 portrait orientation: {prompt}",
    "oil_painting": "Masterpiece oil painting on rough canvas, rich impasto brushstrokes, dramatic Chiaroscuro lighting, deep classical tones, Rembrandt style, gallery-grade quality, vertical 9:16 portrait orientation: {prompt}"
}


def build_story_context(scenes: list) -> str:
    """
    Derives a single-sentence visual coherence brief from the full storyboard.
    This string is prepended to EVERY scene's image prompt so that all images
    share the same visual world: setting, color palette, lighting mood, and
    protagonist/environment consistency.

    Uses the LLM client for a rich result, with a deterministic fallback
    built from the first scene's visual prompt if the LLM call fails.
    """
    if not scenes:
        return ""

    # Build a compact summary of all scene visuals for the LLM to analyze
    scene_summaries = []
    for i, s in enumerate(scenes):
        vis = s.get("visual", s.get("narration", ""))[:120]
        narr = s.get("narration", "")[:80]
        scene_summaries.append(f"Scene {i+1}: {narr} | Visual: {vis}")
    full_summary = "\n".join(scene_summaries)

    prompt = (
        "You are a film production designer. Analyze the following storyboard scenes and "
        "produce ONE concise sentence (max 40 words) describing the shared visual world: "
        "include the dominant setting/environment, color palette, lighting mood, and visual style. "
        "This sentence will be prepended to AI image prompts to ensure all scenes look visually consistent.\n"
        "Output ONLY the sentence, nothing else.\n\n"
        f"Storyboard:\n{full_summary}"
    )

    try:
        from scripts.llm_client import query_llm
        result = query_llm(prompt, temperature=0.3, max_tokens=80)
        if result and len(result.strip()) > 10:
            ctx = result.strip().strip('"\'')
            print(f"[image_generator] [STORY CONTEXT] {ctx}", flush=True)
            return ctx
    except Exception as e:
        print(f"[image_generator] build_story_context LLM failed ({e}), using fallback.", flush=True)

    # Deterministic fallback: derive context from first scene's visual
    fallback_visual = scenes[0].get("visual", scenes[0].get("narration", ""))[:100]
    fallback_ctx = f"Consistent visual world: {fallback_visual}"
    print(f"[image_generator] [STORY CONTEXT FALLBACK] {fallback_ctx}", flush=True)
    return fallback_ctx


def enrich_visual_prompt(scene_visual: str, art_style: str, scene_index: int = 0) -> str:
    """
    Enriches a simple visual prompt with atmospheric, hyper-detailed rendering modifiers
    tailored to the chosen art style. Only adds terms NOT already in STYLE_TEMPLATES
    to avoid duplicate keyword confusion in the AI model.
    """
    prompt = scene_visual.strip()
    if prompt.endswith("."):
        prompt = prompt[:-1]
        
    modifiers = {
        # Cinematic: template already has 8k, photorealistic, rim lighting — add unique mood depth
        "cinematic": ", volumetric god rays, fine film grain, hyper-detailed textures, cinematic color grade",
        "cyberpunk": ", gorgeous glowing neon accents, highly detailed futuristic architecture, rain-soaked asphalt reflections, cyberpunk grit",
        "pixar": ", warm claymation lighting, highly detailed soft textures, adorable cartoon features, high-fidelity digital art, colorful and whimsical",
        "anime": ", beautiful makoto shinkai aesthetic, gorgeous detailed background art, cinematic atmospheric light rays, soft anime colors, high aesthetic",
        "painting": ", thick heavy impasto brushstrokes, realistic rough canvas texture, rich oil colors, chiaroscuro shading, fine art masterpiece"
    }
    
    style_key = str(art_style).lower().strip()
    match_key = "cinematic"
    if "cyber" in style_key:
        match_key = "cyberpunk"
    elif "pixar" in style_key or "3d" in style_key:
        match_key = "pixar"
    elif "anime" in style_key:
        match_key = "anime"
    elif "paint" in style_key or "oil" in style_key:
        match_key = "painting"
    # Rotationally apply cinematic camera angles (Close-Up, Medium-Shot, Wide Epic Landscape)
    camera_perspectives = [
        ", dramatic close-up shot, extreme detail, cinematic studio lighting",
        ", cinematic medium-shot, photorealistic details, 85mm portrait lens, shallow depth of field",
        ", sweeping wide-angle cinematic shot, majestic scenery, dynamic volumetric lighting, golden hour octane render"
    ]
    camera_modifier = camera_perspectives[scene_index % len(camera_perspectives)]
        
    return prompt + modifiers.get(match_key, "") + camera_modifier


_last_pollinations_request_time = 0.0

def wait_for_pollinations_cooldown(min_cooldown: float = 46.0):
    """
    Ensures at least min_cooldown seconds have elapsed since the last network request
    to Pollinations.ai, strictly complying with their free IP rate limit (1 image / 45s).
    Automatically bypassed if POLLINATIONS_API_KEY is configured.
    """
    global _last_pollinations_request_time
    api_key = os.getenv("POLLINATIONS_API_KEY", "").strip()
    if api_key:
        return
    now = time.time()
    elapsed = now - _last_pollinations_request_time
    if elapsed < min_cooldown and _last_pollinations_request_time > 0:
        sleep_needed = min_cooldown - elapsed
        print(f"[image_generator] [COOLDOWN] Free IP limit (1 img/45s): waiting {sleep_needed:.1f}s before next image request...", flush=True)
        time.sleep(sleep_needed)

def mark_pollinations_request():
    global _last_pollinations_request_time
    _last_pollinations_request_time = time.time()


def download_single_image(i, scene, style_template, seed_offset, output_dir, job_id, art_style, width: int = 1080, height: int = 1920, story_context: str = ""):
    scene_visual = scene["visual"]
    
    # Enrich the raw visual prompt dynamically with style presets and rotational camera perspectives
    enriched_visual = enrich_visual_prompt(scene_visual, art_style, scene_index=i)

    # Prepend the global story-coherence context so the AI generates this scene
    # within the same visual world as every other scene in the story.
    if story_context:
        coherent_visual = f"{story_context}. {enriched_visual}"
    else:
        coherent_visual = enriched_visual
    
    # Build enriched prompt using selected art style safely (replace is immune to braces in prompt)
    prompt = style_template.replace("{prompt}", coherent_visual)
    # Truncate prompt safely to 600 chars to avoid URL length overflow
    if len(prompt) > 600:
        prompt = prompt[:597] + "..."
    from urllib.parse import quote as url_quote
    encoded_prompt = url_quote(prompt, safe='')
    
    # Use randomized seed offset for unique generation
    seed = (seed_offset + i) % 100000
    
    # Check visual cache first — hash is prompt-only (seed excluded) so the same
    # prompt reuses the cached image across different jobs, saving generation time.
    # Cache key includes width and height to prevent 1080p vs 4K cache collisions!
    import hashlib
    import shutil
    prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    cache_dir = os.path.join(output_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cached_path = os.path.join(cache_dir, f"{prompt_hash}_{width}x{height}.jpg")
    output_path = os.path.join(output_dir, f"{job_id}_scene_{i:02d}.jpg")
    
    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 1000:
        print(f"[image_generator] [CACHE HIT] Reusing cached visual for scene {i+1} ({width}x{height}) at {cached_path}", flush=True)
        shutil.copy(cached_path, output_path)
        return output_path

    # LRU cache eviction: keep only the 150 most-recently-modified cache files
    try:
        cache_files = sorted(
            [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if f.endswith(".jpg")],
            key=os.path.getmtime
        )
        if len(cache_files) > 150:
            for old_file in cache_files[:len(cache_files) - 150]:
                os.remove(old_file)
    except Exception:
        pass

    # ─── Pollinations.ai (Free Tier Optimization) ────────────────────────────
    # Pollinations free tier reliably supports dimensions up to 1080x1920.
    # Base 'flux' is the official free tier model; rich style prompt modifiers
    # guide Flux to generate Pixar, Cinematic, Anime, and Painting aesthetics.
    req_width = min(width, 1080)
    req_height = min(height, 1920)

    # Use base flux for free tier stability
    current_model = "flux"

    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={req_width}&height={req_height}&nologo=true&seed={seed}&model={current_model}&enhance=true&private=true"
    )

    headers = {}
    api_key = os.getenv("POLLINATIONS_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    max_attempts = 3
    for attempt in range(max_attempts):
        wait_for_pollinations_cooldown(46.0)
        try:
            print(f"[image_generator] Generating scene {i+1}: '{scene_visual[:35]}...' model={current_model} dim={req_width}x{req_height} (attempt {attempt+1}/{max_attempts})", flush=True)
            mark_pollinations_request()
            response = requests.get(url, headers=headers, timeout=40)
            
            if response.status_code == 200 and len(response.content) > 1000:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                try:
                    shutil.copy(output_path, cached_path)
                except Exception as e:
                    print(f"[image_generator] Warning: cache write failed: {e}", flush=True)
                print(f"[image_generator] [OK] Scene {i+1} saved to {output_path}", flush=True)
                return output_path
            elif response.status_code in (402, 429):
                # Pollinations rate limit / cooldown response
                retry_header = response.headers.get("Retry-After")
                try:
                    retry_sec = float(retry_header) if retry_header else 46.0
                except (ValueError, TypeError):
                    retry_sec = 46.0
                wait_sec = max(retry_sec, 46.0)
                print(f"[image_generator] Free limit reached (Status {response.status_code}). Waiting {wait_sec:.1f}s cooldown before retrying...", flush=True)
                time.sleep(wait_sec)
            else:
                wait_sec = 2.0 * (attempt + 1)
                print(f"[image_generator] Bad response scene {i+1}: status={response.status_code} (attempt {attempt+1}), retrying in {wait_sec}s...", flush=True)
                time.sleep(wait_sec)
        except requests.exceptions.RequestException as e:
            wait_sec = 3.0 * (attempt + 1)
            print(f"[image_generator] Request error scene {i+1}: {e} (attempt {attempt+1}), retrying in {wait_sec}s...", flush=True)
            time.sleep(wait_sec)

    # All retries failed — use high-quality local fallback gradient so the render proceeds uninterrupted
    print(f"[image_generator] [FALLBACK] Using local styled fallback image for scene {i+1}", flush=True)
    _create_fallback_image(output_path, width=width, height=height)
    return output_path


def generate_scene_images(script: str, output_dir: str, job_id: str = "default", art_style: str = "cinematic", width: int = 1080, height: int = 1920, progress_callback = None) -> list[str]:
    """
    Generates AI images for each storyboard scene sequentially with smart 45s IP pacing.
    Returns a list of local file paths to the downloaded images, ordered perfectly.

    Visual Coherence: A single story-context brief is derived from the full storyboard
    and injected into every scene's image prompt, ensuring all images share the same
    visual world (setting, color palette, lighting mood, protagonist/environment).
    """
    from scripts.script_polisher import parse_storyboard
    scenes = parse_storyboard(script)
    
    style_key = str(art_style).lower().strip()
    style_template = STYLE_TEMPLATES.get(style_key, STYLE_TEMPLATES["cinematic"])

    import random
    if job_id and job_id != "default":
        seed_offset = abs(hash(job_id)) % 50000
    else:
        seed_offset = random.randint(0, 50000)

    # Build a single story-coherence context from the full storyboard ONCE.
    # This is passed to every worker so all images share the same visual universe.
    story_context = build_story_context(scenes)

    print(f"[image_generator] Generating {len(scenes)} scene images ({width}x{height}) with smart rate-limit pacing...", flush=True)

    image_paths = [None] * len(scenes)

    def worker_task(idx, scene):
        try:
            path = download_single_image(
                idx, scene, style_template, seed_offset,
                output_dir, job_id, art_style,
                width=width, height=height,
                story_context=story_context
            )
            image_paths[idx] = path
        except Exception as exc:
            print(f"[image_generator] Error on Scene {idx+1}: {exc}", flush=True)
            fallback_path = os.path.join(output_dir, f"{job_id}_scene_{idx:02d}.jpg")
            _create_fallback_image(fallback_path, width=width, height=height)
            image_paths[idx] = fallback_path

    # Sequentially process scenes with intelligent 45s cooldown (cached scenes skip cooldown)
    for idx, scene in enumerate(scenes):
        if progress_callback:
            try:
                progress_callback(idx, len(scenes), status="generating")
            except Exception as e:
                print(f"[image_generator] Progress callback error: {e}", flush=True)
        worker_task(idx, scene)
        if progress_callback:
            try:
                progress_callback(idx + 1, len(scenes), status="completed_scene")
            except Exception as e:
                print(f"[image_generator] Progress callback error: {e}", flush=True)

    return image_paths



def _create_fallback_image(output_path: str, width: int = 1080, height: int = 1920):
    """Creates a premium high-aesthetic dark neon gradient fallback image using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFilter
        # Create a deep elegant navy-slate background
        img = Image.new("RGB", (width, height), color=(15, 16, 28))
        draw = ImageDraw.Draw(img)
        
        # Draw a beautiful, smooth vertical linear gradient
        for y in range(height):
            # Slow transition from deep slate-blue to dark cosmic purple
            r = int(12 + (y / height) * 20)
            g = int(14 + (y / height) * 12)
            b = int(24 + (y / height) * 26)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # Draw a sleek subtle glowing border frame inside the video boundaries
        border_inset = int(40 * (height / 1920.0))
        border_w = int(4 * (height / 1920.0))
        draw.rectangle([border_inset, border_inset, width - border_inset, height - border_inset], outline=(30, 40, 70), width=border_w)
        
        # Subtly overlay a centered soft circular glow aura (neon cyan/mint themed)
        center_x = width // 2
        center_y = height // 2
        max_glow_radius = int(250 * (height / 1920.0))
        for r_offset in range(max_glow_radius, 0, -10):
            draw.ellipse(
                [center_x - r_offset, center_y - r_offset, center_x + r_offset, center_y + r_offset],
                outline=(0, 255, 180),
                width=1
            )
            
        img.save(output_path, "JPEG", quality=95)
    except ImportError:
        # Pillow not installed — create a minimal valid JPEG via raw bytes alternative
        # Just write a tiny placeholder; FFmpeg will handle it
        import struct
        # Minimal 1x1 dark JPEG
        minimal_jpg = bytes([
            0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,
            0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,
            0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,0x07,0x07,0x07,0x09,
            0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
            0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,
            0x24,0x2E,0x27,0x20,0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,
            0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,0x39,0x3D,0x38,0x32,
            0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,
            0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,
            0x01,0x05,0x01,0x01,0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,
            0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,
            0x09,0x0A,0x0B,0xFF,0xC4,0x00,0xB5,0x10,0x00,0x02,0x01,0x03,
            0x03,0x02,0x04,0x03,0x05,0x05,0x04,0x04,0x00,0x00,0x01,0x7D,
            0x01,0x02,0x03,0x00,0x04,0x11,0x05,0x12,0x21,0x31,0x41,0x06,
            0x13,0x51,0x61,0x07,0x22,0x71,0x14,0x32,0x81,0x91,0xA1,0x08,
            0x23,0x42,0xB1,0xC1,0x15,0x52,0xD1,0xF0,0x24,0x33,0x62,0x72,
            0x82,0x09,0x0A,0x16,0x17,0x18,0x19,0x1A,0x25,0x26,0x27,0x28,
            0xFF,0xDA,0x00,0x08,0x01,0x01,0x00,0x00,0x3F,0x00,0xFB,0xD4,
            0xFF,0xD9
        ])
        with open(output_path, 'wb') as f:
            f.write(minimal_jpg)
