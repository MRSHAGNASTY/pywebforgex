import os, subprocess, json, hashlib, time, sys
from .sandbox import _venv_bin
def pip_freeze(venv_path: str):
    py = _venv_bin(venv_path, "python")
    try:
        out = subprocess.check_output([py, "-m", "pip", "freeze"], text=True, timeout=60)
        return [l.strip() for l in out.splitlines() if l.strip()]
    except Exception: return []
def run_pip_audit(venv_path: str):
    py = _venv_bin(venv_path, "python")
    try:
        subprocess.run([py, "-m", "pip", "install", "pip-audit"], timeout=60, check=False)
        out = subprocess.check_output([py, "-m", "pip_audit", "-f", "json"], text=True, timeout=120)
        return json.loads(out)
    except Exception: return {"warning": "pip-audit not available or failed"}
def file_hashes(project_dir: str):
    items = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith((".pyc",".pyo")): continue
            p = os.path.join(root, f)
            try:
                with open(p, "rb") as fh: h = hashlib.sha256(fh.read()).hexdigest()
                items.append({"path": os.path.relpath(p, project_dir), "sha256": h})
            except Exception: pass
    return items
def build_stamp(): return {"ts": time.time(), "python": sys.version}
def build_sbom(venv_path: str, project_dir: str):
    return {"build_info": build_stamp(), "packages": pip_freeze(venv_path), "audit": run_pip_audit(venv_path), "files": file_hashes(project_dir)}
