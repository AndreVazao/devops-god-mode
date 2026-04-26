from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["operator-priority-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Operator Priority Control</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#312e81,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;font-weight:1000}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}textarea{width:100%;min-height:130px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Operator Priority Control</h1><p class="muted">A ordem dos projetos é tua. Dinheiro é consequência, não prioridade do God Mode.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel"><h2>Ordem dos projetos</h2><p class="muted">Um projeto por linha, pela ordem que queres que o backend respeite.</p><textarea id="order"></textarea><div class="buttons"><button id="save">Guardar ordem</button><button id="refresh">Atualizar</button><button onclick="location.href='/app/operator-chat-sync-cards'" class="dark">Chat</button></div></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);let state=null;async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:20px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}async function load(){const d=await api('/api/operator-priority/priorities');state=d.state||{};const items=state.projects||[];qs('#hero').textContent=`Ativo: ${state.active_project||'—'}`;qs('#order').value=items.map(x=>x.project_id).join('\n');qs('#cards').innerHTML=card('Política',state.policy||'—')+card('Projetos',items.length)+card('Ativo',state.active_project||'—')+card('Money priority','desligado');qs('#out').textContent=JSON.stringify(d,null,2)}async function save(){const ordered=qs('#order').value.split('\n').map(x=>x.trim()).filter(Boolean);const d=await api('/api/operator-priority/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ordered_project_ids:ordered,note:'updated from mobile cockpit'})});qs('#out').textContent=JSON.stringify(d,null,2);await load()}qs('#refresh').onclick=load;qs('#save').onclick=save;load();
</script>
</body></html>
"""


@router.get('/app/operator-priority', response_class=HTMLResponse)
async def operator_priority_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/project-priority', response_class=HTMLResponse)
async def project_priority_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
