from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["god-mode-home-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Home</title>
  <style>
    :root{color-scheme:dark;--bg:#050816;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 55%);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px;box-shadow:0 14px 34px rgba(0,0,0,.32)}h1,h2{margin:.1rem 0}.hero{font-size:28px;font-weight:1000;line-height:1.1}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}button.stop{background:linear-gradient(135deg,#991b1b,#ef4444);color:white}.chat{display:grid;gap:8px;max-height:44vh;overflow:auto}.msg{padding:10px;border-radius:18px;border:1px solid var(--line);background:#0b1220;white-space:pre-wrap}.operator{margin-left:20px;background:#111827}.assistant{margin-right:20px;background:#0f1b35}.light{display:inline-flex;border-radius:999px;padding:7px 10px;font-weight:900}.green{background:#052e16;color:#86efac}.yellow{background:#422006;color:#fde68a}.blue{background:#082f49;color:#7dd3fc}.red{background:#450a0a;color:#fecaca}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:320px}@media(max-width:760px){.hero{font-size:23px}.buttons{grid-template-columns:1fr}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>God Mode</h1><p class="muted">Home principal. Chat, autopilot, aprovações e prioridade do operador num só sítio.</p><div class="hero" id="hero">A carregar...</div><div id="light"></div></section>
  <section class="panel buttons"><button id="continue">Continuar</button><button id="artifacts" class="dark">APK/EXE</button><button id="install" class="dark">Instalar/1º arranque</button><button id="start">Ligar PC Autopilot</button><button id="stop" class="stop">Parar</button><button id="ready" class="dark">Pronto para usar</button><button id="approve" class="dark">Aprovar próximo</button><button onclick="location.href='/app/operator-chat-sync-cards'" class="dark">Chat completo</button><button onclick="location.href='/app/mobile-approval-cockpit-v2'" class="dark">Problemas/OK</button></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Chat rápido</h2><div class="chat" id="chat"></div><textarea id="msg" rows="3" placeholder="Dá uma ordem: continua o projeto, revê problemas, cria próxima fase..."></textarea><input id="project" placeholder="Projeto opcional, ex: GOD_MODE, PROVENTIL"><div class="buttons"><button id="send">Enviar e executar</button><button id="refresh" class="dark">Atualizar</button><button id="driving" class="dark">Modo condução</button></div></section>
  <section class="panel"><h2>Ações principais</h2><div class="buttons" id="actions"></div></section>
  <section class="panel"><h2>Último resultado</h2><pre id="out"></pre></section>
</div>
<script>
let state={};const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:23px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function addMsg(role,text){const box=document.createElement('div');box.className='msg '+(role==='operator'?'operator':'assistant');box.textContent=text;qs('#chat').appendChild(box);qs('#chat').scrollTop=qs('#chat').scrollHeight}async function post(path,body={}){const r=await api(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});show(r);await load();return r}function render(d){state=d;const l=d.traffic_light||{};const ready=d.ready_to_use||{};const install=d.install_first_run||{};const artifacts=d.artifacts_center||{};qs('#hero').textContent=d.operator_message||((l.label||'Pronto')+' · '+(d.next_task?.label||''));qs('#light').innerHTML=`<span class="light ${esc(l.color||'blue')}">${esc(l.label||'Pronto')}</span>`;qs('#summary').innerHTML=card('Projeto ativo',d.active_project||'—')+card('Pronto para usar',(ready.readiness_score??0)+'%',ready.status||'—')+card('Instalação',(install.done_count??0)+' passos',install.status||'—')+card('APK/EXE',artifacts.artifact_count??0,artifacts.status||'—')+card('PC Autopilot',d.pc_autopilot?.status||'—')+card('Aprovações',d.approvals?.count||0)+card('Próxima tarefa',d.next_task?.label||'—');qs('#actions').innerHTML=(d.quick_actions||[]).map(a=>a.route?`<button class="dark" onclick="location.href='${esc(a.route)}'">${esc(a.label)}</button>`:`<button data-endpoint="${esc(a.endpoint)}">${esc(a.label)}</button>`).join('');qs('#actions').querySelectorAll('button[data-endpoint]').forEach(b=>b.onclick=()=>post(b.dataset.endpoint,{}));show(d)}async function load(){render(await api('/api/god-mode-home/dashboard'))}qs('#continue').onclick=()=>post('/api/god-mode-home/continue',{command_text:null,requested_project:qs('#project').value.trim()||null});qs('#artifacts').onclick=async()=>show(await api('/api/artifacts-center/dashboard'));qs('#install').onclick=async()=>show(await api('/api/install-first-run/guide'));qs('#start').onclick=()=>post('/api/god-mode-home/start-autopilot');qs('#stop').onclick=()=>post('/api/god-mode-home/stop-autopilot');qs('#ready').onclick=async()=>show(await api('/api/ready-to-use/checklist'));qs('#approve').onclick=()=>post('/api/god-mode-home/approve-next',{});qs('#refresh').onclick=load;qs('#driving').onclick=async()=>show(await api('/api/god-mode-home/driving-mode'));qs('#send').onclick=async()=>{const text=qs('#msg').value.trim();if(!text)return;qs('#msg').value='';addMsg('operator',text);const r=await post('/api/god-mode-home/chat',{message:text,requested_project:qs('#project').value.trim()||null});const rep=r.result?.report;addMsg('assistant',rep?`Projeto: ${rep.resolved_project_id}\nJob: ${rep.job_id}\nStop: ${rep.autopilot_stop_reason||'—'}`:'Ordem enviada.');};qs('#msg').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();qs('#send').click()}});load();
</script>
</body></html>
"""


@router.get('/app/god-mode-home', response_class=HTMLResponse)
async def god_mode_home_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/home', response_class=HTMLResponse)
async def god_mode_home_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/god-mode', response_class=HTMLResponse)
async def god_mode_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
