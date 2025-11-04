#!/usr/bin/env python3
import os, re, sys, shutil
from pathlib import Path

ROOT = Path.cwd()

SERVER = ROOT / "src_original/public/pywebforge_omegax/app/server.py"
APPJS  = ROOT / "src_original/public/pywebforge_omegax/app/static/js/app.js"
INDEX  = ROOT / "src_original/public/pywebforge_omegax/app/templates/index.html"
REQS   = ROOT / "requirements.txt"
GITIGNORE = ROOT / ".gitignore"
CFG_EXAMPLE = ROOT / "config.js.example"
ENV_EXAMPLE = ROOT / ".env.example"

def backup_once(p: Path):
    if p.exists():
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(p, bak)

def ensure_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

# --- 1) server.py: replace CORS(app) with env-driven CORS block ---
def patch_server():
    if not SERVER.exists():
        print(f"[WARN] server.py not found: {SERVER}")
        return
    src = ensure_text(SERVER)
    if "ALLOWED_ORIGINS" in src and "resources={r\"/api/*\"" in src:
        print("[OK] server.py already patched")
        return
    backup_once(SERVER)

    # Make sure import present (it is, but ensure os is there)
    if "from flask_cors import CORS" not in src:
        src = src.replace("from flask import Flask, render_template, send_file, jsonify",
                          "from flask import Flask, render_template, send_file, jsonify\nfrom flask_cors import CORS")

    # Replace CORS(app) call with env-driven block
    pattern = r"CORS\(\s*app\s*\)"
    cors_block = (
        "allowed = [o.strip() for o in os.getenv(\"ALLOWED_ORIGINS\", \"\").split(\",\") if o.strip()]\n"
        "    allow_creds = os.getenv(\"CORS_CREDENTIALS\", \"false\").lower() == \"true\"\n"
        "    CORS(\n"
        "        app,\n"
        "        resources={r\"/api/*\": {\"origins\": allowed or \"*\"}},\n"
        "        supports_credentials=allow_creds,\n"
        "        methods=[\"GET\",\"POST\",\"PUT\",\"PATCH\",\"DELETE\",\"OPTIONS\"],\n"
        "        allow_headers=[\"Content-Type\",\"Authorization\",\"X-Requested-With\"],\n"
        "    )"
    )
    if re.search(pattern, src):
        src = re.sub(pattern, cors_block, src, count=1)
    else:
        # fallback: insert after logger setLevel
        src = src.replace(
            "app.logger.setLevel(logging.INFO)",
            "app.logger.setLevel(logging.INFO)\n    " + cors_block
        )
    write_text(SERVER, src)
    print("[EDIT] server.py → env-driven CORS applied")

