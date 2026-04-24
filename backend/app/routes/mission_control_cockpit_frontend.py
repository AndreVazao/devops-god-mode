from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["mission-control-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Mission Control</title>
  <style>
    :root{color-scheme:dark;--bg:#070b14;--panel:#101827;--line:#26334d;--text:#eaf1ff;--muted:#9fb0d0;--accent:#38bdf8;--ok:#22c55e;--warn:#f59e0b;--bad:#ef4444}
    *{box-sizing:border-box} body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#12203a,#070b14 55%);color:var(--text)}
    .page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(16,24,39,.92);border:1px solid var(--line);border-radius:20px;box-shadow:0 18px 50px rgba(0,0,0,.25)}
    .top{padding:14px;display:flex;justify-content:space-between;gap:10px;align-items:center;position:sticky;top:0;z-index:3}.brand h1{font-size:20px;margin:0}.brand p{margin:4px 0 0;color:var(--muted);font-size:13px}.light{width:18px;height:18px;border-radius:999px;background:var(--warn);box-shadow:0 0 22px currentColor}.green{color:var(--ok);background:var(--ok)}.yellow{color:var(--warn);background:var(--warn)}.red{color:var(--bad);background:var(--bad)}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:10px}.panel{padding:12px}.card{padding:12px;background:rgba(15,23,42,.72)}.big{font-size:26px;font-weight:900}.muted{color:var(--muted)}button,input,select,textarea{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px 12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:0;font-weight:800;cursor:pointer}textarea{width:100%;min-height:120px;resize:vertical}.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1}.project{display:grid;gap:8px}.pill{display:inline-flex;padding:5px 9px;border-radius:999px;background:#0b1220;border:1px solid var(--line);font-size:12px}.scroll{max-height:360px;overflow:auto}pre{white-space:pre-wrap;overflow:auto;font-size:12px}.quick{position:fixed;right:14px;bottom:14px;display:grid;gap:8px;z-index:5}.quick a{background:var(--accent);color:#00131f;text-decoration:none;padding:12px 14px;border-radius:999px;font-weight:900;box-shadow:0 10px 30px rgba(56,189,248,.3)}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><div class="brand"><h1>God Mode Mission Control</h1><p>Um ecrã para comando, memória, aprovações, fila e auditoria.</p></div><div id="light" class="light yellow"></div></section>
  <section class="panel"><div class="row"><select id="project"><option>GOD_MODE</option><option>PROVENTIL</option><option>VERBAFORGE</option><option>BOT_LORDS_MOBILE</option><option>ECU_REPRO</option><option>BUILD_CONTROL_CENTER</option></select><button id="refresh">Atualizar</button></div></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Comando rápido</h2><textarea id="cmd" placeholder="Ex: Audita o God Mode e diz-me o próximo passo seguro..."></textarea><button id="send">Enviar e criar cartão de aprovação</button></section>
  <section class="panel"><h2>Projetos</h2><div id="projects" class="grid"></div></section>
  <section class="panel"><h2>Últimos cartões / tarefas</h2><div id="activity" class="scroll"></div></section>
  <section class="panel"><h2>Debug</h2><pre id="out"></pre></section>
</div>
<div class="quick"><a href="/app/memory-core">Memória</a><a href="/app/mobile-approval-cockpit-v2">Aprovar</a><a href="/app/system-integrity-audit">Auditar</a></div>
<script>
const qs=s=>document.querySelector(s); async function api(p,o){const r=await fetch(p,o); const t=await r.text(); let j; try{j=JSON.parse(t)}catch{j={raw:t}}; if(!r.ok) throw new Error(t); return j} function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')} function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}
function card(label,value,sub=''){return `<div class="card"><div class="muted">${esc(label)}</div><div class="big">${esc(value)}</div><div class="muted">${esc(sub)}</div></div>`}
function render(d){qs('#light').className='light '+(d.readiness||'yellow'); const s=d.summary||{}; qs('#summary').innerHTML=card('Estado',d.readiness||'?', 'verde/amarelo/vermelho')+card('Aprovações',s.pending_approvals??0,'pendentes')+card('Fila',s.queued_tasks??0,'tarefas queued')+card('Auditoria',s.integrity_status??'?','integridade')+card('Tree',s.project_tree_in_sync?'sync':'ver','PROJECT_TREE'); qs('#projects').innerHTML=(d.projects||[]).map(p=>`<div class="card project"><b>${esc(p.project)}</b><span class="pill">memória ${esc(p.memory_score)}%</span><span class="muted">Sessão: ${p.has_last_session?'sim':'não'} · Backlog: ${p.has_backlog?'sim':'não'} · Decisões: ${p.has_decisions?'sim':'não'}</span><a href="${esc(p.obsidian?.open_uri||'#')}">Abrir Obsidian</a></div>`).join(''); const cards=d.approvals?.result?.recent_cards||[]; const tasks=d.queue?.result?.recent_tasks||[]; qs('#activity').innerHTML=[...cards.slice(-10).map(x=>`<div class="card"><b>${esc(x.title)}</b><p class="muted">${esc(x.status)} · ${esc(x.project_id)}</p></div>`),...tasks.slice(-10).map(x=>`<div class="card"><b>${esc(x.source_title)}</b><p class="muted">${esc(x.status)} · ${esc(x.project_id)}</p></div>`)].join('')||'<p class="muted">Sem atividade recente.</p>'; show(d)}
async function load(){render(await api('/api/mission-control/dashboard'))}
qs('#refresh').onclick=load; qs('#send').onclick=async()=>{const res=await api('/api/mission-control/command',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command_text:qs('#cmd').value,project_hint:qs('#project').value})}); render(res.dashboard)}; load(); setInterval(load,15000);
</script>
</body></html>
"""


@router.get('/app/mission-control', response_class=HTMLResponse)
async def mission_control_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
