
"""Generate pytest skeletons for a module's functions."""
from __future__ import annotations
from pathlib import Path
import ast

def generate_tests(module_path: str, out_dir: str) -> dict:
    p = Path(module_path); t = ast.parse(p.read_text(encoding='utf-8', errors='ignore'))
    tests = []
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            test_name = f"test_{n.name}"
            body = f"def {test_name}():\n    # TODO: set inputs/expected\n    from {p.stem} import {n.name}\n    assert True\n"
            tests.append((test_name, body))
    o = Path(out_dir); o.mkdir(parents=True, exist_ok=True)
    for name, content in tests:
        (o/f"{name}.py").write_text(content, encoding='utf-8')
    return {"ok": True, "tests": [n for n,_ in tests]}
