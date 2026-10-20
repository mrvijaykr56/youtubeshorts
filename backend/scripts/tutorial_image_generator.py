import os
import re
import sys
import time
import requests
import hashlib
import shutil
from PIL import Image, ImageDraw, ImageFilter

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
    Prepended to every slide's illustration prompt so all slides share the same
    visual universe: color palette, lighting mood, setting, and style.
    Falls back to the first scene's visual if the LLM call fails.
    """
    if not scenes:
        return ""

    scene_summaries = []
    for i, s in enumerate(scenes):
        vis = s.get("visual", s.get("narration", ""))[:120]
        narr = s.get("narration", "")[:80]
        scene_summaries.append(f"Scene {i+1}: {narr} | Visual: {vis}")
    full_summary = "\n".join(scene_summaries)

    prompt = (
        "You are a film production designer. Analyze the following tutorial storyboard scenes and "
        "produce ONE concise sentence (max 40 words) describing the shared visual world: "
        "include the dominant setting/environment, color palette, lighting mood, and visual style. "
        "This sentence will be prepended to AI image prompts to ensure all slides look visually consistent.\n"
        "Output ONLY the sentence, nothing else.\n\n"
        f"Storyboard:\n{full_summary}"
    )

    try:
        from scripts.llm_client import query_llm
        result = query_llm(prompt, temperature=0.3, max_tokens=80)
        if result and len(result.strip()) > 10:
            ctx = result.strip().strip('"\'')
            print(f"[tutorial_image_generator] [STORY CONTEXT] {ctx}", flush=True)
            return ctx
    except Exception as e:
        print(f"[tutorial_image_generator] build_story_context LLM failed ({e}), using fallback.", flush=True)

    fallback_visual = scenes[0].get("visual", scenes[0].get("narration", ""))[:100]
    fallback_ctx = f"Consistent visual world: {fallback_visual}"
    print(f"[tutorial_image_generator] [STORY CONTEXT FALLBACK] {fallback_ctx}", flush=True)
    return fallback_ctx


def enrich_visual_prompt(scene_visual: str, art_style: str, scene_index: int = 0) -> str:
    """
    Enriches simple visual prompts with details tailored to the selected art style.
    """
    prompt = scene_visual.strip()
    if prompt.endswith("."):
        prompt = prompt[:-1]
        
    modifiers = {
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
        
    camera_perspectives = [
        ", dramatic close-up shot, extreme detail, cinematic studio lighting",
        ", cinematic medium-shot, photorealistic details, 85mm portrait lens, shallow depth of field",
        ", sweeping wide-angle cinematic shot, majestic scenery, dynamic volumetric lighting, golden hour octane render"
    ]
    camera_modifier = camera_perspectives[scene_index % len(camera_perspectives)]
        
    return prompt + modifiers.get(match_key, "") + camera_modifier


def download_single_image(i, scene, style_template, seed_offset, output_dir, job_id, art_style, width: int = 2160, height: int = 3840, story_context: str = ""):
    """
    Synthesizes and downloads tutorial presentation slide frames.
    """
    # Stagger thread start slightly to prevent concurrent requests hitting Pollinations at the exact same millisecond
    if i > 0:
        time.sleep(i * 1.2)

    illust_path = None
    
    # Only download custom Pollinations illustrations if there's no terminal code snippet
    if not scene.get("code_snippet", "").strip():
        illust_temp_path = os.path.join(output_dir, f"{job_id}_scene_{i:02d}_illust.jpg")
        scene_visual = scene.get("visual", "clean graphical slide icon")
        enriched_illust = enrich_visual_prompt(scene_visual, art_style, scene_index=i)

        # Prepend global story-coherence context so all slide illustrations share the same visual world
        if story_context:
            coherent_illust = f"{story_context}. {enriched_illust}"
        else:
            coherent_illust = enriched_illust
        prompt = style_template.replace("{prompt}", coherent_illust)
        
        from urllib.parse import quote as url_quote
        encoded_prompt = url_quote(prompt, safe='')
        seed = (seed_offset + i) % 100000
        
        style_key = str(art_style).lower().strip()
        if "pixar" in style_key or "3d" in style_key:
            model = "flux-3d"
        elif "anime" in style_key:
            model = "flux-anime"
        elif "cinematic" in style_key:
            model = "flux-realism"
        else:
            model = "flux"
            
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}&model={model}&enhance=true"
        
        # Download the square illustration
        for attempt in range(2):
            try:
                print(f"[tutorial_image_generator] Slide {i+1} Illustration download: (attempt {attempt+1})...", flush=True)
                response = requests.get(url, timeout=30)
                if response.status_code == 200 and len(response.content) > 1000:
                    with open(illust_temp_path, 'wb') as f:
                        f.write(response.content)
                    illust_path = illust_temp_path
                    break
            except Exception as e:
                print(f"[tutorial_image_generator] Slide {i+1} Illustration download failed: {e}", flush=True)
                time.sleep(1)
                
    # Compile the final slide image using Pillow renderer
    output_path = os.path.join(output_dir, f"{job_id}_scene_{i:02d}.jpg")
    from scripts.slide_renderer import render_slide
    scene["art_style"] = art_style
    render_slide(scene, output_path, width=width, height=height, illustration_path=illust_path)
    
    # Cleanup temporary illustration icon
    if illust_path and os.path.exists(illust_path):
        try:
            os.remove(illust_path)
        except Exception:
            pass
            
    return output_path


def generate_scene_images(script: str, output_dir: str, job_id: str = "default", art_style: str = "cinematic", width: int = 2160, height: int = 3840, progress_callback = None) -> list[str]:
    """
    Renders presentation slides for all scenes in the tutorial script concurrently using ThreadPoolExecutor.

    Visual Coherence: A single story-context brief is derived from the full storyboard
    and injected into every slide's illustration prompt so all slides share the same
    visual world (color palette, lighting mood, background style).
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
    # Passed to every worker so all slide illustrations share the same visual universe.
    story_context = build_story_context(scenes)

    print(f"[tutorial_image_generator] Generating {len(scenes)} tutorial slide frames concurrently ({width}x{height}) using ThreadPoolExecutor...", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed
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
            print(f"[tutorial_image_generator] Slide {idx+1} slide render exception: {exc}", flush=True)
            # Create standard fallback slide
            fallback_path = os.path.join(output_dir, f"{job_id}_scene_{idx:02d}.jpg")
            from scripts.slide_renderer import render_slide
            scene["art_style"] = art_style
            render_slide(scene, fallback_path, width=width, height=height)
            image_paths[idx] = fallback_path
        return idx

    # Keep concurrency bounded to 3 to stay well within Pollinations API thresholds
    futures = {}
    completed_count = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        for idx, scene in enumerate(scenes):
            fut = executor.submit(worker_task, idx, scene)
            futures[fut] = idx
        for fut in as_completed(futures):
            fut.result()
            completed_count += 1
            if progress_callback:
                try:
                    progress_callback(completed_count, len(scenes), status="completed_scene")
                except Exception as e:
                    print(f"[tutorial_image_generator] Progress callback error: {e}", flush=True)

    return image_paths
