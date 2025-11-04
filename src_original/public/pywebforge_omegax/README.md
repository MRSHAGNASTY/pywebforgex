# PyWebForge ΩX (Omega X)

Next‑gen, self‑augmenting Python micro‑IDE with AI reasoning, docs generation, dependency graphs, plugins, WebSockets, and secure(ish) sandboxing.

## Quick start

```bash
# local
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m app

# docker
docker compose up --build
```

Open http://localhost:5000

## Environment

- `OPENAI_API_KEY`  (optional; enables OpenAI adapter)
- `OLLAMA_HOST`     (optional; enables Ollama adapter; default http://localhost:11434)
- `PYWEBFORGE_SECRET` (Flask secret)

## Features
- Monaco editor, D3 graphs, live logs
- AST analyzer → function/class graph
- LLM adapters (OpenAI, Ollama)
- Auto‑docs generator → README & API docs
- Plugin system with safe registry
- WebSocket console for live events
- Orchestrator builds & zips artifacts
- Unit tests (pytest), coverage, black
- Dockerfile + compose
