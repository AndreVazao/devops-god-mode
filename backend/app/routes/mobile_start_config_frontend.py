from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["mobile-start-config-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mobile Start Config</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#082f49,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.red{color:var(--bad)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:380px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Mobile Start Config</h1><p class="muted">Configuração versionada para o APK/WebView abrir sempre a rota certa.</p><div class="hero" id="hero">A validar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="device" value="android-apk"></section>
  <section class="panel buttons"><button id="refresh" class="good">Atualizar</button><button id="start">Abrir Start</button><button id="route" class="dark">Abrir rota resolvida</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Config / Plano</h2><pre id="out"></pre></section>
</div>
<script>
let plan=null;const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}async function load(){const tenant=encodeURIComponent(qs('#tenant').value||'owner-andre');const device=encodeURIComponent(qs('#device').value||'android-apk');const d=await api(`/api/mobile-start-config/dashboard?tenant_id=${tenant}&device_id=${device}`);plan=d.plan||{};qs('#hero').innerHTML=`Validação: <span class="${plan.validation_status==='green'?'green':'red'}">${esc(plan.validation_status||'unknown')}</span>`;qs('#cards').innerHTML=card('Abrir primeiro',plan.open_first||'—')+card('Rota resolvida',plan.resolved_route||'—')+card('Fallback',plan.fallback_route||'—')+card('Home segura',plan.safe_home_route||'—');show(d)}qs('#refresh').onclick=load;qs('#start').onclick=()=>location.href='/app/apk-start';qs('#route').onclick=()=>location.href=plan?.resolved_route||'/app/operator-chat-sync-cards';load();
</script>
</body></html>
"""


@router.get('/app/mobile-start-config', response_class=HTMLResponse)
async def mobile_start_config_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
