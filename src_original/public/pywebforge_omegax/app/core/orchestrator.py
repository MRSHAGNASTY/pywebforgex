import os, shutil, uuid
from typing import Dict, Any

def orchestrate(project_path: str, output_root: str) -> Dict[str, Any]:
    out = os.path.join(output_root, f'build_{uuid.uuid4().hex}')
    os.makedirs(out, exist_ok=True)
    result = {"status": "starting", "generated": [], "errors": []}
    try:
        for root, _, files in os.walk(project_path):
            for fn in files:
                if fn.endswith('.py'):
                    src = os.path.join(root, fn)
                    dst = os.path.join(out, os.path.relpath(src, project_path))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy(src, dst)
                    result["generated"].append(dst)
        result["status"] = "complete"
        return result
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        return result
