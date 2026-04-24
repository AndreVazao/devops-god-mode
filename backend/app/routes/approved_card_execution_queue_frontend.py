from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["approved-card-execution-queue-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Approved Card Execution Queue</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --ok:#22c55e; --warn:#f59e0b; --danger:#ef4444; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:14px; display:grid; gap:14px; }
    .topbar, .panel, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:14px; display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    h1 { margin:0; font-size:20px; } p { margin:5px 0 0; color:var(--muted); }
    .summary { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }
    .panel { padding:14px; overflow:auto; }
    .card { padding:12px; background:rgba(15,23,41,.75); display:grid; gap:8px; margin-bottom:10px; }
    .row { display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .muted { color:var(--muted); }
    .chip { padding:4px 8px; border-radius:999px; border:1px solid var(--line); font-size:12px; font-weight:700; }
    .chip.queued { color:#bfdbfe; border-color:rgba(96,165,250,.4); background:rgba(96,165,250,.12); }
    .chip.running { color:#fde68a; border-color:rgba(245,158,11,.4); background:rgba(245,158,11,.12); }
    .chip.completed { color:#bbf7d0; border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.12); }
    .chip.blocked, .chip.failed { color:#fecaca; border-color:rgba(239,68,68,.4); background:rgba(239,68,68,.12); }
    button { font:inherit; border-radius:14px; border:none; background:var(--accent); color:white; padding:10px 12px; font-weight:700; cursor:pointer; }
    .steps { display:grid; gap:6px; }
    .step { padding:8px; border:1px solid var(--line); border-radius:12px; }
    @media (max-width: 800px){ .page{padding:8px;} }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Approved Card Execution Queue</h1><p>Transforma cartões aprovados do telemóvel em tarefas seguras para o PC.</p></div>
      <div><button id=\"ingestBtn\">Ingerir aprovados</button> <button id=\"refreshBtn\">Atualizar</button></div>
    </section>
    <section class=\"summary\" id=\"summary\"></section>
    <section class=\"panel\"><div id=\"tasks\"></div></section>
  </div>
  <script>
    const qs = s => document.querySelector(s);
    async function api(path, options){ const r = await fetch(path, options); if(!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function esc(v){ return String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function renderSummary(d){ qs('#summary').innerHTML = [['Tasks',d.task_count],['Queued',d.queued_count],['Blocked',d.blocked_count],['Risky steps',d.risky_step_count]].map(([l,v])=>`<div class=\"card\"><span class=\"muted\">${esc(l)}</span><strong style=\"font-size:28px\">${esc(v)}</strong></div>`).join(''); }
    function renderTasks(tasks){ qs('#tasks').innerHTML = (tasks||[]).slice().reverse().map(t=>`<div class=\"card\"><div class=\"row\"><strong>${esc(t.source_title)}</strong><span class=\"chip ${esc(t.status)}\">${esc(t.status)}</span></div><div class=\"muted\">${esc(t.project_id)} · ${esc(t.source_card_type)} · ${esc(t.execution_mode)}</div><div class=\"steps\">${(t.steps||[]).map(s=>`<div class=\"step\">${esc(s.label)} <span class=\"muted\">· ${esc(s.risk)}</span></div>`).join('')}</div></div>`).join('') || '<div class=\"muted\">Sem tarefas.</div>'; }
    async function load(){ const d = await api('/api/approved-card-execution-queue/dashboard?tenant_id=owner-andre'); renderSummary(d); renderTasks(d.recent_tasks); }
    async function ingest(){ await api('/api/approved-card-execution-queue/ingest-approved-cards',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tenant_id:'owner-andre'})}); await load(); }
    qs('#refreshBtn').onclick=load; qs('#ingestBtn').onclick=ingest; load(); setInterval(load,10000);
  </script>
</body>
</html>
"""


@router.get('/app/approved-card-execution-queue', response_class=HTMLResponse)
async def approved_card_execution_queue_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
