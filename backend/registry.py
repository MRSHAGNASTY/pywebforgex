
from pathlib import Path
import ast

def scan_file(fp: Path):
    try:
        t = ast.parse(fp.read_text(encoding='utf-8', errors='ignore'))
    except Exception as e:
        return {"path": str(fp), "status": "PARSE_ERROR", "error": repr(e)}
    funcs = []
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            args = [a.arg for a in n.args.args]
            doc = ast.get_docstring(n) or ""
            funcs.append({"name": n.name, "args": args, "doc": doc})
    return {"path": str(fp), "status": "OK", "functions": funcs}

def scan_registry(root: Path):
    root = Path(root)
    out = {}
    for p in root.rglob("*.py"):
        rel = str(p.relative_to(root)).replace("\\","/")
        r = scan_file(p)
        if r.get("functions"):
            out[rel] = r["functions"]
    return out
