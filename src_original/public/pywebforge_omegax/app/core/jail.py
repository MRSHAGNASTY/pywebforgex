import os, shutil, uuid, pathlib
from .settings import TMP_ROOT
def create_run_jail(project_dir: str):
    run_id = str(uuid.uuid4())
    base = TMP_ROOT / run_id; src = base / "src"; out = base / "out"
    src.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(project_dir):
        rel = os.path.relpath(root, project_dir)
        if any(part in ("__pycache__", ".venv", "venv") for part in rel.split(os.sep)): continue
        dst_root = src / rel; pathlib.Path(dst_root).mkdir(parents=True, exist_ok=True)
        for f in files:
            if f.endswith((".pyc",".pyo")): continue
            sp = os.path.join(root, f); dp = dst_root / f; shutil.copy2(sp, dp)
    return str(base), str(src), str(out)
def cleanup_run_jail(base_path: str):
    shutil.rmtree(base_path, ignore_errors=True)
