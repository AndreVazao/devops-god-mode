from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["chat-action-cards-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Chat Action Cards</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#082f49,#070b14);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0;font-size:22px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:900}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px;margin:2px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:300px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Chat Action Cards</h1><p class="muted">Cartões clicáveis que aparecem dentro da conversa corrida do APK.</p></section>
  <section class="panel"><textarea id="msg" rows="3" placeholder="quero ganhar dinheiro / continua / revê memória"></textarea><div class="buttons"><button id="create" class="good">Criar cartões a partir do chat</button><button onclick="location.href='/app/operator-chat-sync'">Abrir chat corrido</button></div></section>
  <section class="grid" id="summary"></section>
  <section class="panel"><h2>Cartões abertos</h2><div class="grid" id="cards"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){qs('#summary').innerHTML=card('Cartões',d.card_count||0)+card('Abertos',d.open_count||0)+card('Alta prioridade',d.high_priority_open_count||0);qs('#cards').innerHTML=(d.recent_cards||[]).filter(c=>c.status==='open').reverse().map(c=>`<div class="card"><b>${esc(c.title)}</b><p>${esc(c.body)}</p><p>${(c.actions||[]).map(a=>`<button data-card="${esc(c.card_id)}" data-action="${esc(a.action_id)}">${esc(a.label)}</button>`).join('')}</p><button class="dark" data-dismiss="${esc(c.card_id)}">Ignorar</button><p class="muted">${esc(c.thread_id)}</p></div>`).join('')||'<p class="muted">Sem cartões abertos.</p>';qs('#cards').querySelectorAll('button[data-card]').forEach(b=>b.onclick=()=>exec(b.dataset.card,b.dataset.action));qs('#cards').querySelectorAll('button[data-dismiss]').forEach(b=>b.onclick=()=>dismiss(b.dataset.dismiss));show(d)}async function load(){render(await api('/api/chat-action-cards/dashboard'))}async function exec(card,action){show(await api('/api/chat-action-cards/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card_id:card,action_id:action})}));load()}async function dismiss(card){show(await api('/api/chat-action-cards/dismiss',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card_id:card})}));load()}qs('#create').onclick=async()=>{const m=qs('#msg').value.trim()||'quero ganhar dinheiro';show(await api('/api/chat-action-cards/from-home-chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})}));qs('#msg').value='';load()};load();
</script>
</body></html>
"""


@router.get('/app/chat-action-cards', response_class=HTMLResponse)
async def chat_action_cards_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
