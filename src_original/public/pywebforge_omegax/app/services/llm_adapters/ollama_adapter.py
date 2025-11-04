import os, requests, json

def ollama_chat(prompt: str) -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        r = requests.post(f"{host}/api/generate", json={"model": "llama3", "prompt": prompt, "stream": False})
        r.raise_for_status()
        data = r.json()
        return data.get("response", "No response")
    except Exception as e:
        return f"[Ollama adapter error] {e}"
