from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pc-mobile-pairing-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PC Mobile Pairing</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#1d4ed8,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button{font:inherit;border-radius:16px;border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;padding:12px;font-weight:1000}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}code{font-size:13px;word-break:break-all}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>PC Mobile Pairing</h1><p class="muted">Usa o APK em Auto. Se falhar, copia o URL recomendado daqui.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel buttons"><button id="refresh">Atualizar</button><button onclick="location.href='/app/apk-start'">APK Start</button><button onclick="location.href='/app/first-use'">First Use</button><button onclick="location.href='/app/operator-chat-sync-cards'" class="dark">Chat</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>URLs encontrados no PC</h2><div class="grid" id="urls"></div></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:20px;display:block"><code>${esc(b)}</code></b><span class="muted">${esc(c)}</span></div>`}async function copyText(t){try{await navigator.clipboard.writeText(t);alert('Copiado: '+t)}catch(e){prompt('Copia este URL:',t)}}async function load(){const d=await api('/api/pc-mobile-pairing/dashboard');const p=d.package||{};const rec=p.recommended||{};qs('#hero').textContent=rec.base_url?`Recomendado: ${rec.base_url}`:'Sem URL recomendado';qs('#cards').innerHTML=card('Porta',p.port||'8000')+card('Recomendado',rec.base_url||'—','colar no APK se Auto falhar')+card('Health',rec.health_url||'—')+card('Start',rec.apk_start_url||'—');qs('#urls').innerHTML=(p.urls||[]).map(u=>`<div class="card"><b>${esc(u.recommended_for_phone?'Recomendado':'Local')}</b><p><code>${esc(u.base_url)}</code></p><p class="muted">${esc(u.apk_start_url)}</p><button onclick="copyText('${esc(u.base_url)}')">Copiar URL</button></div>`).join('')||'<p class="muted">Sem URLs.</p>';qs('#out').textContent=JSON.stringify(d,null,2)}qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/pc-mobile-pairing', response_class=HTMLResponse)
async def pc_mobile_pairing_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/pairing', response_class=HTMLResponse)
async def pairing_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
