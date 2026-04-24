from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["system-integrity-audit-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>System Integrity Audit</title>
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
    .chip.clean { color:#bbf7d0; border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.12); }
    .chip.ready_with_attention { color:#fde68a; border-color:rgba(245,158,11,.4); background:rgba(245,158,11,.12); }
    .chip.blocked { color:#fecaca; border-color:rgba(239,68,68,.4); background:rgba(239,68,68,.12); }
    button { font:inherit; border-radius:14px; border:none; background:var(--accent); color:white; padding:10px 12px; font-weight:700; cursor:pointer; }
    .finding-critical { border-color:rgba(239,68,68,.55); }
    .finding-high { border-color:rgba(245,158,11,.55); }
    .finding-medium { border-color:rgba(96,165,250,.45); }
    @media (max-width: 800px){ .page{padding:8px;} }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>System Integrity Audit</h1><p>Auditoria interna: workflows, routes, services, docs e storage local.</p></div>
      <button id=\"runBtn\">Auditar agora</button>
    </section>
    <section class=\"summary\" id=\"summary\"></section>
    <section class=\"panel\"><h2>Findings</h2><div id=\"findings\"></div></section>
    <section class=\"panel\"><h2>Próximas ações</h2><div id=\"actions\"></div></section>
  </div>
  <script>
    const qs = s => document.querySelector(s);
    async function api(path, options){ const r = await fetch(path, options); if(!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function esc(v){ return String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function render(d){
      const items = [['Status',d.status],['Score',d.readiness_score],['Findings',d.finding_count],['Workflows',d.workflow_count],['Routes',d.route_count],['Services',d.service_count],['Docs',d.doc_count]];
      qs('#summary').innerHTML = items.map(([l,v])=>`<div class=\"card\"><span class=\"muted\">${esc(l)}</span><strong style=\"font-size:26px\">${esc(v)}</strong></div>`).join('');
      qs('#findings').innerHTML = (d.findings||[]).map(f=>`<div class=\"card finding-${esc(f.severity)}\"><div class=\"row\"><strong>${esc(f.title)}</strong><span class=\"chip ${esc(d.status)}\">${esc(f.severity)}</span></div><div class=\"muted\">${esc(f.category)} · ${esc(f.count)} items</div><pre style=\"white-space:pre-wrap;overflow:auto;margin:0\">${esc(JSON.stringify(f.items,null,2))}</pre></div>`).join('') || '<div class=\"muted\">Sem findings.</div>';
      qs('#actions').innerHTML = (d.next_actions||[]).map(a=>`<div class=\"card\">${esc(a)}</div>`).join('');
    }
    async function load(){ render(await api('/api/system-integrity-audit/dashboard')); }
    async function run(){ render(await api('/api/system-integrity-audit/run',{method:'POST'})); }
    qs('#runBtn').onclick=run; load(); setInterval(load,15000);
  </script>
</body>
</html>
"""


@router.get('/app/system-integrity-audit', response_class=HTMLResponse)
async def system_integrity_audit_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
