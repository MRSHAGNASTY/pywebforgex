
import yaml
from pathlib import Path

def load_policy(p: Path):
    try: return yaml.safe_load(p.read_text()) or {}
    except Exception: return {}

def check_allowed(policy: dict, module_rel: str, function: str):
    deny = (policy or {}).get("deny", {})
    if any(module_rel.endswith(x) for x in deny.get("modules", [])): return False, f"module {module_rel} denied"
    if function in deny.get("functions", []): return False, f"function {function} denied"
    return True, ""
