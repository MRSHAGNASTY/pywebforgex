import functools, threading, secrets
from flask import request, jsonify
from .settings import API_KEY, CSRF_SECRET, MAX_CONCURRENT_PER_IP
_IP_ACTIVE = {}; _LOCK = threading.Lock()
def require_api_key(fn):
    @functools.wraps(fn)
    def wrapped(*a, **k):
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if key != API_KEY: return jsonify({"success": False, "error": "unauthorized"}), 401
        return fn(*a, **k)
    return wrapped
def require_csrf(fn):
    @functools.wraps(fn)
    def wrapped(*a, **k):
        token = request.headers.get("X-CSRF-Token") or (request.json or {}).get("csrf_token") if request.is_json else request.form.get("csrf_token")
        if not token or not secrets.compare_digest(token, CSRF_SECRET): return jsonify({"success": False, "error": "csrf failed"}), 403
        return fn(*a, **k)
    return wrapped
def rate_limit_concurrent(fn):
    @functools.wraps(fn)
    def wrapped(*a, **k):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
        with _LOCK:
            n = _IP_ACTIVE.get(ip, 0)
            if n >= MAX_CONCURRENT_PER_IP: return jsonify({"success": False, "error": "rate limit"}), 429
            _IP_ACTIVE[ip] = n+1
        try: return fn(*a, **k)
        finally:
            with _LOCK: _IP_ACTIVE[ip] = max(0, _IP_ACTIVE.get(ip, 1)-1)
    return wrapped
