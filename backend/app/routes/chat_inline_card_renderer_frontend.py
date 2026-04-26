from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["chat-inline-card-renderer-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Chat Cards</title>
  <style>
    :root{color-scheme:dark;--bg:#050816;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#07152b,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;grid-template-rows:auto 1fr auto;gap:10px}.top,.panel,.msg,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0;font-size:22px}.muted{color:var(--muted)}.chat{display:flex;flex-direction:column;gap:10px;overflow:auto;max-height:68vh}.msg{max-width:92%}.operator{align-self:flex-end;background:#14337a}.assistant{align-self:flex-start}.system{align-self:center;background:rgba(245,158,11,.12)}.card{margin-top:8px;background:rgba(8,47,73,.75)}.card h3{margin:.1rem 0}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.composer{display:grid;gap:8px}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:220px}@media(max-width:720px){.page{padding:8px}.msg{max-width:100%}.buttons{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>God Mode Chat Cards</h1><p class="muted">Conversa corrida com cartões clicáveis inline para APK/mobile.</p><span class="pill" id="thread">thread: nova</span><span class="pill" id="cards">cartões: 0</span></section>
  <section class="chat" id="chat"></section>
  <section class="panel composer"><textarea id="msg" rows="3" placeholder="Escreve como no ChatGPT: quero ganhar dinheiro, continua, revê memória..."></textarea><div class="buttons"><button id="send" class="good">Enviar</button><button class="dark" onclick="location.href='/app/operator-chat-sync'">Chat antigo</button><button class="dark" onclick="location.href='/app/chat-action-cards'">Admin cartões</button></div><pre id="out"></pre></section>
</div>
<script>
let threadId=null, openCards=[];const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function add(role,text){const b=document.createElement('div');b.className='msg '+role;b.innerHTML=`<div class="muted">${role}</div><div>${esc(text)}</div>`;qs('#chat').appendChild(b);qs('#chat').scrollTop=qs('#chat').scrollHeight}function renderCards(cards){openCards=cards||[];qs('#cards').textContent='cartões: '+openCards.length;for(const c of openCards){if(document.querySelector(`[data-card-box="${c.card_id}"]`))continue;const box=document.createElement('div');box.className='msg assistant';box.dataset.cardBox=c.card_id;box.innerHTML=`<div class="card"><h3>${esc(c.title)}</h3><p>${esc(c.body)}</p><p class="muted">${esc(c.priority)} · ${esc(c.status)}</p><div class="buttons">${(c.actions||[]).map(a=>`<button data-card="${esc(c.card_id)}" data-action="${esc(a.action_id)}">${esc(a.label)}</button>`).join('')}<button class="dark" data-dismiss="${esc(c.card_id)}">Ignorar</button></div></div>`;qs('#chat').appendChild(box)}qs('#chat').querySelectorAll('button[data-card]').forEach(b=>b.onclick=()=>execCard(b.dataset.card,b.dataset.action));qs('#chat').querySelectorAll('button[data-dismiss]').forEach(b=>b.onclick=()=>dismissCard(b.dataset.dismiss));qs('#chat').scrollTop=qs('#chat').scrollHeight}async function send(){const text=qs('#msg').value.trim();if(!text)return;qs('#msg').value='';add('operator',text);const r=await api('/api/chat-inline-card-renderer/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,thread_id:threadId})});threadId=r.thread_id;qs('#thread').textContent='thread: '+threadId;add('assistant',r.chat_result?.chat?.reply||'Recebido. Criei ações sugeridas quando aplicável.');renderCards(r.open_cards);show(r)}async function execCard(card,action){const r=await api('/api/chat-action-cards/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card_id:card,action_id:action})});add('system','Ação executada: '+(r.execution?.action_type||action));show(r);await refreshCards()}async function dismissCard(card){const r=await api('/api/chat-action-cards/dismiss',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card_id:card})});document.querySelector(`[data-card-box="${card}"]`)?.remove();show(r);await refreshCards()}async function refreshCards(){if(!threadId)return;const r=await api('/api/chat-action-cards/cards?thread_id='+encodeURIComponent(threadId)+'&status=open');renderCards(r.cards);show(r)}qs('#send').onclick=send;qs('#msg').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});add('assistant','Estou pronto. Escreve normalmente e eu mostro cartões clicáveis quando houver ação segura.');
</script>
</body></html>
"""


@router.get('/app/operator-chat-sync-cards', response_class=HTMLResponse)
async def operator_chat_sync_cards_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/chat-inline-cards', response_class=HTMLResponse)
async def chat_inline_cards_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
