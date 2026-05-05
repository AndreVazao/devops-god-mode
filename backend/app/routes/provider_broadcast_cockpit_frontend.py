from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["provider-broadcast-cockpit-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Provider Broadcast Cockpit</title>
  <style>
    :root{color-scheme:dark;--bg:#050816;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444;--blue:#60a5fa}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 55%);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card,.provider,.job{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px;box-shadow:0 14px 34px rgba(0,0,0,.32)}h1,h2,h3{margin:.1rem 0}.hero{font-size:25px;font-weight:1000;line-height:1.1}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.providers{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}.provider{display:flex;align-items:center;gap:10px}.provider input{width:22px;height:22px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea,select{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000;cursor:pointer}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}button.ok{background:linear-gradient(135deg,#15803d,#22c55e);color:#04130a}button.warn{background:linear-gradient(135deg,#b45309,#f59e0b);color:#1f1300}textarea{width:100%;min-height:105px;resize:vertical}.promptBox{white-space:pre-wrap;background:#081226;border:1px solid var(--line);border-radius:18px;padding:12px;max-height:260px;overflow:auto}.chip{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 9px;color:var(--muted);font-size:12px}.job{display:grid;gap:8px}.row{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.copy{background:#1d4ed8;color:white}.response{min-height:130px}.good{color:#86efac}.warnText{color:#fde68a}.bad{color:#fecaca}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:360px;background:#081226;border:1px solid var(--line);border-radius:18px;padding:12px}@media(max-width:760px){.hero{font-size:21px}.buttons{grid-template-columns:1fr}.page{padding:8px}.providers{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top">
    <div class="row"><div><h1>Provider Broadcast Cockpit</h1><p class="muted">Seleciona IAs, gera prompt, copia para cada provider e importa respostas para o ledger.</p></div><button class="dark" onclick="location.href='/app/home'">Home</button></div>
    <div class="hero" id="hero">A carregar...</div>
  </section>

  <section class="panel">
    <h2>1) Pedido do Oner</h2>
    <textarea id="operatorRequest" placeholder="Escreve aqui o pedido original. Este texto é preservado e nunca é substituído pela resposta da IA."></textarea>
    <div class="grid">
      <input id="projectKey" value="GOD_MODE" placeholder="Projeto, ex: GOD_MODE" />
      <select id="promptMode"><option value="development">development</option><option value="research">research</option><option value="implementation">implementation</option><option value="plain">plain</option></select>
      <label class="provider"><input type="checkbox" id="promptCritic" checked /> Prompt critic seguro</label>
    </div>
  </section>

  <section class="panel">
    <div class="row"><h2>2) Providers</h2><button class="dark" onclick="loadDefaultProfile()">Recarregar providers</button></div>
    <div class="providers" id="providers"></div>
  </section>

  <section class="panel buttons">
    <button onclick="createPlan()">Criar broadcast plan</button>
    <button class="dark" onclick="refreshPlans()">Planos recentes</button>
    <button class="dark" onclick="loadPackage()">Status</button>
  </section>

  <section class="panel" id="planPanel" style="display:none">
    <div class="row"><h2>3) Prompt para copiar</h2><button class="copy" onclick="copyPrompt()">Copiar prompt</button></div>
    <div class="promptBox" id="promptBox"></div>
    <div class="muted" id="planMeta"></div>
  </section>

  <section class="panel" id="jobsPanel" style="display:none">
    <h2>4) Respostas dos providers</h2>
    <p class="muted">Cola aqui a resposta de cada IA. Cada resposta entra no ledger como <b>ai_response</b>, nunca como decisão final.</p>
    <div class="grid" id="jobs"></div>
    <div class="buttons"><button class="ok" onclick="compareResponses()">Comparar respostas</button><button class="dark" onclick="openLedger()">Abrir cards do ledger</button></div>
  </section>

  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let currentProfile=null,currentPlan=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}
