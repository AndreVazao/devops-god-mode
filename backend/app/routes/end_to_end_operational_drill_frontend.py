from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["e2e-operational-drill-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>E2E Operational Drill</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#581c87,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea,select{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>E2E Operational Drill</h1><p class="muted">Prova o fluxo: APK/chat → job → worker → approval/resume → relatório final.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="project" value="GOD_MODE"><select id="offline"><option value="true">incluir offline bridge</option><option value="false">sem offline bridge</option></select></section>
  <section class="panel"><textarea id="request" rows="4" placeholder="Pedido opcional para o drill"></textarea><div class="buttons"><button id="run" class="good">Correr drill E2E</button><button id="refresh">Atualizar</button><button onclick="location.href='/app/install-readiness'" class="dark">Readiness</button><button onclick="location.href='/app/operator-chat-sync-cards'" class="dark">Chat</button></div></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Provas</h2><div class="grid" id="proof"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let dashboard=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(d){dashboard=d;const r=d.latest_report||d.report||null;qs('#hero').innerHTML=r?`Último: <span class="${esc(r.status||'yellow')}">${esc(r.status)}</span>`:'Sem drill corrido';qs('#cards').innerHTML=r?card('Job',r.job_id||'—',r.final_job_status||'—')+card('Thread',r.thread_id||'—')+card('Blockers',(r.blockers||[]).length)+card('Offline',r.offline_bridge_included?'sim':'não'):card('Estado','sem relatório');const p=r?.proof||{};qs('#proof').innerHTML=Object.keys(p).map(k=>card(k,p[k]?'ok':'não')).join('')||'<p class="muted">Sem provas.</p>';show(d)}async function load(){const d=await api('/api/e2e-operational-drill/dashboard');render(d)}async function run(){const payload={tenant_id:qs('#tenant').value||'owner-andre',project_id:qs('#project').value||'GOD_MODE',request_text:qs('#request').value.trim()||null,include_offline_bridge:qs('#offline').value==='true'};const r=await api('/api/e2e-operational-drill/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});render(r);show(r)}qs('#run').onclick=run;qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/e2e-operational-drill', response_class=HTMLResponse)
async def e2e_operational_drill_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/operational-drill', response_class=HTMLResponse)
async def e2e_operational_drill_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
