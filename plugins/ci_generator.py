
"""Generate a minimal GitHub Actions CI workflow."""
from __future__ import annotations
from pathlib import Path

YAML = """name: ci\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: {python-version: '3.11'}\n      - run: pip install -r requirements.txt || true\n      - run: pip install pytest\n      - run: pytest -q\n"""

def write_ci(project_dir: str) -> dict:
    p = Path(project_dir)/'.github'/'workflows'; p.mkdir(parents=True, exist_ok=True)
    (p/'ci.yml').write_text(YAML, encoding='utf-8')
    return {"ok": True, "path": str(p/'ci.yml')}
