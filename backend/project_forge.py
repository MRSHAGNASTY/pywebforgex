
from __future__ import annotations
from pathlib import Path
TEMPLATES = {
  "flask-app": {
    "app.py": "from flask import Flask\napp=Flask(__name__)\n@app.get('/')\ndef hi(): return 'ok'\nif __name__=='__main__': app.run()\n",
    "requirements.txt": "Flask\n"
  },
  "python-lib": {
    "pkg/__init__.py": "__all__=['add']\n",
    "pkg/add.py": "def add(a,b): return a+b\n",
    "pyproject.toml": "[project]\nname='example'\nversion='0.0.1'\n"
  }
}
def scaffold(dest: Path, kind: str, name: str):
    dest = Path(dest)/name
    dest.mkdir(parents=True, exist_ok=True)
    tpl = TEMPLATES.get(kind) or {}
    for rel, content in tpl.items():
        p = dest/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
    return {"ok": True, "path": str(dest), "files": len(tpl)}

from .forge_packs import materialize as pack_materialize

def scaffold_pack(dest, pack: str, name: str):
    return pack_materialize(dest, pack, name)