# --- 2) app.js: replace entirely with API_BASE-aware version ---
APP_JS_NEW = r"""// Backend base URL injected via /config.js on Hostinger
// In public_html/config.js, set:  window.API_BASE="https://pywebforgex.onrender.com";
const API_BASE = (window.API_BASE || '');

let editor;
require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.51.0/min/vs' } });
require(['vs/editor/editor.main'], function() {
  editor = monaco.editor.create(document.getElementById('editor'), {
    value: '# PyWebForge ΩX — editor ready\n',
    language: 'python',
    theme: 'vs-dark',
    automaticLayout: true
  });
});

function log(s){
  const el = document.getElementById('console');
  el.textContent += "\n" + s;
  el.scrollTop = el.scrollHeight;
}

document.getElementById('btnUpload').onclick = async () => {
  const f = document.getElementById('fileInput').files[0];
  if(!f){ return alert('Choose a file'); }
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch(`${API_BASE}/api/files/upload`, { method: 'POST', body: fd });
  const j = await res.json();
  if(j.success){
    document.getElementById('projectPath').textContent = j.path;
    log('Uploaded: ' + j.path);
  } else {
    log('Upload error: ' + (j.error||'unknown'));
  }
};

document.getElementById('btnRead').onclick = async () => {
  const p = document.getElementById('pathField').value;
  const res = await fetch(`${API_BASE}/api/files/read`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p}) });
  const j = await res.json();
  if(j.success){
    editor.setValue(j.content);
    document.getElementById('analysisOut').textContent = JSON.stringify(j.analysis, null, 2);
    log('Loaded file: ' + p);
  } else { log('Read error: ' + (j.error||'unknown')); }
};

document.getElementById('btnSave').onclick = async () => {
  const p = document.getElementById('pathField').value;
  const content = editor.getValue();
  const res = await fetch(`${API_BASE}/api/files/save`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p, content}) });
  const j = await res.json();
  log(j.success ? 'Saved.' : ('Save error: ' + j.error));
};

document.getElementById('btnAnalyze').onclick = async () => {
  const p = document.getElementById('pathField').value;
  const res = await fetch(`${API_BASE}/api/files/read`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p}) });
  const j = await res.json();
  if(j.success){
    document.getElementById('analysisOut').textContent = JSON.stringify(j.analysis, null, 2);
    log('Analysis done.');
  }
};

document.getElementById('btnAI').onclick = async () => {
  const prompt = document.getElementById('aiInput').value;
  const res = await fetch(`${API_BASE}/api/ai/query`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prompt}) });
  const j = await res.json();
  log(j.success ? ('AI: ' + j.response) : ('AI error: ' + j.error));
};

document.getElementById('btnBuild').onclick = async () => {
  const proj = document.getElementById('projectPath').textContent.trim();
  if(!proj) return alert('Upload a project or set a path');
  const res = await fetch(`${API_BASE}/api/build/orchestrate`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
  const j = await res.json();
  log(j.success ? ('Build: ' + JSON.stringify(j.result)) : ('Build error: ' + j.error));
};

document.getElementById('btnAutoDoc').onclick = async () => {
  const proj = document.getElementById('projectPath').textContent.trim();
  if(!proj) return alert('Upload a project or set a path');
  const res = await fetch(`${API_BASE}/api/docs/autodoc`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
  const j = await res.json();
  if(j.success){
    log('AutoDoc ready (markdown length ' + j.markdown.length + ')');
  } else {
    log('AutoDoc error: ' + j.error);
  }
};

document.getElementById('btnGraph').onclick = async () => {
  const proj = document.getElementById('projectPath').textContent.trim();
  if(!proj) return alert('Upload a project or set a path');
  const res = await fetch(`${API_BASE}/api/graphs/deps`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
  const j = await res.json();
  if(!j.success) return log('Graph error: ' + j.error);
  const g = j.graph;
  const svg = d3.select('#graph').html('').append('svg');
  const width = document.getElementById('graph').clientWidth;
  const height = 340;
  const link = svg.selectAll('line').data(g.edges).enter().append('line');
  const node = svg.selectAll('circle').data(g.nodes).enter().append('circle').attr('r', 5);
  const label = svg.selectAll('text').data(g.nodes).enter().append('text').text(d=>d).attr('font-size', 8).attr('fill','#9fb3ff');

  const sim = d3.forceSimulation(g.nodes)
    .force('link', d3.forceLink(g.edges).id(d=>d).distance(60))
    .force('charge', d3.forceManyBody().strength(-80))
    .force('center', d3.forceCenter(width/2, height/2));

  sim.on('tick', ()=>{
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y).attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('cx', d=>d.x).attr('cy', d=>d.y).attr('fill', '#5b8def');
    label.attr('x', d=>d.x+6).attr('y', d=>d.y+3);
  });
};

document.getElementById('btnListPlugins').onclick = async () => {
  const res = await fetch(`${API_BASE}/api/plugins/list`);
  const j = await res.json();
  document.getElementById('pluginsOut').textContent = JSON.stringify(j, null, 2);
};

document.getElementById('btnRunUpper').onclick = async () => {
  const res = await fetch(`${API_BASE}/api/plugins/run`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:"uppercase", kwargs:{text:"forge me"}}) });
  const j = await res.json();
  document.getElementById('pluginsOut').textContent = JSON.stringify(j, null, 2);
};

(function(){
  function token(h){ return document.querySelector(`meta[name="${h}"]`)?.content || ""; }
  function getProjectRoot(){ const el=document.getElementById('projectPath')||document.getElementById('project'); return el? el.value.trim(): (window.projectRoot||''); }
  function getCurrentFile(){ const el=document.getElementById('filePath')||document.querySelector('[data-current-file]'); return el? el.value.trim(): (window.editor&&window.editor.currentFilePath)||''; }
  async function postJSON(url, body){
    const full = url.startsWith('/api') ? `${API_BASE}${url}` : url;
    return fetch(full,{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':token('x-api-key'),'X-CSRF-Token':token('x-csrf')},body:JSON.stringify(body||{})});
  }
  function openAutoUI(){ const proj=getProjectRoot(), file=getCurrentFile(); if(!proj||!file||!file.endsWith('.py')){ alert('Set project path and open a Python file.'); return; } window.open(`${API_BASE}/api/auto_ui/${file}?project=${encodeURIComponent(proj)}`,'_blank'); }
  function openCLI(){ window.open('/cli.html','_blank'); }
  async function packageAndDownload(){ const proj=getProjectRoot(); if(!proj){alert('Set project path first.');return;} const name='pywebforge_ready_build.zip'; const r=await postJSON('/api/sandbox/package_and_destroy',{project:proj,name}); const j=await r.json(); if(!j.success){alert('Package failed: '+(j.error||'unknown'));return;} const a=document.createElement('a'); a.href=`${API_BASE}/download?path=${encodeURIComponent(j.zip_path)}`; a.download=name; document.body.appendChild(a); a.click(); document.body.removeChild(a); alert(j.message||'Packaged and sandbox destroyed. Thanks for using PyWebForge!'); }
  async function classifyAndRoute(){ const proj=getProjectRoot(); if(!proj) return; try{ const r=await postJSON('/api/analyze/classify_project',{project:proj}); const j=await r.json(); if(!j.success) return; if(j.mode==='web'){ const file=getCurrentFile()||'app/server.py'; window.open(`${API_BASE}/api/auto_ui/${file}?project=${encodeURIComponent(proj)}`,'_blank'); } else if(j.mode==='cli'){ window.open('/cli.html','_blank'); } }catch(e){} }
  async function startPreview(){ const proj=getProjectRoot(); if(!proj){alert('Set project path first.');return;} const cmd='uvicorn app.main:app --host 127.0.0.1 --port {port}'; const r=await postJSON('/api/sandbox/run_server',{project:proj,cmd,allow_network:true,cpu_secs:180,mem_mb:768}); const j=await r.json(); if(!j.success){alert('Failed to start server: '+(j.error||'unknown'));return;} const url=`${API_BASE}/api/sandbox/proxy/?project=${encodeURIComponent(proj)}`; window.open(url,'_blank'); }
  const autoBtn=document.getElementById('openAutoUiBtn'); const cliBtn=document.getElementById('openCliBtn'); const pkgBtn=document.getElementById('packageBtn'); const prevBtn=document.getElementById('previewBtn');
  if(autoBtn) autoBtn.onclick=openAutoUI; if(cliBtn) cliBtn.onclick=openCLI; if(pkgBtn) pkgBtn.onclick=packageAndDownload; if(prevBtn) prevBtn.onclick=startPreview;
  const analyzeBtn=document.getElementById('btnAnalyze'); if(analyzeBtn){ const old=analyzeBtn.onclick; analyzeBtn.onclick=async function(){ if(typeof old==='function'){ try{ await old(); }catch(e){} } setTimeout(classifyAndRoute, 500); }; }
})();
"""

