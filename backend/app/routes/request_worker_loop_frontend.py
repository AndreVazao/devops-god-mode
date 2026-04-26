from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["request-worker-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Request Worker Loop</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#1e1b4b,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Request Worker Loop</h1><p class="muted">Processa jobs pendentes no backend, mesmo que o APK já tenha desligado.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="ticks" type="number" min="1" max="25" value="3"><input id="max" type="number" min="1" max="50" value="5"></section>
  <section class="panel buttons"><button id="tick" class="good">Processar agora</button><button id="run">Correr ciclos</button><button id="refresh" class="dark">Atualizar</button><button onclick="location.href='/app/request-orchestrator'" class="dark">Ver jobs</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Últimos ticks</h2><div class="grid" id="ticksView"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let dashboard=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(d){dashboard=d;const st=d.status||{};qs('#hero').textContent=`${st.runnable_count||0} jobs executáveis · ${st.blocked_count||0} bloqueados`;qs('#cards').innerHTML=card('Executáveis',st.runnable_count||0)+card('Bloqueados',st.blocked_count||0)+card('Concluídos',st.completed_count||0)+card('Ticks',st.tick_count||0);qs('#ticksView').innerHTML=(d.recent_ticks||[]).slice().reverse().slice(0,8).map(t=>card(t.status||'tick',`${t.processed_count||0} processados`,`${t.blocked_count||0} bloqueados · ${t.completed_count||0} concluídos`)).join('')||'<p class="muted">Sem ticks.</p>';show(d)}async function load(){const t=encodeURIComponent(qs('#tenant').value||'owner-andre');render(await api(`/api/request-worker/dashboard?tenant_id=${t}`))}async function doTick(){const payload={tenant_id:qs('#tenant').value||'owner-andre',max_jobs:Number(qs('#max').value||5)};show(await api('/api/request-worker/tick',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));await load()}async function doRun(){const payload={tenant_id:qs('#tenant').value||'owner-andre',ticks:Number(qs('#ticks').value||3),max_jobs_per_tick:Number(qs('#max').value||5)};show(await api('/api/request-worker/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));await load()}qs('#tick').onclick=doTick;qs('#run').onclick=doRun;qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/request-worker', response_class=HTMLResponse)
async def request_worker_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
