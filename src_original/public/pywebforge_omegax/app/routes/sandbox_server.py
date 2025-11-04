import os, socket, subprocess, shlex, threading
from flask import Blueprint, request, jsonify, Response, stream_with_context
import requests
from ..core.environment import ensure_env_for_project
from ..core.sandbox import _venv_bin
from ..core.limits import make_preexec, kill_tree
from ..core.security import require_api_key, rate_limit_concurrent
from ..core.settings import CPU_SECS_DEFAULT, MEM_MB_DEFAULT
sandbox_server=Blueprint("sandbox_server", __name__); RUNNING={}
def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]
@sandbox_server.post("/sandbox/run_server")
@require_api_key
@rate_limit_concurrent
def run_server():
    data=request.json or {}; project=data.get("project"); cmd=data.get("cmd")
    cpu=int(data.get("cpu_secs", CPU_SECS_DEFAULT)); mem=int(data.get("mem_mb", MEM_MB_DEFAULT))
    if not (project and cmd): return jsonify({"success":False,"error":"project and cmd required"}),400
    if project in RUNNING: return jsonify({"success":True,"port":RUNNING[project]["port"],"pid":RUNNING[project]["pid"],"already":True})
    env_path=ensure_env_for_project(project, allow_network=True)
    port=_find_free_port(); cmd=cmd.replace("{port}",str(port)).replace("$PORT",str(port))
    parts=shlex.split(cmd)
    if parts and parts[0] in ("python","uvicorn","gunicorn","flask"):
        exe=parts[0]; parts[0]=_venv_bin(env_path, exe)
        if not os.path.exists(parts[0]) and exe!="python": parts=[_venv_bin(env_path,"python"),"-m",exe,*parts[1:]]
    preexec=make_preexec(max_cpu_secs=cpu, max_mem_mb=mem)
    proc=subprocess.Popen(parts, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=preexec)
    def _drain(p):
        try: p.communicate()
        except Exception: pass
    threading.Thread(target=_drain, args=(proc,), daemon=True).start()
    RUNNING[project]={"pid":proc.pid,"port":port}; return jsonify({"success":True,"port":port,"pid":proc.pid})
@sandbox_server.post("/sandbox/stop_server")
@require_api_key
def stop_server():
    data=request.json or {}; project=data.get("project"); info=RUNNING.get(project)
    if not info: return jsonify({"success":True,"stopped":False})
    try: kill_tree(info["pid"])
    except Exception: pass
    RUNNING.pop(project, None); return jsonify({"success":True,"stopped":True})
@sandbox_server.get("/sandbox/server_status")
@require_api_key
def server_status():
    project=request.args.get("project"); return jsonify({"success":True,"running": project in RUNNING, "info": RUNNING.get(project)})
@sandbox_server.route("/sandbox/proxy/", defaults={"path": ""}, methods=["GET","POST","PUT","PATCH","DELETE"])
@sandbox_server.route("/sandbox/proxy/<path:path>", methods=["GET","POST","PUT","PATCH","DELETE"])
@require_api_key
def proxy(path):
    project=request.args.get("project"); info=RUNNING.get(project)
    if not info: return Response("Server not running", status=502)
    url=f"http://127.0.0.1:{info['port']}/{path}"; method=request.method
    headers={k:v for k,v in request.headers if k.lower() not in ("host","content-length")}
    try:
        resp=requests.request(method, url, params=request.args, data=request.get_data(), headers=headers, stream=True, allow_redirects=False)
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk: yield chunk
        excluded=["content-encoding","transfer-encoding","connection"]
        h=[(k,v) for k,v in resp.raw.headers.items() if k.lower() not in excluded]
        return Response(stream_with_context(generate()), status=resp.status_code, headers=h)
    except Exception as e:
        return Response(f"Proxy error: {e}", status=502)
