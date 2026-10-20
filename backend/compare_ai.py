import requests
import time
import sys
import io

# Force UTF-8 output on Windows to handle AI-generated unicode
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAW_SCRIPT = "honey is old. scientists found old honey in egypt pyramids. it was still good. honey does not go bad because of acid and no water in it. bacteria cannot live in honey."

SYSTEM_PROMPT = """You are an expert YouTube Shorts scriptwriter. Polish this raw script for maximum engagement.
Rules: Hook in first sentence. Max 70 words. Punchy short sentences. End with a wow fact.
Return ONLY the polished script. No titles, no hashtags, no commentary."""


def test_pollinations():
    """Test Pollinations.ai - 100% free, no API key"""
    start = time.time()
    try:
        payload = {
            "model": "openai",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": RAW_SCRIPT}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        r = requests.post("https://text.pollinations.ai/openai", json=payload, timeout=30)
        elapsed = time.time() - start
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            return {"status": "OK", "time": elapsed, "text": text, "error": None}
        else:
            return {"status": "FAIL", "time": elapsed, "text": None, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "time": time.time() - start, "text": None, "error": str(e)}


def test_groq():
    """Test Groq - free tier, needs API key (check env)"""
    import os
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return {"status": "SKIP", "time": 0, "text": None, "error": "No GROQ_API_KEY env var set"}

    start = time.time()
    try:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": RAW_SCRIPT}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=20
        )
        elapsed = time.time() - start
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            return {"status": "OK", "time": elapsed, "text": text, "error": None}
        else:
            return {"status": "FAIL", "time": elapsed, "text": None, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"status": "FAIL", "time": time.time() - start, "text": None, "error": str(e)}


def test_ollama():
    """Test Ollama - local, completely offline"""
    start = time.time()
    try:
        # First check if Ollama is running
        r_check = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r_check.status_code != 200:
            return {"status": "SKIP", "time": 0, "text": None, "error": "Ollama not running (start with: ollama serve)"}

        # Find available models
        models = r_check.json().get("models", [])
        model_names = [m["name"] for m in models]
        if not model_names:
            return {"status": "SKIP", "time": 0, "text": None, "error": "No Ollama models installed (run: ollama pull llama3.2)"}

        # Use first available model
        model = model_names[0]
        print(f"  [Ollama] Using model: {model}")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": RAW_SCRIPT}
            ],
            "stream": False
        }
        r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        elapsed = time.time() - start
        if r.status_code == 200:
            text = r.json()["message"]["content"].strip()
            return {"status": "OK", "time": elapsed, "text": text, "error": None, "model": model}
        else:
            return {"status": "FAIL", "time": elapsed, "text": None, "error": f"HTTP {r.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "SKIP", "time": 0, "text": None, "error": "Ollama not running (install from ollama.com, then: ollama serve)"}
    except Exception as e:
        return {"status": "FAIL", "time": time.time() - start, "text": None, "error": str(e)}


def print_result(name, emoji, result):
    line = "-" * 60
    print(f"\n{line}")
    print(f"  {emoji}  {name}")
    print(line)
    print(f"  Status : {result['status']}")
    print(f"  Time   : {result['time']:.2f}s")
    if result.get("model"):
        print(f"  Model  : {result['model']}")
    if result["status"] == "OK":
        # Sanitize: replace non-ASCII chars that Windows console can't handle
        safe_text = result['text'].encode('ascii', errors='replace').decode('ascii')
        print(f"  Words  : {len(result['text'].split())}")
        print(f"\n  Output :\n")
        words = safe_text.split()
        line_buf, lines_out = [], []
        for w in words:
            line_buf.append(w)
            if len(" ".join(line_buf)) > 55:
                lines_out.append("    " + " ".join(line_buf[:-1]))
                line_buf = [w]
        if line_buf:
            lines_out.append("    " + " ".join(line_buf))
        print("\n".join(lines_out))
    elif result["status"] == "SKIP":
        print(f"  Reason : {result['error']}")
    else:
        print(f"  Error  : {result['error']}")


print("=" * 60)
print("  SCRIPT POLISHER — LIVE AI COMPARISON TEST")
print("=" * 60)
print(f"\n  RAW INPUT ({len(RAW_SCRIPT.split())} words):")
print(f"  \"{RAW_SCRIPT}\"\n")

print("\n[1/3] Testing Pollinations.ai...")
r1 = test_pollinations()

print("[2/3] Testing Groq...")
r2 = test_groq()

print("[3/3] Testing Ollama (local)...")
r3 = test_ollama()

print_result("POLLINATIONS.AI  (free, no API key, uses GPT-4o)", "[1]", r1)
print_result("GROQ             (free tier, Llama 3.3 70B, fastest)", "[2]", r2)
print_result("OLLAMA           (local, offline, no limits)", "[3]", r3)

print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
results = [
    ("Pollinations.ai", r1, "No key needed, cloud GPT-4o"),
    ("Groq",            r2, "Needs free API key, very fast"),
    ("Ollama",          r3, "Fully local, needs install"),
]
for name, res, note in results:
    speed = f"{res['time']:.2f}s" if res['time'] > 0 else "N/A"
    status = res['status']
    print(f"  {status:5s} | {speed:8s} | {name:20s} | {note}")
print()
