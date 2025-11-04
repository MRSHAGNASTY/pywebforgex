
from __future__ import annotations
import importlib.util, sys, json, traceback, resource, os
from pathlib import Path

def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

def set_limits(mem_mb: int, cpu_s: int):
    try:
        if mem_mb:
            resource.setrlimit(resource.RLIMIT_AS, (mem_mb*1024*1024, mem_mb*1024*1024))
        if cpu_s:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
    except Exception:
        pass

def main():
    data = json.loads(sys.stdin.read())
    module_path = Path(data["module_path"]); func = data["function"]
    args = data.get("args", []); kwargs = data.get("kwargs", {})
    limits = data.get("limits", {"mem_mb":256,"cpu_s":5})
    try:
        import socket
        class Blocker(socket.socket):
            def connect(self, *a, **k): raise RuntimeError("egress denied")
        socket.socket = Blocker
    except Exception:
        pass
    set_limits(limits.get("mem_mb",256), limits.get("cpu_s",5))
    try:
        mod = load_module_from_path("dyn_"+module_path.stem, module_path)
        fn = getattr(mod, func, None)
        if not callable(fn):
            print(json.dumps({"ok":False,"error":f"{func} not found"})); return
        res = fn(*args, **kwargs)
        print(json.dumps({"ok":True,"result":res}, default=str))
    except Exception as e:
        tb = traceback.format_exc()
        print(json.dumps({"ok":False,"error":repr(e),"traceback":tb}))

if __name__ == "__main__":
    main()
