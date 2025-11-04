
"""Naive license inventory from requirements.txt (names only)."""
from __future__ import annotations
from pathlib import Path

def inventory(project_dir: str) -> dict:
    req = Path(project_dir)/'requirements.txt'
    libs = []
    if req.exists():
        for line in req.read_text(encoding='utf-8').splitlines():
            line=line.strip()
            if not line or line.startswith('#'): continue
            libs.append(line.split('==')[0])
    return {"ok": True, "libraries": libs}
