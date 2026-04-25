from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["project-tree-autorefresh-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Project Tree Autorefresh</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--ok:#22c55e;--bad:#ef4444;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#071524,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}button{font:inherit;border:0;border-radius:15px;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#00131f;padding:11px;font-weight:900}.bad{color:var(--bad)}.ok{color:var(--ok)}.warn{color:var(--warn)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Project Tree Autorefresh</h1><p class="muted">Compara PROJECT_TREE.txt com a estrutura real e evita esquecimentos em cada fase.</p></section>
  <section class="panel"><button id="refresh">Comparar agora</button><button id="generated">Ver tree gerada</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Preview diferenças</h2><div class="grid"><div class="card"><h3>Em falta</h3><pre id="missing"></pre></div><div class="card"><h3>Obsoletas</h3><pre id="obsolete"></pre></div></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const c=d.comparison||d.report||{};qs('#summary').innerHTML=card('Estado',d.status||c.in_sync?'in_sync':'needs_refresh')+card('Linhas atuais',c.current_line_count||0)+card('Linhas geradas',c.generated_line_count||0)+card('Em falta',c.missing_line_count||0)+card('Obsoletas',c.obsolete_line_count||0);qs('#missing').textContent=(c.missing_lines_preview||[]).join('\n');qs('#obsolete').textContent=(c.obsolete_lines_preview||[]).join('\n');show(d)}async function load(){render(await api('/api/project-tree-autorefresh/dashboard'))}qs('#refresh').onclick=load;qs('#generated').onclick=async()=>show(await api('/api/project-tree-autorefresh/generated'));load();
</script>
</body></html>
"""


@router.get('/app/project-tree-autorefresh', response_class=HTMLResponse)
async def project_tree_autorefresh_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
