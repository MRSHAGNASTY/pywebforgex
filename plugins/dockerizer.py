
"""Create a Dockerfile for a simple python app/lib."""
from __future__ import annotations
from pathlib import Path

DF = """FROM python:3.11-slim\nWORKDIR /app\nCOPY . /app\nRUN pip install --no-cache-dir -r requirements.txt || true\nCMD [\"python\",\"-c\",\"print('ok')\"]\n"""

def dockerize(project_dir: str) -> dict:
    p = Path(project_dir); (p/'Dockerfile').write_text(DF, encoding='utf-8')
    return {"ok": True, "path": str(p/'Dockerfile')}
