import json, subprocess, sys, traceback
from typing import Dict, Any
import os
_venv_bin = os.path.join(os.getcwd(), ".venv", "bin")


def run_function_sandbox(filepath: str, func_name: str, params: Dict[str, Any], timeout: int = 8) -> Dict[str, Any]:
    """Execute a function from a Python file in a subprocess with JSON IO."""
    runner = f"""
import json, traceback, importlib.util
spec = importlib.util.spec_from_file_location('user_module', r'{filepath}')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
try:
    fn = getattr(m, '{func_name}')
    result = fn(**{json.dumps(params)})
    print(json.dumps({{'success': True, 'result': result}}))
except Exception:
    print(json.dumps({{'success': False, 'error': traceback.format_exc()}}))
"""
    try:
        proc = subprocess.run([sys.executable, "-c", runner], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        out = proc.stdout.decode("utf-8", errors="ignore").strip()
        if not out:
            err = proc.stderr.decode("utf-8", errors="ignore").strip()
            return {"success": False, "error": err or "No output"}
        try:
            return json.loads(out)
        except Exception:
            return {"success": False, "error": out}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out"}
