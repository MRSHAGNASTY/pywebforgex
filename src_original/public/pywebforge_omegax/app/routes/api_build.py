import os, uuid
from flask import Blueprint, request, jsonify
from ..core.orchestrator import orchestrate
from ..utils.paths import GENERATED_DIR

build_api = Blueprint("build_api", __name__)

@build_api.post("/orchestrate")
def build():
    data = request.json or {}
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "error": "path missing"}), 400
    out_root = os.path.join(GENERATED_DIR, f"builds_{uuid.uuid4().hex}")
    os.makedirs(out_root, exist_ok=True)
    result = orchestrate(path, out_root)
    return jsonify({"success": True, "result": result, "build_path": out_root})