def patch_appjs():
    if not APPJS.exists():
        print(f"[WARN] app.js not found: {APPJS}")
        return
    src = ensure_text(APPJS)
    if "const API_BASE = (window.API_BASE || '')" in src or 'const API_BASE = (window.API_BASE || \'\')' in src:
        print("[OK] app.js already patched (API_BASE present)")
        return
    backup_once(APPJS)
    write_text(APPJS, APP_JS_NEW)
    print("[EDIT] app.js replaced with API_BASE-aware version")

# --- 3) index.html: insert config.js before app.js; fix duplicate ids ---
def patch_index():
    if not INDEX.exists():
        print(f"[WARN] index.html not found: {INDEX}")
        return
    src = ensure_text(INDEX)
    backup_once(INDEX)

    # Ensure <script src="/config.js"></script> before app.js
    if '/config.js' not in src:
        src = src.replace(
            '<script src="/static/js/app.js"></script>',
            '<script src="/config.js"></script>\n<script src="/static/js/app.js"></script>'
        )

    # Fix duplicate id: change the input with id="projectPath" to id="project"
    src = src.replace('<input id="projectPath"', '<input id="project"')

    write_text(INDEX, src)
    print("[EDIT] index.html updated (config.js & id fix)")

# --- 4) requirements.txt: ensure flask-sock present ---
def patch_requirements():
    if not REQS.exists():
        print(f"[WARN] requirements.txt not found: {REQS}")
        return
    txt = ensure_text(REQS)
    if re.search(r'(?im)^flask-?sock\s*$', txt):
        print("[OK] requirements.txt already has flask-sock")
        return
    backup_once(REQS)
    txt = txt.rstrip() + "\nflask-sock\n"
    write_text(REQS, txt)
    print("[EDIT] requirements.txt → added flask-sock")

# --- 5) config.js.example & .env.example ---
def create_examples():
    if not CFG_EXAMPLE.exists():
        write_text(CFG_EXAMPLE, 'window.API_BASE="https://pywebforgex.onrender.com";\n')
        print("[ADD] config.js.example created")
    else:
        print("[OK] config.js.example exists")

    env_body = """# Render environment (example — do not commit real secrets)
ALLOWED_ORIGINS=https://covenant-firm.com
CORS_CREDENTIALS=false
PYWEBFORGE_SECRET=CHANGE_ME
PWF_CSRF_SECRET=CHANGE_ME
PWF_API_KEY=pwf_live_R4p2nZK3s7YqB8u1X9cD5tL0JmHeWaQv
# OPENAI_API_KEY=
# OLLAMA_HOST=
"""
    if not ENV_EXAMPLE.exists():
        write_text(ENV_EXAMPLE, env_body)
        print("[ADD] .env.example created")
    else:
        print("[OK] .env.example exists")

# --- 6) .gitignore additions ---
def patch_gitignore():
    ig = ensure_text(GITIGNORE)
    add = []
    if "config.js" not in ig:
        add.append("config.js")
    if ".env" not in ig:
        add.append(".env")
    if ".env." not in ig:
        add.append(".env.*")
    if add:
        backup_once(GITIGNORE)
        ig = (ig + "\n" if ig else "") + "\n".join(add) + "\n"
        write_text(GITIGNORE, ig)
        print("[EDIT] .gitignore updated:", ", ".join(add))
    else:
        print("[OK] .gitignore already covers config.js and envs")

def main():
    patch_server()
    patch_appjs()
    patch_index()
    patch_requirements()
    create_examples()
    patch_gitignore()
    print("\nAll edits applied. Review backups (*.bak) if needed.")

if __name__ == "__main__":
    main()
