from flask import Blueprint, jsonify
from ..core.observability import snapshot
health_bp=Blueprint("health_bp", __name__)
@health_bp.get("/health")
def health(): return jsonify({"ok": True})
@health_bp.get("/metrics")
def metrics(): return jsonify(snapshot())
