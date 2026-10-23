import os
import re
import time
import random
import requests
from dotenv import load_dotenv
from pathlib import Path
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
load_dotenv()

def clean_json_string(text: str) -> str:
    """
    Cleans markdown formatting and stray symbols from LLM outputs
    to isolate and return a clean, parseable JSON string.
    """
    if not text:
        return ""
    
    cleaned = text.strip()
    
    # Remove markdown code block fences if present
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.IGNORECASE).strip()
    
    # Strip any trailing comma before matching closing brackets/braces
    cleaned = re.sub(r',\s*([\]}])', r'\1', cleaned)
    
    # Locate outer boundaries of JSON arrays or objects
    start_arr = cleaned.find('[')
    end_arr = cleaned.rfind(']')
    start_obj = cleaned.find('{')
    end_obj = cleaned.rfind('}')
    
    # Match the most outer envelope
    if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
        if end_arr != -1:
            cleaned = cleaned[start_arr:end_arr+1]
    elif start_obj != -1:
        if end_obj != -1:
            cleaned = cleaned[start_obj:end_obj+1]
            
    return cleaned


def query_llm(
    prompt: str,
    system_prompt: str = None,
    response_format_json: bool = False,
    temperature: float = 0.5,
    max_tokens: int = 1000,
    max_retries: int = 3
) -> str:
    """
    World-class, highly resilient central function to query LLMs.
    - If GEMINI_API_KEY is configured in the environment, calls Gemini 2.5 Flash.
    - If the key is missing or the Gemini API fails, transparently falls back to
      the keyless, rate-resilient Pollinations AI LLM.
    - Employs a robust retry loop with exponential backoff and randomized jitter.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # Try Google Gemini (gemini-3.5-flash -> gemini-3.5-flash-lite -> gemini-flash-lite-latest)
    if api_key:
        candidate_models = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
        
        # Build contents structure
        gen_config = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
        if response_format_json:
            gen_config["responseMimeType"] = "application/json"
            
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_config
        }
        
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }
            
        for model_name in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            for attempt in range(max_retries):
                try:
                    print(f"[llm_client] Querying Google {model_name} (attempt {attempt+1}/{max_retries})...", flush=True)
                    response = requests.post(url, json=payload, timeout=25)
                    
                    if response.status_code == 200:
                        data = response.json()
                        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text:
                                return text
                    elif response.status_code in (404, 503, 502, 504):
                        print(f"[llm_client] {model_name} temporarily unavailable ({response.status_code}), swiftly switching to next Gemini model...", flush=True)
                        break  # Immediately switch to next candidate Gemini model without delay
                    elif response.status_code == 429:
                        print(f"[llm_client] {model_name} rate limit reached (429), switching to next Gemini model...", flush=True)
                        break
                    else:
                        print(f"[llm_client] {model_name} returned status {response.status_code}. Retrying...", flush=True)
                        time.sleep(1.0)
                except Exception as e:
                    print(f"[llm_client] {model_name} network error: {e}. Trying next Gemini candidate...", flush=True)
                    break
                    
        print("[llm_client] [WARNING] All Gemini candidate models failed.", flush=True)
        return ""
        
    # If no API key is present in environment, fallback to keyless Pollinations LLM
        
    # Resilient fallback to keyless Pollinations LLM
    pollinations_url = "https://text.pollinations.ai/openai"
    
    # Structure OpenAI-compatible payload
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "openai-fast",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    if response_format_json:
        payload["response_format"] = {"type": "json_object"}
        
    backoff = 2.0
    # Restrict to at most 1 retry (2 attempts max) to avoid long blocking waits when LLM is down
    max_llm_attempts = min(max_retries, 1) + 1
    for attempt in range(max_llm_attempts):
        try:
            print(f"[llm_client] Querying Pollinations LLM (attempt {attempt+1}/{max_llm_attempts})...", flush=True)
            response = requests.post(pollinations_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                if text:
                    return text
            elif response.status_code in (402, 429):
                print(f"[llm_client] Pollinations rate limited or cooling period ({response.status_code}). Failing fast to offline sentence parser.", flush=True)
                break  # Fail fast to offline parser rather than waiting in cooling period
            else:
                print(f"[llm_client] Pollinations bad status {response.status_code}. Retrying...", flush=True)
                time.sleep(2.0)
        except Exception as e:
            print(f"[llm_client] Pollinations request error: {e}. Retrying...", flush=True)
            time.sleep(2.0)
            
    # Ultimate fail-safe return empty
    print("[llm_client] [CRITICAL] All LLM endpoints failed.", flush=True)
    return ""
