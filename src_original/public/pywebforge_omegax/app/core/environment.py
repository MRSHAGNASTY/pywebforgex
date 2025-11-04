import os, tempfile, venv, subprocess, hashlib
from typing import Optional
def _hash_path(p: str) -> str:
    return hashlib.sha256(os.path.abspath(p).encode('utf-8')).hexdigest()[:12]
def ensure_env_for_project(project_dir: str, base_dir: Optional[str] = None, allow_network: bool = True, timeout: int = 600) -> str:
    base = base_dir or os.path.join(tempfile.gettempdir(), "pwf_envs")
    os.makedirs(base, exist_ok=True)
    env_path = os.path.join(base, f"env_{_hash_path(project_dir)}")
    if not os.path.exists(env_path):
        venv.create(env_path, with_pip=True)
        req = os.path.join(project_dir, "requirements.txt")
        if os.path.exists(req):
            pip = os.path.join(env_path, "Scripts" if os.name == "nt" else "bin", "pip")
            env = os.environ.copy()
            from .settings import WHEEL_CACHE
            env['PIP_CACHE_DIR'] = str(WHEEL_CACHE)
            subprocess.run([pip, "install", "-r", req], check=False, env=env, timeout=timeout)
    return env_path

def destroy_env_for_project(project_name: str) -> None:
    """Safely remove or reset a project's virtual environment (stub)."""
    # No-op placeholder for backward compatibility
    return
