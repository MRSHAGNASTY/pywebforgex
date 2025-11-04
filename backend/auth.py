
import os, functools, base64, json
from flask import request, jsonify

def _keys():
    raw = os.environ.get("PYWEBFORGE_KEYS","")
    m = {}
    for pair in raw.split(","):
        if ":" in pair:
            role, key = pair.split(":",1)
            m[key.strip()] = role.strip()
    return m

def _parse_jwt_unverified(tok: str):
    try:
        parts = tok.split(".")
        if len(parts) != 3: return {}
        pad = "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad).decode() or "{}")
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}

def _oidc_from_headers():
    user = request.headers.get("X-User") or request.headers.get("X-Auth-User")
    email = request.headers.get("X-Email") or request.headers.get("X-Auth-Email")
    roles = (request.headers.get("X-Roles") or "").split(",") if request.headers.get("X-Roles") else []
    auth = request.headers.get("Authorization","")
    if auth.startswith("Bearer "):
        claims = _parse_jwt_unverified(auth.split(" ",1)[1])
        user = user or claims.get("preferred_username") or claims.get("name") or claims.get("sub")
        email = email or claims.get("email")
        jwt_roles = claims.get("roles") or claims.get("realm_access",{}).get("roles") or []
        if isinstance(jwt_roles, list) and not roles:
            roles = jwt_roles
    return {"user": user, "email": email, "roles": roles}

def _role_from_sources(oidc_roles, api_key_role):
    rset = {r.lower() for r in (oidc_roles or [])}
    if "admin" in rset or "pywebforge:admin" in rset: return "admin"
    if "editor" in rset or "pywebforge:editor" in rset: return "editor"
    if "viewer" in rset or "pywebforge:viewer" in rset: return "viewer"
    return api_key_role or "viewer"

def current_identity():
    key = request.headers.get("X-API-Key") or request.args.get("api_key")
    api_key_role = _keys().get(key, "viewer") if key else None
    oidc = _oidc_from_headers()
    role = _role_from_sources(oidc.get("roles"), api_key_role)
    tenant = request.headers.get("X-Tenant","public")
    user = oidc.get("user") or request.headers.get("X-User") or "anon"
    return {"user": user, "email": oidc.get("email"), "role": role, "tenant": tenant}

def require_role(min_role="viewer"):
    order = {"viewer":0,"editor":1,"admin":2}
    def deco(fn):
        @functools.wraps(fn)
        def wrap(*a, **k):
            ident = current_identity()
            if order.get(ident["role"],0) < order.get(min_role,0):
                return jsonify({"ok":False,"error":"forbidden","need":min_role}), 403
            return fn(*a, **k)
        return wrap
    return deco
