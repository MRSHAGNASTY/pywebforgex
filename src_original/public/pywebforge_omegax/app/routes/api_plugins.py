import importlib, pkgutil
from flask import Blueprint, request, jsonify
from ..services.plugins import REGISTRY

plugins_api = Blueprint("plugins_api", __name__)

@plugins_api.get("/list")
def list_plugins():
    return jsonify({"success": True, "plugins": list(REGISTRY.keys())})

@plugins_api.post("/run")
def run_plugin():
    data = request.json or {}
    name = data.get("name")
    kwargs = data.get("kwargs", {})
    if name not in REGISTRY:
        return jsonify({"success": False, "error": "plugin not found"}), 404
    try:
        result = REGISTRY[name](**kwargs)
        return jsonify({"success": True, "result": result})
    except TypeError as e:
        return jsonify({"success": False, "error": f"Bad args: {e}"}), 400
