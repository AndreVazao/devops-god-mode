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
    :root{color-scheme:dark;--bg:#050816;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 55%);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px;box-shadow:0 14px 34px rgba(0,0,0,.32)}h1,h2{margin:.1rem 0}.hero{font-size:28px;font-weight:1000;line-height:1.1}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}button.money{background:linear-gradient(135deg,#16a34a,#84cc16)}.chat{display:grid;gap:8px;max-height:44vh;overflow:auto}.msg{padding:10px;border-radius:18px;border:1px solid var(--line);background:#0b1220}.operator{margin-left:20px;background:#111827}.assistant{margin-right:20px;background:#0f1b35}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}.critical{color:var(--bad)}.high{color:var(--warn)}.ok{color:var(--green)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:320px}@media(max-width:760px){.hero{font-size:23px}.top,.panel,.card{border-radius:18px}.buttons{grid-template-columns:1fr}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top">
    <h1>God Mode Home</h1>
    <p class="muted">Entrada principal mobile/APK. Conversa corrida primeiro, botões grandes quando precisares.</p>
    <div class="hero" id="hero">A calcular próxima ação...</div>
  </section>
  <section class="panel buttons">
    <button id="next" class="money">Executar recomendado</button>
    <button onclick="location.href='/app/operator-chat-sync'">Chat corrido</button>
    <button onclick="location.href='/app/money-command-center'">Ganhar dinheiro</button>
    <button onclick="location.href='/app/mobile-approval-cockpit-v2'">Aprovações</button>
  </section>
  <section class="grid" id="summary"></section>
  <section class="panel">
    <h2>Conversa corrida</h2>
    <div class="chat" id="chat"></div>
    <textarea id="msg" rows="3" placeholder="Escreve como no ChatGPT: continua, quero ganhar dinheiro, revê memória..."></textarea>
    <div class="buttons"><button id="send">Enviar</button><button class="dark" id="driving">Modo condução</button></div>
  </section>
  <section class="panel"><h2>Ações rápidas</h2><div class="buttons" id="buttons"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let state={},threadId=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function addMsg(role,text){const box=document.createElement('div');box.className='msg '+(role==='operator'?'operator':'assistant');box.textContent=text;qs('#chat').appendChild(box);qs('#chat').scrollTop=qs('#chat').scrollHeight}function render(d){state=d;qs('#hero').textContent=d.operator_message||'Pronto.';const s=d.summary||{};qs('#summary').innerHTML=card('Readiness',s.readiness||'—')+card('Aprovações',s.pending_approvals||0)+card('Chat pendente',s.chat_waiting_threads||0)+card('Top dinheiro',s.top_money_project||'—');qs('#buttons').innerHTML=(d.one_tap_buttons||[]).map(b=>`<button data-id="${esc(b.button_id)}">${esc(b.label)}</button>`).join('')+(d.open_buttons||[]).map(b=>`<button class="dark" onclick="location.href='${esc(b.url)}'">${esc(b.label)}</button>`).join('');qs('#buttons').querySelectorAll('button[data-id]').forEach(btn=>btn.onclick=()=>oneTap(btn.dataset.id));show(d)}async function load(){render(await api('/api/god-mode-home/dashboard'))}async function oneTap(id){const r=await api('/api/god-mode-home/one-tap',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action_id:id})});show(r);addMsg('assistant',r.event?.label||'Ação executada.');await load()}async function send(){const text=qs('#msg').value.trim();if(!text)return;qs('#msg').value='';addMsg('operator',text);const r=await api('/api/god-mode-home/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,thread_id:threadId})});threadId=r.thread_id;addMsg('assistant',r.reply);show(r);await load()}qs('#send').onclick=send;qs('#msg').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});qs('#next').onclick=()=>{const n=state.next_action||{};if(n.url)location.href=n.url;else oneTap(n.action_id||'one-tap-continue-god-mode')};qs('#driving').onclick=async()=>show(await api('/api/god-mode-home/driving-mode'));load();
</script>
</body></html>
"""


@router.get('/app/god-mode-home', response_class=HTMLResponse)
async def god_mode_home_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/home', response_class=HTMLResponse)
async def god_mode_home_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
