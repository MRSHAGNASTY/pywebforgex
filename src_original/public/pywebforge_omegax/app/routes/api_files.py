import os, uuid, zipfile, shutil
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from ..core.analyzer import CodeAnalyzer
from ..core.sandbox import run_function_sandbox
from ..utils.paths import UPLOAD_DIR, GENERATED_DIR
from ..utils.logs import write_log

ALLOWED_EXT = {'.py', '.zip', '.txt'}

files_api = Blueprint("files_api", __name__)

@files_api.post("/upload")
def upload():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "no file part"}), 400
    f = request.files['file']
    if f.filename == "":
        return jsonify({"success": False, "error": "no filename"}), 400
    if os.path.splitext(f.filename)[1].lower() not in ALLOWED_EXT:
        return jsonify({"success": False, "error": "file type not allowed"}), 400
    name = secure_filename(f.filename)
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{name}")
    f.save(save_path)
    write_log(f"Uploaded {name} -> {save_path}")
    if name.lower().endswith(".zip"):
        project_dir = os.path.join(UPLOAD_DIR, f"project_{uuid.uuid4().hex}")
        os.makedirs(project_dir, exist_ok=True)
        with zipfile.ZipFile(save_path, 'r') as z:
            z.extractall(project_dir)
        write_log(f"Extracted project to {project_dir}")
        return jsonify({"success": True, "path": project_dir, "is_project": True})
    else:
        dest = os.path.join(UPLOAD_DIR, f"file_{uuid.uuid4().hex}_{name}")
        shutil.copy(save_path, dest)
        return jsonify({"success": True, "path": dest, "is_project": False})

@files_api.post("/read")
def read_file():
    data = request.json or {}
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "error": "path missing"}), 400
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"success": True, "content": content, "analysis": CodeAnalyzer.analyze_source(content)})

@files_api.post("/save")
def save_file():
    data = request.json or {}
    path = data.get("path")
    content = data.get("content", "")
    if not path:
        return jsonify({"success": False, "error": "path missing"}), 400
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    write_log(f"Saved file {path}")
    return jsonify({"success": True})

@files_api.post("/execute")
def execute():
    data = request.json or {}
    path = data.get("path")
    func = data.get("function")
    params = data.get("params", {})
    if not (path and func):
        return jsonify({"success": False, "error": "missing path or function"}), 400
    out = run_function_sandbox(path, func, params, timeout=8)
    write_log(f"Executed {func} in {path}: success={out.get('success')}")
    return jsonify({"success": True, "result": out})

@files_api.get("/download_build")
def download_build():
    builds = []
    for name in os.listdir(GENERATED_DIR):
        full = os.path.join(GENERATED_DIR, name)
        if os.path.isdir(full):
            builds.append((os.path.getmtime(full), full))
    if not builds:
        return jsonify({"success": False, "error": "no build found"}), 404
    builds.sort(reverse=True)
    latest = builds[0][1]
    buf_path = os.path.join(GENERATED_DIR, "pywebforge_build.zip")
    if os.path.exists(buf_path):
        os.remove(buf_path)
    import zipfile
    with zipfile.ZipFile(buf_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(latest):
            for f in files:
                absf = os.path.join(root, f)
                arc = os.path.relpath(absf, latest)
                z.write(absf, arc)
    return send_file(buf_path, mimetype="application/zip", as_attachment=True, download_name="pywebforge_build.zip")
