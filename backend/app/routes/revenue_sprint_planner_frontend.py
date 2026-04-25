from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["revenue-sprint-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Revenue Sprint Planner</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#fb7185;--ok:#22c55e;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#210712,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}button,input{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#e11d48,#fb7185);border:none;font-weight:900}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}pre{white-space:pre-wrap;overflow:auto;font-size:12px}@media(max-width:720px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Revenue Sprint Planner</h1><p class="muted">Transforma a matriz de monetização em sprint curto com cartão de aprovação.</p></section>
  <section class="panel row"><input id="max" type="number" value="3" min="1" max="6"><button id="create">Criar sprint</button><button id="approve">Criar sprint + cartão de aprovação</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Último sprint</h2><div id="sprint"></div></section>
  <section class="panel"><h2>Tarefas</h2><div class="grid" id="tasks"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){qs('#summary').innerHTML=card('Sprints',d.sprint_count||0)+card('Tarefas',d.task_count||0);const s=d.latest_sprint;qs('#sprint').innerHTML=s?`<div class="card"><b>${esc(s.sprint_id)}</b><p>${esc(s.summary)}</p><p>${(s.project_ids||[]).map(x=>`<span class="pill">${esc(x)}</span>`).join('')}</p></div>`:'<p class="muted">Sem sprint.</p>';qs('#tasks').innerHTML=(d.latest_tasks||[]).map(t=>`<div class="card"><b>${esc(t.project_id)} · ${esc(t.title)}</b><p class="muted">${esc(t.risk)} · ${esc(t.kind)}</p><p>${esc(t.description)}</p></div>`).join('')||'<p class="muted">Sem tarefas.</p>';show(d)}async function load(){render(await api('/api/revenue-sprint/dashboard'))}function body(){return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({max_projects:Number(qs('#max').value||3)})}}qs('#create').onclick=async()=>{show(await api('/api/revenue-sprint/create',body()));load()};qs('#approve').onclick=async()=>{show(await api('/api/revenue-sprint/approval-card',body()));load()};load();
</script>
</body></html>
"""


@router.get('/app/revenue-sprint', response_class=HTMLResponse)
async def revenue_sprint_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
