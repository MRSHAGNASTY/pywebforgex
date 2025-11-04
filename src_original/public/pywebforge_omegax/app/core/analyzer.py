import ast, os, json
from typing import Dict, Any

class CodeAnalyzer:
    @staticmethod
    def analyze_source(content: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                "functions": [], "classes": [], "imports": [],
                "lines_of_code": len(content.splitlines()),
                "complexity": 0, "issues": [f"SyntaxError: {e}"], "security": []
            }
        funcs, classes, imports, issues, security = [], [], set(), [], []
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                funcs.append({"name": node.name, "args": args, "line": node.lineno, "doc": ast.get_docstring(node)})
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({"name": node.name, "methods": methods, "line": node.lineno, "doc": ast.get_docstring(node)})
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append("Bare except clause detected")
            if isinstance(node, ast.Call):
                func_name = getattr(node.func, "id", "") or getattr(node.func, "attr", "")
                if func_name == "print":
                    issues.append("Use logging rather than print()")
                if func_name in {"eval", "exec", "__import__", "compile", "open", "os.system", "subprocess"}:
                    security.append(f"Suspicious call: {func_name}()")
        return {
            "functions": funcs, "classes": classes, "imports": list(imports),
            "lines_of_code": len(content.splitlines()), "complexity": complexity,
            "issues": issues, "security": security
        }

    @staticmethod
    def analyze_file(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return CodeAnalyzer.analyze_source(f.read())
