import os, subprocess, shlex, tempfile, re
from flask import Blueprint, request, jsonify, Response, stream_with_context
from ..core.environment import ensure_env_for_project, destroy_env_for_project
from ..core.sandbox import _venv_bin
from ..core.packager import zipdir
from ..core.limits import make_preexec, kill_tree, clamp_output
from ..core.jail import create_run_jail, cleanup_run_jail
from ..core.settings import RUNTIME_ALLOW_NETWORK, CPU_SECS_DEFAULT, MEM_MB_DEFAULT
from ..core.security import require_api_key, require_csrf, rate_limit_concurrent
from ..core.audit_sbom import build_sbom
sandbox_cli=Blueprint("sandbox_cli",__name__)
ALLOW_CMDS=[r"^python(\s|$)",r"^pytest(\s|$)",r"^pip(\s|$)",r"^uvicorn(\s|$)",r"^gunicorn(\s|$)",r"^flask(\s|$)"]
ALLOW_RE=[re.compile(p) for p in ALLOW_CMDS]
def _allowed(cmd:str)->bool:
    try: first=shlex.split(cmd)[0]
    except Exception: return False
    return any(rx.match(first) for rx in ALLOW_RE)
def _map_entry(env_path:str, parts:list):
    exe=parts[0]
    if exe=="python":
        parts[0]=_venv_bin(env_path,"python"); return parts
    if exe in ("pip","pytest","flask","uvicorn","gunicorn"):
        cand=_venv_bin(env_path,exe)
        if os.path.exists(cand): parts[0]=cand
        else: parts[:]=[_venv_bin(env_path,"python"),"-m",exe,*parts[1:]]
    return parts
@sandbox_cli.post("/sandbox/exec")
@require_api_key
@require_csrf
@rate_limit_concurrent
def sandbox_exec():
    data=request.json or {}; project=data.get("project"); cmd=data.get("cmd")
    timeout=int(data.get("timeout",60))
    allow_network=bool(data.get("allow_network", RUNTIME_ALLOW_NETWORK))
    cpu=int(data.get("cpu_secs", CPU_SECS_DEFAULT)); mem=int(data.get("mem_mb", MEM_MB_DEFAULT))
    if not (project and cmd): return jsonify({"success":False,"error":"project and cmd required"}),400
    if not _allowed(cmd): return jsonify({"success":False,"error":"command not allowed"}),403
    env_path=ensure_env_for_project(project, allow_network=allow_network)
    base,src,out=create_run_jail(project)
    parts=_map_entry(env_path, shlex.split(cmd)); preexec=make_preexec(max_cpu_secs=cpu, max_mem_mb=mem)
    proc=subprocess.Popen(parts, cwd=src, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=preexec)
    try: stdout,stderr=proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_tree(proc.pid); cleanup_run_jail(base); return jsonify({"success":False,"error":"execution timed out"}),408
    stdout=clamp_output(stdout); stderr=clamp_output(stderr); cleanup_run_jail(base)
    return jsonify({"success":proc.returncode==0,"stdout":stdout,"stderr":stderr,"returncode":proc.returncode})
@sandbox_cli.get("/sandbox/exec_stream")
@require_api_key
@rate_limit_concurrent
def sandbox_exec_stream():
    project=request.args.get("project"); cmd=request.args.get("cmd")
    allow_network=(request.args.get("allow_network","0")=="1") or RUNTIME_ALLOW_NETWORK
    cpu=int(request.args.get("cpu_secs", str(CPU_SECS_DEFAULT))); mem=int(request.args.get("mem_mb", str(MEM_MB_DEFAULT)))
    if not (project and cmd): return jsonify({"success":False,"error":"project and cmd required"}),400
    if not _allowed(cmd): return jsonify({"success":False,"error":"command not allowed"}),403
    env_path=ensure_env_for_project(project, allow_network=allow_network)
    base,src,out=create_run_jail(project)
    parts=_map_entry(env_path, shlex.split(cmd)); preexec=make_preexec(max_cpu_secs=cpu, max_mem_mb=mem)
    def generate():
        proc=subprocess.Popen(parts, cwd=src, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, preexec_fn=preexec)
        try:
            for line in iter(proc.stdout.readline, ''): yield f"data: {line.rstrip()}\n\n"
            proc.wait(); yield f"data: <<exit {proc.returncode}>>\n\n"
        finally: cleanup_run_jail(base)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
@sandbox_cli.post("/sandbox/package")
@require_api_key
@require_csrf
def sandbox_package():
    data=request.json or {}; project=data.get("project"); out_name=data.get("name") or "pywebforge_ready_build.zip"
    if not project: return jsonify({"success":False,"error":"project required"}),400
    out_path=os.path.join(tempfile.gettempdir(), out_name); zipdir(project,out_path)
    return jsonify({"success":True,"zip_path":out_path})
@sandbox_cli.post("/sandbox/package_and_destroy")
@require_api_key
@require_csrf
def sandbox_package_and_destroy():
    data=request.json or {}; project=data.get("project"); out_name=data.get("name") or "pywebforge_ready_build.zip"
    if not project: return jsonify({"success":False,"error":"project required"}),400
    out_path=os.path.join(tempfile.gettempdir(), out_name)
    venv_path=ensure_env_for_project(project, allow_network=True)
    try:
        sbom=build_sbom(venv_path, project); import json as _json
        build_info=os.path.join(project,"BUILD_INFO.json")
        with open(build_info,"w",encoding="utf-8") as f: _json.dump(sbom,f,indent=2)
    except Exception: pass
    zipdir(project,out_path); destroyed=destroy_env_for_project(project)
    return jsonify({"success":True,"zip_path":out_path,"destroyed":destroyed,"message":"Thanks for using PyWebForge!"})
