from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["project-tree-sync-guard-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Project Tree Sync Guard</title>
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
    .muted { color:var(--muted); }
    .ok { color:#bbf7d0; } .bad { color:#fecaca; }
    button { font:inherit; border-radius:14px; border:none; background:var(--accent); color:white; padding:10px 12px; font-weight:700; cursor:pointer; }
    pre { white-space:pre-wrap; overflow:auto; margin:0; font-size:12px; }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Project Tree Sync Guard</h1><p>Guarda que impede PROJECT_TREE.txt de ficar desatualizado.</p></div>
      <button id=\"refreshBtn\">Atualizar</button>
    </section>
    <section class=\"summary\" id=\"summary\"></section>
    <section class=\"panel\"><h2>Diferenças</h2><div id=\"diffs\"></div></section>
    <section class=\"panel\"><h2>Regras</h2><div id=\"rules\"></div></section>
  </div>
  <script>
    const qs = s => document.querySelector(s);
    async function api(path){ const r = await fetch(path); if(!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function esc(v){ return String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function render(d){
      const items = [['Existe',d.project_tree_exists],['Sync',d.in_sync],['Generated',d.generated_line_count],['Committed',d.committed_line_count],['Missing',d.missing_from_committed_count],['Stale',d.stale_in_committed_count]];
      qs('#summary').innerHTML = items.map(([l,v])=>`<div class=\"card\"><span class=\"muted\">${esc(l)}</span><strong style=\"font-size:24px\" class=\"${v===false?'bad':'ok'}\">${esc(v)}</strong></div>`).join('');
      qs('#diffs').innerHTML = `<div class=\"card\"><strong>Missing from committed</strong><pre>${esc(JSON.stringify(d.check.missing_from_committed,null,2))}</pre></div><div class=\"card\"><strong>Stale in committed</strong><pre>${esc(JSON.stringify(d.check.stale_in_committed,null,2))}</pre></div>`;
      qs('#rules').innerHTML = (d.rules||[]).map(rule=>`<div class=\"card\">${esc(rule)}</div>`).join('');
    }
    async function load(){ render(await api('/api/project-tree-sync-guard/dashboard')); }
    qs('#refreshBtn').onclick=load; load(); setInterval(load,15000);
  </script>
</body>
</html>
"""


@router.get('/app/project-tree-sync-guard', response_class=HTMLResponse)
async def project_tree_sync_guard_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
