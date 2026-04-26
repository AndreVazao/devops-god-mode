from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["mobile-first-run-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode First Run</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#064e3b,#050816 62%);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:24px;padding:14px}.top h1{margin:0}.hero{font-size:32px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:360px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:25px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>God Mode First Run</h1><p class="muted">Teste rápido para saber se o APK/mobile está pronto.</p><div class="hero" id="hero">A testar...</div><p id="message" class="muted"></p></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="device" value="android-apk"></section>
  <section class="panel buttons"><button id="start" class="good">Entrar no God Mode</button><button id="check">Testar de novo</button><button id="fallback" class="dark">Fallback</button><button id="home" class="dark">Home</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
let dashboard=null;const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}async function load(){const tenant=encodeURIComponent(qs('#tenant').value||'owner-andre');const device=encodeURIComponent(qs('#device').value||'android-apk');dashboard=await api(`/api/mobile-first-run/dashboard?tenant_id=${tenant}&device_id=${device}`);const c=dashboard.check||{};qs('#hero').innerHTML=`Estado: <span class="${esc(c.status||'yellow')}">${esc(c.status||'unknown')}</span>`;qs('#message').textContent=c.operator_message||'';qs('#cards').innerHTML=card('Rota recomendada',c.recommended_route||'—')+card('Fallback',c.fallback_route||'—')+card('Falhas',(c.failed_components||[]).length)+card('Avisos',(c.warning_components||[]).length);show(dashboard)}qs('#check').onclick=load;qs('#start').onclick=async()=>{const tenant=encodeURIComponent(qs('#tenant').value||'owner-andre');const device=encodeURIComponent(qs('#device').value||'android-apk');const s=await api(`/api/mobile-first-run/start?tenant_id=${tenant}&device_id=${device}`);show(s);location.href=s.start?.open_route||'/app/apk-start'};qs('#fallback').onclick=()=>location.href=dashboard?.check?.fallback_route||'/app/operator-chat-sync';qs('#home').onclick=()=>location.href='/app/home';load();
</script>
</body></html>
"""


@router.get('/app/mobile-first-run', response_class=HTMLResponse)
async def mobile_first_run_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/first-run', response_class=HTMLResponse)
async def mobile_first_run_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
