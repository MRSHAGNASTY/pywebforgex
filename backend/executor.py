
from __future__ import annotations
import subprocess, sys, json
from pathlib import Path
from ai_engine import ADVISOR  # keep advisor

def call_function(module_path: Path, func_name: str, args=None, kwargs=None, with_ai=False, dry_run=False, timeout_s=10, egress_deny=True, mem_mb=256, cpu_s=5):
    args = args or []; kwargs = kwargs or {}
    if dry_run:
        return {"ok": True, "dry_run": True, "plan": {"module": str(module_path), "function": func_name, "args": args, "kwargs": kwargs, "limits":{"mem_mb":mem_mb,"cpu_s":cpu_s}}}
    worker = Path(__file__).resolve().parent/"exec_worker.py"
    payload = json.dumps({
        "module_path": str(module_path), "function": func_name, "args": args, "kwargs": kwargs,
        "limits": {"mem_mb": mem_mb, "cpu_s": cpu_s}
    })
    try:
        p = subprocess.Popen([sys.executable, str(worker)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, err = p.communicate(payload, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            p.kill()
            return {"ok": False, "error": "timeout", "traceback": None}
        try:
            data = json.loads(out or "{}")
        except Exception:
            data = {"ok": False, "error": "bad worker output", "stderr": err}
        if not data.get("ok") and with_ai and data.get("traceback"):
            data["advice"] = ADVISOR.suggest_from_exception(data["traceback"])
        return data
    except Exception as e:
        return {"ok": False, "error": repr(e)}
