from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["project-portfolio-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Project Portfolio</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#34d399;--bad:#ef4444;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#071a12,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}button,input,select{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#059669,#34d399);border:none;color:#001b11;font-weight:900}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px}.row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}pre{white-space:pre-wrap;overflow:auto;font-size:12px}@media(max-width:780px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Project Portfolio</h1><p class="muted">Mapa dos teus projetos, repos, prioridades e próximo caminho para monetizar.</p></section>
  <section class="panel"><button id="seed">Inicializar / atualizar portfólio</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Ligar repo</h2><div class="row"><input id="pid" placeholder="PROJECT_ID" value="BARIBUDOS_STUDIO"><input id="repo" placeholder="AndreVazao/repo"><select id="role"><option>studio</option><option>website</option><option>backend</option><option>frontend</option><option>workflow</option><option>mobile</option></select></div><button id="link">Ligar repositório</button></section>
  <section class="panel"><h2>Projetos</h2><div class="grid" id="projects"></div></section>
  <section class="panel"><h2>Próximas ações recomendadas</h2><div id="actions"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const s=d.summary||{};qs('#summary').innerHTML=card('Projetos',s.project_count||0)+card('Repos',s.repository_count||0)+card('Alta prioridade',s.high_priority_count||0);qs('#projects').innerHTML=(d.projects||[]).map(p=>`<div class="card"><b>${esc(p.name)}</b><span class="pill">${esc(p.project_id)}</span><span class="pill">${esc(p.priority)}</span><p class="muted">${esc(p.goal)}</p><p>${(p.repositories||[]).map(r=>`<span class="pill">${esc(r)}</span>`).join(' ')||'<span class="muted">sem repo ligado</span>'}</p></div>`).join('');qs('#actions').innerHTML=(d.next_recommended_actions||[]).map(a=>`<div class="card">${esc(a)}</div>`).join('');show(d)}
async function load(){render(await api('/api/project-portfolio/dashboard'))}qs('#seed').onclick=async()=>{show(await api('/api/project-portfolio/seed',{method:'POST'}));load()};qs('#link').onclick=async()=>{const r=await api('/api/project-portfolio/repositories/link',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:qs('#pid').value,repository_full_name:qs('#repo').value,role:qs('#role').value})});show(r);load()};load();
</script>
</body></html>
"""


@router.get('/app/project-portfolio', response_class=HTMLResponse)
async def project_portfolio_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
