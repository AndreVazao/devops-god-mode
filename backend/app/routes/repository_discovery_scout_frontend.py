from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["repository-discovery-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repository Discovery Scout</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#60a5fa;--bad:#ef4444;--warn:#f59e0b;--ok:#22c55e}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#071327,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px;padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}.row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}button,input,select{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#2563eb,#60a5fa);border:none;font-weight:900}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px}.bad{color:var(--bad)}.ok{color:var(--ok)}pre{white-space:pre-wrap;overflow:auto;font-size:12px}@media(max-width:780px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Repository Discovery Scout</h1><p class="muted">Descobre se projetos como Bot Factory já têm repo/app ou se precisam de proposta de repo novo.</p></section>
  <section class="panel row"><select id="project"><option>BOT_FACTORY</option><option>GOD_MODE</option><option>BARIBUDOS_STUDIO</option><option>BARIBUDOS_STUDIO_WEBSITE</option><option>PROVENTIL</option><option>VERBAFORGE</option><option>BUILD_CONTROL_CENTER</option></select><button id="plan">Plano de procura</button><button id="audit">Auditar projeto</button></section>
  <section class="panel"><h2>Adicionar candidato manual</h2><div class="row"><input id="repo" placeholder="AndreVazao/repo"><input id="note" placeholder="nota"><select id="role"><option>unknown</option><option>backend</option><option>frontend</option><option>website</option><option>studio</option><option>mobile</option><option>workflow</option></select></div><button id="candidate">Adicionar candidato</button></section>
  <section class="panel"><h2>Dashboard</h2><div class="grid" id="audits"></div></section>
  <section class="panel"><h2>Candidatos</h2><div class="grid" id="candidates"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function project(){return qs('#project').value}async function confirmCandidate(id){const r=await api('/api/repository-discovery/candidates/confirm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({candidate_id:id,role:qs('#role').value})});show(r);load()}
function render(d){qs('#audits').innerHTML=(d.audits||[]).map(a=>`<div class="card"><b>${esc(a.project_id)}</b><p class="muted">${esc(a.status)}</p><span class="pill">repos ${esc(a.existing_repository_count)}</span><span class="pill">candidatos ${esc(a.candidate_count)}</span>${a.proposal?`<p class="bad">Propor: ${esc(a.proposal.suggested_repository_full_name)}</p>`:''}</div>`).join('');qs('#candidates').innerHTML=(d.candidates||[]).map(c=>`<div class="card"><b>${esc(c.repository_full_name)}</b><p class="muted">${esc(c.project_id)} · ${esc(c.status)} · ${esc(c.confidence)}</p><button onclick="confirmCandidate('${esc(c.candidate_id)}')">Confirmar e ligar</button></div>`).join('')||'<p class="muted">Sem candidatos.</p>';show(d)}async function load(){render(await api('/api/repository-discovery/dashboard'))}
qs('#plan').onclick=async()=>show(await api('/api/repository-discovery/plan/'+encodeURIComponent(project())));qs('#audit').onclick=async()=>{show(await api('/api/repository-discovery/audit/'+encodeURIComponent(project())));load()};qs('#candidate').onclick=async()=>{const r=await api('/api/repository-discovery/candidates',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:project(),repository_full_name:qs('#repo').value,confidence:0.7,source:'operator',note:qs('#note').value})});show(r);load()};load();
</script>
</body></html>
"""


@router.get('/app/repository-discovery', response_class=HTMLResponse)
async def repository_discovery_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
