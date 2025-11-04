import os, markdown
from flask import Blueprint, request, jsonify
from ..core.analyzer import CodeAnalyzer

docs_api = Blueprint("docs_api", __name__)

@docs_api.post("/autodoc")
def autodoc():
    data = request.json or {}
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "error": "path missing"}), 400
    docs = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                with open(p, "r", encoding="utf-8") as fh:
                    content = fh.read()
                a = CodeAnalyzer.analyze_source(content)
                docs.append(f"## {f}\n\n**Imports**: {', '.join(a['imports'])}\n\n**Functions**:\n" + "\n".join([f"- `{fn['name']}({', '.join(fn['args'])})`" for fn in a['functions']]) + "\n")
    readme = "# Project Documentation\n\n" + "\n\n".join(docs)
    return jsonify({"success": True, "markdown": readme, "html": markdown.markdown(readme)})
