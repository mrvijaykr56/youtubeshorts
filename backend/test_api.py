import requests
import time
import os

BASE_URL = "http://localhost:5000"

# A real, interesting script with 3 clear scenes
script = (
    "Did you know that honey never spoils? "
    "Archaeologists have found pots of honey in ancient Egyptian tombs "
    "that are over 3000 years old and still perfectly edible! "
    "This is because honey is naturally acidic and has very low moisture, "
    "creating an environment where bacteria just cannot survive."
)

print(f"Submitting real script ({len(script)} chars)...")
response = requests.post(f"{BASE_URL}/generate", json={"script": script})
job_id = response.json().get("job_id")
print(f"Job ID: {job_id}")

prev_msg = ""
while True:
    status_res = requests.get(f"{BASE_URL}/status/{job_id}").json()
    state = status_res.get("state")
    message = status_res.get("message")
    if message != prev_msg:
        print(f"  [{state}] {message}")
        prev_msg = message
    if state == "completed":
        dl = requests.get(f"{BASE_URL}/download/{job_id}")
        fname = f"honey_ai_{job_id[:8]}.mp4"
        with open(fname, "wb") as f:
            f.write(dl.content)
        size = os.path.getsize(fname)
        print(f"\nDownloaded: {fname} ({size/1024:.1f} KB)")
        print("SUCCESS - Check output folder for scene_*.jpg AI images!")
        break
    elif state == "error":
        print(f"\nERROR: {message}")
        break
    time.sleep(3)

# List scene images in output dir
output_dir = os.path.join(os.path.dirname(__file__), "output")
scene_files = sorted([f for f in os.listdir(output_dir) if f.startswith("scene_")])
print(f"\nAI Scene Images in output/: {scene_files}")
for sf in scene_files:
    fp = os.path.join(output_dir, sf)
    print(f"  {sf}: {os.path.getsize(fp)/1024:.1f} KB")
