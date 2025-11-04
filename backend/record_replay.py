
import json, hashlib
from pathlib import Path

def _key(tenant: str, module_rel: str, function: str, args, kwargs) -> str:
    blob = json.dumps({"t":tenant,"m":module_rel,"f":function,"a":args,"k":kwargs}, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()

def record(storage_dir: Path, tenant: str, module_rel: str, function: str, args, kwargs, result: dict):
    store = storage_dir/"exec_record.json"
    data = json.loads(store.read_text()) if store.exists() else {}
    data[_key(tenant,module_rel,function,args,kwargs)] = {"ok": result.get("ok", False), "result": result.get("result"), "advice": result.get("advice"), "traceback": result.get("traceback")}
    store.write_text(json.dumps(data, indent=2))

def replay(storage_dir: Path, tenant: str, module_rel: str, function: str, args, kwargs):
    store = storage_dir/"exec_record.json"
    if not store.exists(): return None
    data = json.loads(store.read_text())
    return data.get(_key(tenant,module_rel,function,args,kwargs))
