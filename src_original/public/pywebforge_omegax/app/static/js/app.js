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
  const res = await fetch('/api/files/upload', { method: 'POST', body: fd });
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
  const res = await fetch('/api/files/read', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p}) });
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
  const res = await fetch('/api/files/save', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p, content}) });
  const j = await res.json();
  log(j.success ? 'Saved.' : ('Save error: ' + j.error));
};

document.getElementById('btnAnalyze').onclick = async () => {
  const p = document.getElementById('pathField').value;
  const res = await fetch('/api/files/read', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path:p}) });
  const j = await res.json();
  if(j.success){
    document.getElementById('analysisOut').textContent = JSON.stringify(j.analysis, null, 2);
    log('Analysis done.');
  }
};

document.getElementById('btnAI').onclick = async () => {
  const prompt = document.getElementById('aiInput').value;
  const res = await fetch('/api/ai/query', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prompt}) });
  const j = await res.json();
  log(j.success ? ('AI: ' + j.response) : ('AI error: ' + j.error));
};

document.getElementById('btnBuild').onclick = async () => {
  const proj = document.getElementById('projectPath').textContent.trim();
  if(!proj) return alert('Upload a project or set a path');
  const res = await fetch('/api/build/orchestrate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
  const j = await res.json();
  log(j.success ? ('Build: ' + JSON.stringify(j.result)) : ('Build error: ' + j.error));
};

document.getElementById('btnAutoDoc').onclick = async () => {
  const proj = document.getElementById('projectPath').textContent.trim();
  if(!proj) return alert('Upload a project or set a path');
  const res = await fetch('/api/docs/autodoc', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
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
  const res = await fetch('/api/graphs/deps', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path: proj}) });
  const j = await res.json();
  if(!j.success) return log('Graph error: ' + j.error);
  const g = j.graph;
  // simple d3 force-directed graph
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
  const res = await fetch('/api/plugins/list');
  const j = await res.json();
  document.getElementById('pluginsOut').textContent = JSON.stringify(j, null, 2);
};

document.getElementById('btnRunUpper').onclick = async () => {
  const res = await fetch('/api/plugins/run', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:"uppercase", kwargs:{text:"forge me"}}) });
  const j = await res.json();
  document.getElementById('pluginsOut').textContent = JSON.stringify(j, null, 2);
};
(function(){
  function token(h){ return document.querySelector(`meta[name="${h}"]`)?.content || ""; }
  function getProjectRoot(){ const el=document.getElementById('projectPath')||document.getElementById('project'); return el? el.value.trim(): (window.projectRoot||''); }
  function getCurrentFile(){ const el=document.getElementById('filePath')||document.querySelector('[data-current-file]'); return el? el.value.trim(): (window.editor&&window.editor.currentFilePath)||''; }
  async function postJSON(url, body){ return fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':token('x-api-key'),'X-CSRF-Token':token('x-csrf')},body:JSON.stringify(body||{})}); }
  function openAutoUI(){ const proj=getProjectRoot(), file=getCurrentFile(); if(!proj||!file||!file.endsWith('.py')){ alert('Set project path and open a Python file.'); return; } window.open(`/api/auto_ui/${file}?project=${encodeURIComponent(proj)}`,'_blank'); }
  function openCLI(){ window.open('/cli.html','_blank'); }
  async function packageAndDownload(){ const proj=getProjectRoot(); if(!proj){alert('Set project path first.');return;} const name='pywebforge_ready_build.zip'; const r=await postJSON('/api/sandbox/package_and_destroy',{project:proj,name}); const j=await r.json(); if(!j.success){alert('Package failed: '+(j.error||'unknown'));return;} const a=document.createElement('a'); a.href=`/download?path=${encodeURIComponent(j.zip_path)}`; a.download=name; document.body.appendChild(a); a.click(); document.body.removeChild(a); alert(j.message||'Packaged and sandbox destroyed. Thanks for using PyWebForge!'); }
  async function classifyAndRoute(){ const proj=getProjectRoot(); if(!proj) return; try{ const r=await postJSON('/api/analyze/classify_project',{project:proj}); const j=await r.json(); if(!j.success) return; if(j.mode==='web'){ const file=getCurrentFile()||'app/server.py'; window.open(`/api/auto_ui/${file}?project=${encodeURIComponent(proj)}`,'_blank'); } else if(j.mode==='cli'){ window.open('/cli.html','_blank'); } }catch(e){} }
  async function startPreview(){ const proj=getProjectRoot(); if(!proj){alert('Set project path first.');return;} const cmd='uvicorn app.main:app --host 127.0.0.1 --port {port}'; const r=await postJSON('/api/sandbox/run_server',{project:proj,cmd,allow_network:true,cpu_secs:180,mem_mb:768}); const j=await r.json(); if(!j.success){alert('Failed to start server: '+(j.error||'unknown'));return;} const url=`/api/sandbox/proxy/?project=${encodeURIComponent(proj)}`; window.open(url,'_blank'); }
  const autoBtn=document.getElementById('openAutoUiBtn'); const cliBtn=document.getElementById('openCliBtn'); const pkgBtn=document.getElementById('packageBtn'); const prevBtn=document.getElementById('previewBtn');
  if(autoBtn) autoBtn.onclick=openAutoUI; if(cliBtn) cliBtn.onclick=openCLI; if(pkgBtn) pkgBtn.onclick=packageAndDownload; if(prevBtn) prevBtn.onclick=startPreview;
  const analyzeBtn=document.getElementById('btnAnalyze'); if(analyzeBtn){ const old=analyzeBtn.onclick; analyzeBtn.onclick=async function(){ if(typeof old==='function'){ try{ await old(); }catch(e){} } setTimeout(classifyAndRoute, 500); }; }
})();