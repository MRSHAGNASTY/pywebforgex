
from __future__ import annotations
from flask import Blueprint, jsonify
bp = Blueprint("openapi", __name__)
spec = {
  "openapi":"3.0.3",
  "info":{"title":"Py Forge Omega X API","version":"1.0.0"},
  "paths":{
    "/api/execute":{"post":{"summary":"Execute function","requestBody":{"required":True,"content":{"application/json":{"schema":{"$ref":"#/components/schemas/ExecuteRequest"}}}},"responses":{"200":{"description":"OK"},"4XX":{"description":"Problem+JSON"},"5XX":{"description":"Problem+JSON"}}}},
    "/api/registry":{"get":{"summary":"List registry","responses":{"200":{"description":"OK"}}}},
    "/api/policy":{"get":{"summary":"Get policy"},"post":{"summary":"Set policy (validate)","responses":{"200":{"description":"OK"}}}}
  },
  "components":{"schemas":{"ExecuteRequest":{"type":"object","properties":{"module":{"type":"string"},"function":{"type":"string"},"target":{"type":"string"},"args":{"type":"array"},"kwargs":{"type":"object"},"with_ai":{"type":"boolean"},"mode":{"type":"string"},"timeout_s":{"type":"integer"},"mem_mb":{"type":"integer"},"cpu_s":{"type":"integer"}},"required":["module","function"]}}}
}
@bp.get("/openapi.json")
def get_spec():
    return jsonify(spec)
