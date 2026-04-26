from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["request-orchestrator-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Request Orchestrator</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#111827,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}.status{font-weight:1000}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Request Orchestrator</h1><p class="muted">Dá a ordem. O backend trabalha até terminar ou até precisar do teu OK/inputs manuais.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="project" value="GOD_MODE"><input id="thread" placeholder="thread opcional"></section>
  <section class="panel"><textarea id="req" rows="4" placeholder="Ex: quero começar a ganhar dinheiro com o projeto mais rápido; prepara tudo e pára só quando precisares do meu OK"></textarea><div class="buttons"><button id="submit" class="good">Dar ordem ao backend</button><button id="refresh">Atualizar</button><button class="dark" onclick="location.href='/app/mobile-approval-cockpit-v2'">Aprovações</button></div></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Jobs recentes</h2><div class="grid" id="jobs"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let dashboard=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(d){dashboard=d;const s=d.summary||{};qs('#hero').textContent=`${s.jobs||0} jobs · ${s.blocked||0} bloqueados`;qs('#cards').innerHTML=card('Ativos',s.running||0)+card('Bloqueados',s.blocked||0)+card('Concluídos',s.completed||0)+card('Total',s.jobs||0);qs('#jobs').innerHTML=(d.recent_jobs||[]).slice().reverse().map(j=>`<div class="card"><b>${esc(j.intent)}</b><p>${esc(j.request)}</p><p class="status">${esc(j.status)}</p><p class="muted">${esc(j.blocking_reason||'')}</p><div class="buttons"><button onclick="resumeJob('${esc(j.job_id)}')">Continuar</button><button class="dark" onclick="runJob('${esc(j.job_id)}')">Correr</button></div></div>`).join('')||'<p class="muted">Sem jobs.</p>';show(d)}async function load(){const t=encodeURIComponent(qs('#tenant').value||'owner-andre');render(await api(`/api/request-orchestrator/dashboard?tenant_id=${t}`))}async function submit(){const payload={request:qs('#req').value.trim(),tenant_id:qs('#tenant').value||'owner-andre',project_id:qs('#project').value||'GOD_MODE',thread_id:qs('#thread').value.trim()||null,auto_run:true};if(!payload.request)return;const r=await api('/api/request-orchestrator/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});qs('#req').value='';show(r);await load()}async function resumeJob(id){const r=await api('/api/request-orchestrator/resume',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:id,tenant_id:qs('#tenant').value||'owner-andre',operator_note:'Retomado pelo cockpit'})});show(r);await load()}async function runJob(id){const t=encodeURIComponent(qs('#tenant').value||'owner-andre');show(await api(`/api/request-orchestrator/run/${id}?tenant_id=${t}`,{method:'POST'}));await load()}qs('#submit').onclick=submit;qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/request-orchestrator', response_class=HTMLResponse)
async def request_orchestrator_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
