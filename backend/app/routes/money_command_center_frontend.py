from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["money-command-center-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Money Command Center</title>
  <style>
    :root{color-scheme:dark;--bg:#070b14;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#22c55e;--accent2:#84cc16;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#052e16,#070b14 52%);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px;box-shadow:0 12px 34px rgba(0,0,0,.28)}.top h1{margin:0;font-size:22px}.muted{color:var(--muted)}.money{font-size:36px;font-weight:1000;line-height:1}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:10px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:9px}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#16a34a,#84cc16);border:none;color:#03120a;font-weight:1000}button.secondary{background:#0b1220;color:var(--text);border:1px solid var(--line)}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}.ok{color:var(--accent)}.warn{color:var(--warn)}.bad{color:var(--bad)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:360px}@media(max-width:760px){.row{grid-template-columns:1fr}.money{font-size:30px}.page{padding:10px}.top,.panel,.card{border-radius:18px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top">
    <h1>Money Command Center</h1>
    <p class="muted">Um cockpit para responder: “qual é o próximo passo mais curto para começar a ganhar dinheiro?”</p>
    <div class="money" id="answer">A calcular...</div>
  </section>
  <section class="panel row"><input id="max" type="number" value="3" min="1" max="6"><input id="project" placeholder="Projeto opcional: PROVENTIL"></section>
  <section class="panel buttons">
    <button id="top">Ver projeto com maior chance de dinheiro</button>
    <button id="sprint">Criar sprint de receita</button>
    <button id="approve">Aprovar próximo passo</button>
    <button id="blockers" class="secondary">Ver bloqueios</button>
    <button id="offers" class="secondary">Ver primeiro produto vendável</button>
    <button id="delivery">Preparar entrega MVP</button>
  </section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Projeto recomendado</h2><div id="topProject"></div></section>
  <section class="panel"><h2>Primeiras ofertas vendáveis</h2><div class="grid" id="offersList"></div></section>
  <section class="panel"><h2>Bloqueios</h2><div class="grid" id="blockerList"></div></section>
  <section class="panel"><h2>Último sprint</h2><div id="sprintView"></div></section>
  <section class="panel"><h2>Resultado bruto</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const s=d.summary||{};qs('#answer').textContent=d.operator_answer||'Sem recomendação ainda.';qs('#summary').innerHTML=card('Top projeto',s.top_project||'—')+card('Aprovações',s.pending_approvals||0,'pendentes')+card('Sprints',s.sprint_count||0)+card('Bloqueios',s.blocker_count||0);const top=d.top_project;qs('#topProject').innerHTML=top?`<div class="card"><b>${esc(top.name)} · ${esc(top.project_id)}</b><p>${esc(top.first_sellable_feature)}</p><p class="muted">Score ${esc(top.readiness_score)} · ${esc(top.next_action)}</p>${(top.blockers||[]).map(x=>`<span class="pill warn">${esc(x)}</span>`).join('')}</div>`:'<p class="muted">Sem top projeto.</p>';qs('#offersList').innerHTML=(d.offers||[]).slice(0,9).map(o=>`<div class="card"><b>${esc(o.name)}</b><p>${esc(o.first_sellable_feature)}</p><p class="muted">${esc(o.revenue_path)}</p><span class="pill">score ${esc(o.readiness_score)}</span></div>`).join('')||'<p class="muted">Sem ofertas.</p>';qs('#blockerList').innerHTML=(d.blockers||[]).slice(0,12).map(b=>`<div class="card"><b>${esc(b.name)}</b><p class="warn">${esc(b.blocker)}</p><p class="muted">${esc(b.next_action)}</p></div>`).join('')||'<p class="ok">Sem bloqueios principais.</p>';const sp=d.latest_sprint;qs('#sprintView').innerHTML=sp?`<div class="card"><b>${esc(sp.sprint_id)}</b><p>${esc(sp.summary)}</p><p>${(sp.project_ids||[]).map(x=>`<span class="pill">${esc(x)}</span>`).join('')}</p></div>`:'<p class="muted">Sem sprint criado.</p>';show(d)}async function load(){render(await api('/api/money-command-center/dashboard'))}function sprintBody(){return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({max_projects:Number(qs('#max').value||3)})}}function deliveryBody(){const p=qs('#project').value.trim();return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:p||null})}}
qs('#top').onclick=async()=>{show(await api('/api/money-command-center/top-project'));load()};qs('#sprint').onclick=async()=>{show(await api('/api/money-command-center/revenue-sprint',sprintBody()));load()};qs('#approve').onclick=async()=>{show(await api('/api/money-command-center/approval-card',sprintBody()));load()};qs('#blockers').onclick=async()=>show(await api('/api/money-command-center/blockers'));qs('#offers').onclick=async()=>show(await api('/api/money-command-center/sellable-offers'));qs('#delivery').onclick=async()=>{show(await api('/api/money-command-center/prepare-mvp-delivery',deliveryBody()));load()};load();
</script>
</body></html>
"""


@router.get('/app/money-command-center', response_class=HTMLResponse)
async def money_command_center_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
