import os
from flask import Blueprint, request, jsonify
from ..services.analyzers.graph import build_dependency_graph

graphs_api = Blueprint("graphs_api", __name__)

@graphs_api.post("/deps")
def deps():
    data = request.json or {}
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "error": "path missing"}), 400
    graph = build_dependency_graph(path)
    return jsonify({"success": True, "graph": graph})
