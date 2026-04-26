from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["apk-launch-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>APK Launch Manifest</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#052e16,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0;font-size:22px}.hero{font-size:30px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--warn)}.red{color:var(--bad)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:360px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:24px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>APK Launch Manifest</h1><p class="muted">O APK pergunta aqui qual é a rota principal, fallback e capacidades disponíveis.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><input id="device" value="android-apk"></section>
  <section class="panel buttons"><button id="refresh" class="good">Atualizar manifest</button><button id="openDefault">Abrir rota principal</button><button id="openFallback" class="dark">Abrir fallback</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Botões seguros</h2><div class="buttons" id="safeButtons"></div></section>
  <section class="panel"><h2>Manifest</h2><pre id="out"></pre></section>
</div>
<script>
let manifest=null;const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(d){manifest=d.manifest||{};const h=d.health||{};const lp=manifest.launch_policy||{};qs('#hero').innerHTML=`Estado <span class="${esc(h.status||'yellow')}">${esc(h.status||'unknown')}</span>`;qs('#cards').innerHTML=card('Rota principal',lp.default_route||'—')+card('Fallback',lp.fallback_route||'—')+card('Home',lp.home_route||'—')+card('Device',manifest.device_id||'—');qs('#safeButtons').innerHTML=(manifest.safe_buttons||[]).map(b=>`<button onclick="location.href='${esc(b.route)}'">${esc(b.label)}</button>`).join('');show(d)}async function load(){const tenant=encodeURIComponent(qs('#tenant').value||'owner-andre');const device=encodeURIComponent(qs('#device').value||'android-apk');render(await api(`/api/apk-launch/dashboard?tenant_id=${tenant}&device_id=${device}`))}qs('#refresh').onclick=load;qs('#openDefault').onclick=()=>{const r=manifest?.launch_policy?.default_route||'/app/operator-chat-sync-cards';location.href=r};qs('#openFallback').onclick=()=>{const r=manifest?.launch_policy?.fallback_route||'/app/operator-chat-sync';location.href=r};load();
</script>
</body></html>
"""


@router.get('/app/apk-launch', response_class=HTMLResponse)
async def apk_launch_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
