from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["operator-chat-sync-cards-real-work-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Chat</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--blue:#38bdf8;--green:#22c55e;--red:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#0f172a,#020617);color:var(--text)}.page{min-height:100vh;display:grid;grid-template-rows:auto 1fr auto;gap:10px;padding:10px}.top,.composer,.card{background:rgba(15,23,42,.96);border:1px solid var(--line);border-radius:22px;padding:12px}.top{display:flex;justify-content:space-between;gap:10px;align-items:center}.top h1{margin:0;font-size:20px}.muted{color:var(--muted);font-size:13px}.chat{display:flex;flex-direction:column;gap:10px;overflow:auto}.msg{border:1px solid var(--line);border-radius:20px;padding:12px;max-width:92%;white-space:pre-wrap}.user{align-self:flex-end;background:#1d4ed8}.bot{align-self:flex-start;background:#111827}.system{align-self:center;background:#3f2d0b}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;font-weight:1000}.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}textarea{width:100%;min-height:90px}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:6px 10px;font-size:12px;color:var(--muted)}@media(max-width:720px){.page{padding:8px}.top{display:grid}.grid{grid-template-columns:1fr}.msg{max-width:100%}}
  </style>
</head>
<body>
<div class="page">
  <header class="top"><div><h1>God Mode Chat</h1><div class="muted">Chat principal ligado ao backend real. O backend trabalha até concluir ou pedir o teu OK.</div></div><div><span class="pill" id="projectPill">projeto: automático</span></div></header>
  <main class="chat" id="chat"></main>
  <section class="composer">
    <textarea id="message" placeholder="Escreve a ordem. Ex: continua o God Mode até precisares do meu OK">continua o God Mode até precisares do meu OK</textarea>
    <input id="project" placeholder="Projeto opcional, ex: GOD_MODE, PROVENTIL, VERBAFORGE">
    <div class="grid"><button id="send">Enviar e executar</button><button id="refresh" class="dark">Atualizar</button><button onclick="location.href='/app/operator-priority'" class="dark">Prioridades</button><button onclick="location.href='/app/mobile-approval-cockpit-v2'" class="dark">Aprovações</button></div>
  </section>
</div>
<script>
const qs=s=>document.querySelector(s);const chat=qs('#chat');let last=null;function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function add(role,text){const d=document.createElement('div');d.className='msg '+role;d.textContent=text;chat.appendChild(d);chat.scrollTop=chat.scrollHeight}async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function renderReport(r){if(!r){return}qs('#projectPill').textContent='projeto: '+(r.resolved_project_id||'—');add('bot',`Recebido.\nProjeto: ${r.resolved_project_id||'—'}\nIntent: ${r.intent||'—'}\nJob: ${r.job_id||'—'} · ${r.job_status||'—'}\nWorker: ${r.worker_tick_ran?'sim':'não'}\nPrioridade: ordem do operador.\n\nSe bloquear, abre Aprovações.`)}async function load(){try{const d=await api('/api/operator-chat-real-work/latest');last=d;chat.innerHTML='';add('system','Chat pronto. As mensagens entram no pipeline real do backend.');if(d.report)renderReport(d.report)}catch(e){add('system','Falha a carregar estado: '+e.message)}}async function send(){const message=qs('#message').value.trim();if(!message)return;const requested_project=qs('#project').value.trim()||null;add('user',message);qs('#message').value='';try{const d=await api('/api/operator-chat-real-work/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,requested_project,auto_run:true})});last=d;renderReport(d.report)}catch(e){add('system','Erro: '+e.message)}}qs('#send').onclick=send;qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/operator-chat-sync-cards', response_class=HTMLResponse)
async def operator_chat_sync_cards_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/chat', response_class=HTMLResponse)
async def chat_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
