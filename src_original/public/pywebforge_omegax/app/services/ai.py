import os
from .llm_adapters.openai_adapter import openai_chat
from .llm_adapters.ollama_adapter import ollama_chat

class PyWebForgeAI:
    def __init__(self):
        self.version = "omegax-1.0"

    def reason(self, prompt: str) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            return "No prompt provided."
        # Prefer OpenAI if key present, else Ollama, else fallback
        if os.getenv("OPENAI_API_KEY"):
            return openai_chat(prompt)
        if os.getenv("OLLAMA_HOST"):
            return ollama_chat(prompt)
        # Fallback lightweight heuristics
        p = prompt.lower()
        if "analyze" in p: return "Use Analyze on the file or project to view structure, complexity and issues."
        if "repair" in p or "fix" in p: return "Use Auto-Repair to patch bare excepts and simple syntax faults."
        if "build" in p or "orchestrate" in p: return "Use Build to orchestrate and package your project."
        return f"[PyWebForgeAI] Understood: {prompt}"
