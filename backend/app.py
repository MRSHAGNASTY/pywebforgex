from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from project_forge import scaffold
from openapi import bp as openapi_bp
from models import ExecuteRequest, ExecuteResponse, problem
from logging_mw import before as log_before, after as log_after
from rate_limit import guard as rl_guard
import os, json, zipfile, shutil, time, requests
from pathlib import Path

from db import init_db, get_conn, audit_write, init_audit
from registry import scan_registry
from auth import require_role, current_identity
from executor import call_function
from policy import load_policy, check_allowed
from record_replay import record as rr_record, replay as rr_replay

ROOT = Path(__file__).resolve().parent.parent
SRC_BASE = ROOT/"src_original"
REPAIRED_BASE = ROOT/"repaired_modules"
MUTATED_BASE = ROOT/"mutated_modules"
STORAGE = ROOT/"backend"/"storage"
STORAGE.mkdir(parents=True, exist_ok=True)

HOOK_URL = os.environ.get("PYWEBFORGE_HOOK_URL","")

app = Flask(__name__, static_folder=str(ROOT/"backend"/"static"), static_url_path="/")
from config import settings
CORS(app, origins=settings.origins)
app.register_blueprint(openapi_bp)
app.before_request(log_before)
app.after_request(log_after)

init_db(); init_audit()

def _emit(event: str, payload: dict):
    if not HOOK_URL: return
    try:
        requests.post(HOOK_URL, json={"ts": time.time(), "event": event, **payload}, timeout=2)
    except Exception:
        pass

@app.get("/")
def index():
    return app.send_static_file("index.html")

def _roots(tenant: str):
    src = SRC_BASE/tenant; rep = REPAIRED_BASE/tenant
    src.mkdir(parents=True, exist_ok=True); rep.mkdir(parents=True, exist_ok=True)
    return src, rep

# ---------- Upload / Scan / Repair / Registry ----------

@app.post("/api/upload")
@require_role('editor')
def api_upload():
    ident = current_identity()
    SRC, REPAIRED = _roots(ident['tenant'])
    if 'file' not in request.files:
        return jsonify({"ok": False, "error": "no file"}), 400
    f = request.files['file']
    zpath = STORAGE/"upload.zip"
    f.save(zpath)
    with zipfile.ZipFile(zpath, "r") as z:
        z.extractall(SRC)
    audit_write({'user':ident['user'],'role':ident['role'],'tenant':ident['tenant'],'action':'upload','resource':'src','ok':True,'extra':{'files':len(list(SRC.rglob('*')))}})
    _emit("upload", {"tenant": ident["tenant"], "files": len(list(SRC.rglob('*')))})
    return jsonify({"ok": True, "files": len(list(SRC.rglob('*')))} )

@app.post("/api/scan")
@require_role('viewer')
def api_scan():
    ident = current_identity()
    SRC, REPAIRED = _roots(ident['tenant'])
    report = scan_registry(SRC)
    return jsonify({"ok": True, "report": report})

@app.post("/api/repair")
@require_role('editor')
def api_repair():
    ident = current_identity()
    SRC, REPAIRED = _roots(ident['tenant'])
    # scaffold repair: copy; your AI-repair can be chained here
    if REPAIRED.exists(): shutil.rmtree(REPAIRED, ignore_errors=True)
    shutil.copytree(SRC, REPAIRED, dirs_exist_ok=True)
    audit_write({'user':ident['user'],'role':ident['role'],'tenant':ident['tenant'],'action':'repair','resource':'tree','ok':True})
    _emit("repair", {"tenant": ident["tenant"]})
    return jsonify({"ok": True, "repaired_files": len(list(REPAIRED.rglob('*.py')))} )

@app.get("/api/registry")
@require_role('viewer')
def api_registry():
    ident = current_identity()
    SRC, REPAIRED = _roots(ident['tenant'])
    target = request.args.get("target","repaired")
    root = REPAIRED if target=="repaired" else (MUTATED_BASE if target=="mutated" else SRC)
    reg = scan_registry(root)
    return jsonify({"ok": True, "registry": reg})

