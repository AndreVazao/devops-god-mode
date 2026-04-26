from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["chat-boot-briefing-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Chat Boot Briefing</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#172554,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:24px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Chat Boot Briefing</h1><p class="muted">Cria uma mensagem inicial no chat com estado, próxima ação e cartões clicáveis.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="device" value="android-apk"><input id="thread" placeholder="thread opcional"></section>
  <section class="panel buttons"><button id="boot" class="good">Criar briefing no chat</button><button id="refresh">Atualizar</button><button id="open">Abrir chat</button><button id="fallback" class="dark">Fallback</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Briefing</h2><pre id="brief"></pre></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let dashboard=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}async function load(){const t=encodeURIComponent(qs('#tenant').value||'owner-andre');const d=encodeURIComponent(qs('#device').value||'android-apk');dashboard=await api(`/api/chat-boot-briefing/dashboard?tenant_id=${t}&device_id=${d}`);const b=dashboard.briefing||{};qs('#hero').innerHTML=`Estado: <span class="${esc(b.status||'yellow')}">${esc(b.status||'unknown')}</span>`;qs('#cards').innerHTML=card('Rota',b.recommended_route||'—')+card('Fallback',b.fallback_route||'—')+card('Aprovações',b.pending_approvals||0)+card('Projeto dinheiro',b.money_project||'—');qs('#brief').textContent=b.message||'';show(dashboard)}qs('#refresh').onclick=load;qs('#open').onclick=()=>location.href=dashboard?.briefing?.recommended_route||'/app/operator-chat-sync-cards';qs('#fallback').onclick=()=>location.href=dashboard?.briefing?.fallback_route||'/app/operator-chat-sync';qs('#boot').onclick=async()=>{const payload={tenant_id:qs('#tenant').value||'owner-andre',device_id:qs('#device').value||'android-apk',thread_id:qs('#thread').value.trim()||null};const r=await api('/api/chat-boot-briefing/boot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});show(r);qs('#thread').value=r.boot?.thread_id||'';await load()};load();
</script>
</body></html>
"""


@router.get('/app/chat-boot-briefing', response_class=HTMLResponse)
async def chat_boot_briefing_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
