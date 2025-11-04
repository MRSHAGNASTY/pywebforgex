import os, ast
from flask import Blueprint, request, jsonify
classify_api = Blueprint("classify_api", __name__)
WEB_IMPORTS = {"flask","fastapi","starlette","streamlit","gradio","dash","django"}
CLI_IMPORTS = {"argparse","click","typer"}
def _scan_py(project):
    mods=set()
    for root,_,files in os.walk(project):
        for f in files:
            if f.endswith(".py"):
                p=os.path.join(root,f)
                try:
                    with open(p,"r",encoding="utf-8") as fh:
                        import ast as _ast; tree=_ast.parse(fh.read())
                    for node in _ast.walk(tree):
                        if isinstance(node,_ast.Import):
                            for a in node.names: mods.add(a.name.split(".")[0])
                        elif isinstance(node,_ast.ImportFrom) and node.module:
                            mods.add(node.module.split(".")[0])
                except Exception: pass
    return mods
@classify_api.post("/analyze/classify_project")
def classify_project():
    data=request.json or {}; project=data.get("project")
    if not project or not os.path.isdir(project): return jsonify({"success":False,"error":"valid 'project' path required"}),400
    mods=_scan_py(project)
    evidence={"imports":sorted(list(mods))[:64],"has_templates":os.path.isdir(os.path.join(project,"templates")),"has_static":os.path.isdir(os.path.join(project,"static")),"has_routes_dir":os.path.isdir(os.path.join(project,"app","routes"))}
    score_web=int(bool(evidence["has_templates"] or evidence["has_static"] or evidence["has_routes_dir"]))+sum(1 for m in mods if m in WEB_IMPORTS)
    score_cli=sum(1 for m in mods if m in CLI_IMPORTS)
    mode="library"
    if score_web>=max(1,score_cli+1): mode="web"
    elif score_cli>=1: mode="cli"
    return jsonify({"success":True,"mode":mode,"evidence":evidence})
