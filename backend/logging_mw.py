
from __future__ import annotations
import time, json, uuid
from flask import request, g

def before():
    g.req_id = str(uuid.uuid4())
    g.t0 = time.time()

def after(response):
    try:
        duration = time.time() - getattr(g, "t0", time.time())
        meta = {
            "req_id": getattr(g,"req_id","-"),
            "path": request.path,
            "method": request.method,
            "tenant": request.headers.get("X-Tenant","public"),
            "status": response.status_code,
            "duration_ms": int(duration*1000),
        }
        print(json.dumps({"log":"access","meta":meta}))
    except Exception:
        pass
    return response
