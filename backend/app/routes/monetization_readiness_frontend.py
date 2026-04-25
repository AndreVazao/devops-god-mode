from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["monetization-readiness-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Monetization Readiness</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#facc15;--ok:#22c55e;--bad:#ef4444;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#201a05,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}button{font:inherit;border-radius:15px;border:0;background:linear-gradient(135deg,#ca8a04,#facc15);color:#1b1300;padding:11px;font-weight:900}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}.ready{color:var(--ok)}.blocked{color:var(--bad)}.focus{color:var(--warn)}pre{white-space:pre-wrap;overflow:auto;font-size:12px}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Monetization Readiness</h1><p class="muted">Matriz para decidir o caminho mais curto até MVP, deploy e dinheiro.</p></section>
  <section class="panel"><button id="refresh">Gerar matriz agora</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Projetos</h2><div class="grid" id="rows"></div></section>
  <section class="panel"><h2>Recomendações</h2><div id="recommendations"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:25px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const s=d.summary||{};qs('#summary').innerHTML=card('Projetos',s.project_count||0)+card('Prontos',s.ready_count||0)+card('Bloqueados',s.blocked_count||0)+card('Foco',s.focus_count||0);qs('#rows').innerHTML=(d.rows||[]).map(r=>`<div class="card"><b>${esc(r.name)}</b><span class="pill ${r.status==='ready_to_package'?'ready':r.status==='blocked'?'blocked':'focus'}">${esc(r.status)}</span><span class="pill">score ${esc(r.readiness_score)}</span><p><b>MVP:</b> ${esc(r.mvp)}</p><p><b>1ª venda:</b> ${esc(r.first_sellable_feature)}</p><p class="muted">${esc(r.revenue_path)}</p><p>${(r.blockers||[]).map(b=>`<span class="pill blocked">${esc(b)}</span>`).join('')}</p><p><b>Próximo:</b> ${esc(r.next_action)}</p></div>`).join('');qs('#recommendations').innerHTML=(d.top_recommendations||[]).map(x=>`<div class="card">${esc(x)}</div>`).join('');show(d)}async function load(){render(await api('/api/monetization-readiness/dashboard'))}qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/monetization-readiness', response_class=HTMLResponse)
async def monetization_readiness_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
