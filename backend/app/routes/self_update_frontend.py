from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["self-update-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Self Update</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#818cf8;--ok:#22c55e;--bad:#ef4444;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#0f1028,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}button,input,select{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#4f46e5,#818cf8);border:none;font-weight:900}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}.bad{color:var(--bad)}.ok{color:var(--ok)}pre{white-space:pre-wrap;overflow:auto;font-size:12px}@media(max-width:780px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Self Update</h1><p class="muted">Atualiza o God Mode local sem apagar memória, dados, .env ou estado do operador.</p></section>
  <section class="panel row"><input id="channel" value="main"><button id="plan">Criar plano</button><button id="backup">Manifest backup</button><button id="dry">Dry-run update</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Preservar sempre</h2><div id="preserve"></div></section>
  <section class="panel"><h2>Estado Git</h2><pre id="git"></pre></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const st=d.status||{};qs('#summary').innerHTML=card('Git',st.git_available?'ok':'falta')+card('Planos',st.plan_count||0)+card('Runs',st.run_count||0)+card('Backups',st.backup_count||0);qs('#preserve').innerHTML=(d.preserve_paths||[]).map(x=>`<span class="pill">${esc(x)}</span>`).join('');qs('#git').textContent=JSON.stringify(d.git_state,null,2);show(d)}async function load(){render(await api('/api/self-update/dashboard'))}function body(dry){return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channel:qs('#channel').value,dry_run:dry})}}qs('#plan').onclick=async()=>{show(await api('/api/self-update/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channel:qs('#channel').value})}));load()};qs('#backup').onclick=async()=>{show(await api('/api/self-update/backup-manifest',{method:'POST'}));load()};qs('#dry').onclick=async()=>{show(await api('/api/self-update/execute',body(true)));load()};load();
</script>
</body></html>
"""


@router.get('/app/self-update', response_class=HTMLResponse)
async def self_update_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
