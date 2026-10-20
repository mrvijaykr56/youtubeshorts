import os
import requests
import threading

# Curated public domain / royalty-free synth background instrumental tracks
TRACKS = {
    "lofi.mp3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",     # Chilled, relaxed tempo
    "upbeat.mp3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",    # Energetic, driving synth beat
    "whoosh.mp3": "https://raw.githubusercontent.com/meheleventyone/mixdown/master/examples/assets/swing.mp3"  # Transition SFX whoosh
}

def download_track(filename: str, url: str, dest_dir: str):
    """Downloads a single music file if not present."""
    dest_path = os.path.join(dest_dir, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"[music_downloader] {filename} already exists, skipping download.", flush=True)
        return

    print(f"[music_downloader] Downloading copyright-free track: {filename}...", flush=True)
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[music_downloader] [OK] Downloaded {filename} ({os.path.getsize(dest_path) // 1024} KB)", flush=True)
        else:
            print(f"[music_downloader] Failed to download {filename}: HTTP {r.status_code}", flush=True)
    except Exception as e:
        print(f"[music_downloader] Error downloading {filename}: {e}", flush=True)


def init_music_assets(base_dir: str):
    """
    Initializes the assets/music directory and launches background threads
    to download the background tracks if they don't exist.
    """
    dest_dir = os.path.join(base_dir, "assets", "music")
    os.makedirs(dest_dir, exist_ok=True)

    for filename, url in TRACKS.items():
        thread = threading.Thread(target=download_track, args=(filename, url, dest_dir))
        thread.daemon = True
        thread.start()