@app.post("/api/execute")
@require_role('editor')
def api_execute():
    ident = current_identity()
    SRC, REPAIRED = _roots(ident['tenant'])
    data = request.get_json(force=True) or {}
    req = ExecuteRequest(**data)
    target_base = req.target
    rel_path = req.module; func = req.function
    args = req.args; kwargs = req.kwargs
    mode = (req.mode or "live").lower()
    root = REPAIRED if target_base=="repaired" else (MUTATED_BASE if target_base=="mutated" else SRC)
    module_path = root/rel_path

    # Replay fast-path
    if mode == "replay":
        hit = rr_replay(STORAGE, ident['tenant'], rel_path, func, args, kwargs)
        if hit is not None:
            audit_write({'user':ident['user'],'role':ident['role'],'tenant':ident['tenant'],'action':'execute','resource':rel_path,'ok':hit.get('ok',True),'extra':{'replayed':True}})
            _emit("execute_replay", {"tenant": ident["tenant"], "module": rel_path, "function": func})
            return jsonify({"ok": hit.get("ok", True), "result": hit.get("result"), "advice": hit.get("advice"), "replayed": True})

    # Policy enforcement
    policy = load_policy((ROOT/'policy'/'policy.yaml'))
    allowed, why = check_allowed(policy, rel_path, func)
    if not allowed:
        audit_write({'user':ident['user'],'role':ident['role'],'tenant':ident['tenant'],'action':'execute','resource':rel_path,'ok':False,'extra':{'why':why}})
        return jsonify({'ok':False,'error':why}), 403

    res = call_function(module_path, func, args=args, kwargs=kwargs,
                        with_ai=bool(data.get('with_ai', False)),
                        dry_run=(mode=='dry-run'),
                        timeout_s=int(req.timeout_s), mem_mb=int(req.mem_mb), cpu_s=int(req.cpu_s))
    audit_write({'user':ident['user'],'role':ident['role'],'tenant':ident['tenant'],'action':'execute','resource':rel_path,'ok':res.get('ok',False),'extra':{'function':func,'mode':mode}})
    _emit("execute", {"tenant": ident["tenant"], "module": rel_path, "function": func, "ok": bool(res.get("ok"))})

    if mode == "record":
        try: rr_record(STORAGE, ident['tenant'], rel_path, func, args, kwargs, res)
        except Exception: pass
    return jsonify(res)

# -------- Packaging (downloadable) --------
@app.get("/api/package")
@require_role('viewer')
def api_package():
    zip_path = STORAGE/"enterprise_package.zip"
    if zip_path.exists(): os.remove(zip_path)
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for rd,_,files in os.walk(ROOT):
            for f in files:
                p = Path(rd)/f
                # avoid bundling sqlite db files
                if "/storage/" in str(p).replace("\\","/"): 
                    continue
                z.write(p, str(p.relative_to(ROOT)))
    return send_from_directory(str(STORAGE), "enterprise_package.zip", as_attachment=True)

# Static assets
@app.get("/<path:fname>")
def static_files(fname):
    return app.send_static_file(fname)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)


@app.get("/api/policy")
@require_role('admin')
def get_policy():
    from pathlib import Path
    pol_path = ROOT/'policy'/'policy.json'
    try:
        import json
        return jsonify(json.loads(pol_path.read_text()))
    except Exception:
        return jsonify({"allow":{"modules":[],"functions":[]}})

@app.post("/api/policy")
@require_role('admin')
def set_policy():
    guard = rl_guard()
    if guard:
        return guard
    raw = request.get_data(as_text=True)
    try:
        import json
        data = json.loads(raw)
        from policy import Policy
        Policy.model_validate(data)  # validate
        (ROOT/'policy'/'policy.json').write_text(json.dumps(data, indent=2))
        return jsonify({"ok": True})
    except Exception as e:
        from models import problem
        return jsonify(problem(400, "invalid policy", repr(e))), 400


@app.post("/api/forge")
@require_role('editor')
def api_forge():
    guard = rl_guard()
    if guard:
        return guard
    data = request.get_json(force=True) or {}
    kind = data.get("kind","flask-app"); name = data.get("name","sample")
    dest = (SRC_BASE/current_identity()['tenant'])
    res = scaffold(dest, kind, name)
    return jsonify(res)


@app.post("/api/forge/pack")
@require_role('editor')
def api_forge_pack():
    guard = rl_guard()
    if guard:
        return guard
    data = request.get_json(force=True) or {}
    pack = data.get("pack","fastapi-app"); name = data.get("name","sample-pack")
    dest = (SRC_BASE/current_identity()['tenant'])
    from project_forge import scaffold_pack
    res = scaffold_pack(dest, pack, name)
    return jsonify(res)


@app.post("/api/policy/generate")
@require_role('admin')
def api_policy_generate():
    guard = rl_guard()
    if guard:
        return guard
    tenant = current_identity()['tenant']
    # prefer repaired tree if exists, fallback to original
    src, rep = _roots(tenant)
    root = rep if any(rep.rglob("*.py")) else src
    reg = scan_registry(root)
    modules = list(reg.keys())
    funcs = sorted({f["name"] for arr in reg.values() for f in arr})
    pol = {"allow":{"modules": modules, "functions": funcs}}
    (ROOT/'policy'/'policy.json').write_text(json.dumps(pol, indent=2))
    return jsonify({"ok":True,"policy":pol,"source":"repaired" if root==rep else "original"})
