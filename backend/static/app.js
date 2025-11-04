
// tabs
document.querySelectorAll("nav button").forEach(btn=>{
  btn.onclick = ()=>{
    document.querySelectorAll("main .tab").forEach(t=> t.style.display="none");
    document.getElementById(btn.dataset.tab).style.display = "";
  };
});

// global fetch adds headers
(function(){
  const keyEl=document.getElementById('apiKey'); const tenEl=document.getElementById('tenant');
  const _f=window.fetch.bind(window);
  window.fetch=(i,init={})=>{ init.headers=init.headers||{}; if(keyEl&&keyEl.value) init.headers['X-API-Key']=keyEl.value; if(tenEl&&tenEl.value) init.headers['X-Tenant']=tenEl.value; return _f(i,init); };
})();

// Upload
document.getElementById("uploadBtn").onclick = async ()=>{
  const f = document.getElementById("zipFile").files[0];
  if(!f){ alert("Choose a zip"); return; }
  const fd = new FormData(); fd.append("file", f);
  const r = await fetch("/api/upload", {method:"POST", body: fd});
  document.getElementById("uploadOut").textContent = await r.text();
};

// Scan
document.getElementById("scanBtn").onclick = async ()=>{
  const r = await fetch("/api/scan", {method:"POST"});
  const j = await r.json(); document.getElementById("scanOut").textContent = JSON.stringify(j, null, 2);
};

// Registry
const helpSig = document.getElementById("helpSig");
const helpDoc = document.getElementById("helpDoc");
const helpArgs = document.getElementById("helpArgs");
const helpKw = document.getElementById("helpKwargs");

async function loadRegistry(){
  const base = document.getElementById("targetBase").value;
  const r = await fetch(`/api/registry?target=${base}`);
  const j = await r.json(); const ul = document.getElementById("funcList");
  ul.innerHTML=""; const reg = j.registry || {};
  Object.entries(reg).forEach(([mod, funcs])=>{
    funcs.forEach(f=>{
      const li = document.createElement("li");
      li.textContent = `${mod} :: ${f.name}(${(f.args||[]).join(", ")})`;
      li.title = (f.doc||"").slice(0,200);
      li.onclick = ()=>{
        document.getElementById("modulePath").value = mod;
        document.getElementById("functionName").value = f.name;
        const targs = (f.args||[]).map(a=>null);
        document.getElementById("argsJson").value = JSON.stringify(targs, null, 2);
        document.getElementById("kwargsJson").value = "{}";
        helpSig.textContent = `${f.name}(${(f.args||[]).join(", ")})`;
        helpDoc.textContent = f.doc || "No docstring.";
        helpArgs.textContent = JSON.stringify(targs, null, 2);
        helpKw.textContent = "{}";
      };
      ul.appendChild(li);
    });
  });
}
document.getElementById("refreshReg").onclick = loadRegistry;
document.getElementById("targetBase").onchange = loadRegistry;

// Input Library
document.getElementById("inputLibrary").onchange = (e)=>{
  const v = e.target.value;
  if(v){
    try{ document.getElementById("argsJson").value = JSON.stringify(JSON.parse(v), null, 2); }
    catch{ document.getElementById("argsJson").value = v; }
  }
};

// Execute
document.getElementById("execBtn").onclick = async ()=>{
  const out = document.getElementById("execOutput");
  let args=[]; let kwargs={};
  try{ const a=document.getElementById("argsJson").value.trim(); if(a) args=JSON.parse(a);}catch(e){ alert("Bad args JSON"); return; }
  try{ const k=document.getElementById("kwargsJson").value.trim(); if(k) kwargs=JSON.parse(k);}catch(e){ alert("Bad kwargs JSON"); return; }
  const mode = (document.querySelector('input[name="mode"]:checked')||{value:'live'}).value;
  const payload = {
    module: document.getElementById("modulePath").value.trim(),
    function: document.getElementById("functionName").value.trim(),
    target: document.getElementById("targetBase").value,
    args, kwargs,
    with_ai: document.getElementById("withAI").checked,
    mode
  };
  const r = await fetch("/api/execute", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload)});
  const j = await r.json(); out.textContent = JSON.stringify(j, null, 2);
};