async function loadDefaultProfile(){const d=await api('/api/provider-prompt-broadcast-runtime/default-pane-profile?profile_name=visible-cockpit-'+Date.now(),{method:'POST'});currentProfile=d.profile;renderProviders(currentProfile.providers);qs('#hero').textContent='Providers carregados. Escolhe as IAs e cria o broadcast.';show(d)}
function renderProviders(providers){qs('#providers').innerHTML=(providers||[]).map(p=>`<label class="provider"><input type="checkbox" data-provider="${esc(p.provider_id)}" ${p.enabled?'checked':''}/><div><b>${esc(p.label)}</b><div class="muted">${esc(p.kind)} · ${p.requires_login_attention?'login local':'ok'}</div></div></label>`).join('')}
function selectedProviders(){return [...document.querySelectorAll('[data-provider]')].filter(x=>x.checked).map(x=>x.dataset.provider)}
async function createPlan(){const operatorRequest=qs('#operatorRequest').value.trim();if(!operatorRequest){alert('Escreve o pedido original primeiro.');return}if(!currentProfile){await loadDefaultProfile()}const body={operator_request:operatorRequest,project_key:qs('#projectKey').value.trim()||'GOD_MODE',selected_provider_ids:selectedProviders(),profile_id:currentProfile.profile_id,prompt_mode:qs('#promptMode').value,use_prompt_critic:qs('#promptCritic').checked};const d=await api('/api/provider-prompt-broadcast-runtime/create-broadcast-plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});currentPlan=d.plan;renderPlan(currentPlan);show(d)}
function renderPlan(plan){qs('#planPanel').style.display='block';qs('#jobsPanel').style.display='block';qs('#promptBox').textContent=plan.broadcast_prompt;qs('#planMeta').innerHTML=`<span class="chip">${esc(plan.plan_id)}</span> <span class="chip">Providers: ${esc(plan.selected_provider_ids.join(', '))}</span> <span class="chip">Prompt critic: ${esc(plan.use_prompt_critic)}</span>`;qs('#jobs').innerHTML=(plan.jobs||[]).map(j=>`<div class="job"><div class="row"><b>${esc(j.provider_label)}</b><span class="chip">${esc(j.provider_kind)}</span></div><button class="copy" onclick="copyPrompt()">Copiar prompt para ${esc(j.provider_label)}</button><textarea class="response" id="resp_${esc(j.provider_id)}" placeholder="Cola aqui a resposta de ${esc(j.provider_label)}"></textarea><button onclick="importResponse('${esc(j.provider_id)}')">Importar resposta</button></div>`).join('')}
async function copyPrompt(){if(!currentPlan)return;await navigator.clipboard.writeText(currentPlan.broadcast_prompt);qs('#hero').textContent='Prompt copiado. Cola na IA escolhida.'}
async function importResponse(providerId){if(!currentPlan)return;const text=qs('#resp_'+providerId).value.trim();if(!text){alert('Cola primeiro a resposta.');return}const d=await api('/api/provider-prompt-broadcast-runtime/import-provider-response',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:currentPlan.plan_id,provider_id:providerId,response_text:text,source_mode:'manual_cockpit_paste'})});show(d);qs('#hero').textContent=`Resposta de ${providerId} importada para o ledger como ai_response.`}
async function compareResponses(){if(!currentPlan)return;const d=await api('/api/provider-prompt-broadcast-runtime/compare-responses',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:currentPlan.plan_id})});show(d);qs('#hero').textContent='Comparação pronta. Revê scripts/gaps antes de decidir.'}
async function refreshPlans(){const d=await api('/api/provider-prompt-broadcast-runtime/plans');show(d)}async function loadPackage(){const d=await api('/api/provider-prompt-broadcast-runtime/package');show(d);qs('#hero').textContent='Runtime carregado. Browser automation continua desligado por segurança.'}function openLedger(){location.href='/app/provider-broadcast-cockpit#ledger'; window.open('/api/conversation-ledger-cockpit-review/package','_blank')}
loadDefaultProfile().catch(e=>{qs('#hero').textContent='Erro a carregar providers';show({error:String(e)})});
</script>
</body></html>
"""


@router.get('/app/provider-broadcast-cockpit', response_class=HTMLResponse)
async def provider_broadcast_cockpit_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/provider-prompt-broadcast', response_class=HTMLResponse)
async def provider_prompt_broadcast_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
