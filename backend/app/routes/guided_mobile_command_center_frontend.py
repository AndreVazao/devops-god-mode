from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["guided-command-center-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Guided Command Center</title>
  <style>
    :root{color-scheme:dark;--bg:#070b14;--panel:#0f172a;--card:#111c31;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#22d3ee;--ok:#22c55e;--warn:#f59e0b}
    *{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#07101e,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px}.top{padding:14px;position:sticky;top:0;z-index:2}.top h1{margin:0;font-size:20px}.top p{margin:5px 0 0;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}.panel{padding:12px}.card{padding:12px;background:rgba(17,28,49,.8);display:grid;gap:8px}button,select,textarea,input{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#0891b2,#22d3ee);border:none;color:#00131a;font-weight:900}textarea{width:100%;min-height:90px;resize:vertical}.muted{color:var(--muted)}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px}.primary{font-size:18px;font-weight:900}.quick{position:fixed;right:14px;bottom:14px;display:grid;gap:8px}.quick a{background:var(--accent);color:#00131a;text-decoration:none;padding:12px 14px;border-radius:999px;font-weight:900}pre{white-space:pre-wrap;overflow:auto;font-size:12px}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}@media(max-width:720px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Guided Command Center</h1><p>Botões guiados para não precisares decorar comandos. Escolhe projeto, escolhe ação, envia.</p></section>
  <section class="panel row"><select id="project"><option>GOD_MODE</option><option>PROVENTIL</option><option>VERBAFORGE</option><option>BOT_LORDS_MOBILE</option><option>ECU_REPRO</option><option>BUILD_CONTROL_CENTER</option></select><button id="refresh">Atualizar</button></section>
  <section class="panel"><h2>Ações rápidas</h2><div id="actions" class="grid"></div></section>
  <section class="panel"><h2>Instrução adicional</h2><textarea id="extra" placeholder="Opcional: acrescenta detalhe, prioridade, repo, problema visto..."></textarea></section>
  <section class="panel"><h2>Memória do projeto</h2><div id="brief" class="grid"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<div class="quick"><a href="/app/mission-control">Mission</a><a href="/app/memory-core">Memória</a><a href="/app/mobile-approval-cockpit-v2">Aprovar</a></div>
<script>
const qs=s=>document.querySelector(s);let ACTIONS=[];async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function project(){return qs('#project').value}
async function execute(id){const res=await api('/api/guided-command-center/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:project(),action_id:id,extra_instruction:qs('#extra').value})});show(res)}
function renderActions(actions){qs('#actions').innerHTML=actions.map(a=>`<div class="card"><div class="primary">${esc(a.label)}</div><div class="muted">${esc(a.description)}</div><span class="pill">${esc(a.risk)}</span><button onclick="execute('${esc(a.action_id)}')">Executar</button></div>`).join('')}
function renderBrief(b){qs('#brief').innerHTML=`<div class="card"><div class="muted">Projeto</div><div class="primary">${esc(b.project)}</div></div><div class="card"><div class="muted">Memória</div><div class="primary">${esc(b.memory_score)}%</div></div><div class="card"><div class="muted">Checklist</div><div>${Object.entries(b.checklist||{}).map(([k,v])=>`<span class="pill">${esc(k)}: ${v?'ok':'falta'}</span>`).join(' ')}</div></div><div class="card"><a href="${esc(b.obsidian?.open_uri||'#')}">Abrir nota Obsidian</a></div>`}
async function load(){const pkg=await api('/api/guided-command-center/package');ACTIONS=pkg.package.dashboard.actions;renderActions(ACTIONS);const b=await api('/api/guided-command-center/projects/'+encodeURIComponent(project())+'/brief');renderBrief(b);show(pkg)}
qs('#refresh').onclick=load;qs('#project').onchange=load;load();
</script>
</body></html>
"""


@router.get('/app/guided-command-center', response_class=HTMLResponse)
async def guided_command_center_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
