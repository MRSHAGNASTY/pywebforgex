
from __future__ import annotations
import time, ipaddress
from typing import Dict, Tuple
from flask import request, jsonify
from config import settings

_BUCKETS: Dict[str, Tuple[float,float]] = {}

def _client_id() -> str:
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip())
    key = request.headers.get("X-API-Key","-")
    return f"{ip}|{key}"

def _allowed_ip(ip: str) -> bool:
    if not settings.IP_ALLOWLIST:
        return True
    try:
        ip_obj = ipaddress.ip_address(ip)
        for item in [s.strip() for s in settings.IP_ALLOWLIST.split(",") if s.strip()]:
            net = ipaddress.ip_network(item, strict=False)
            if ip_obj in net: return True
        return False
    except Exception:
        return False

def guard():
    now = time.time()
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip())
    if not _allowed_ip(ip):
        return jsonify({"ok":False,"error":"ip not allowed"}), 403
    rpm = int(settings.RATE_LIMIT_RPM or 120)
    key = _client_id()
    tokens, ts = _BUCKETS.get(key, (rpm, now))
    elapsed = now - ts
    tokens = min(rpm, tokens + elapsed * (rpm/60.0))
    if tokens < 1.0:
        return jsonify({"ok":False,"error":"rate limit"}), 429
    _BUCKETS[key] = (tokens - 1.0, now)
    return None
