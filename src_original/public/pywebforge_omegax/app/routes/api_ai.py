from flask import Blueprint, request, jsonify
from ..services.ai import PyWebForgeAI

ai_api = Blueprint("ai_api", __name__)
AI = PyWebForgeAI()

@ai_api.post("/query")
def query():
    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"success": False, "error": "no prompt"}), 400
    resp = AI.reason(prompt)
    return jsonify({"success": True, "response": resp})
