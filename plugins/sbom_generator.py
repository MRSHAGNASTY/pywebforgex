
"""Generate an ultra-simple SBOM (deps list) from requirements.txt."""
from __future__ import annotations
from pathlib import Path, PurePath
import json

def generate(project_dir: str, out_file: str='sbom.json') -> dict:
    req = Path(project_dir)/'requirements.txt'
    deps = []
    if req.exists():
        for line in req.read_text(encoding='utf-8').splitlines():
            line=line.strip()
            if not line or line.startswith('#'): continue
            parts = line.replace(' ','').split('==')
            deps.append({'name': parts[0], 'version': parts[1] if len(parts)>1 else None})
    sbom = {'bomFormat':'alpha','components': deps}
    out = Path(project_dir)/out_file
    out.write_text(json.dumps(sbom, indent=2), encoding='utf-8')
    return {'ok': True, 'path': str(out), 'count': len(deps)}
