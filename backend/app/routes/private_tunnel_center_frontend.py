from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["private-tunnel-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Private Tunnel Center</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#0f766e,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button{font:inherit;border-radius:16px;border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;padding:12px;font-weight:1000}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}code{font-size:13px;word-break:break-all}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}textarea{width:100%;min-height:120px;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Private Tunnel Center</h1><p class="muted">Ligação APK → PC quando estás fora da rede local.</p><div class="hero" id="hero">A carregar...</div><p id="instruction" class="muted"></p></section>
  <section class="panel buttons"><button id="refresh">Atualizar</button><button id="copyBase">Copiar URL</button><button id="copyPayload">Copiar payload</button><button onclick="location.href='/app/pairing'" class="dark">Pairing LAN</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Pairing não secreto</h2><div class="grid" id="pairingCards"></div><textarea id="pairingText" readonly></textarea><p class="muted">Isto não é QR scannable ainda. É payload seguro para copiar/colar. QR real fica para fase própria.</p></section>
  <section class="panel"><h2>Providers</h2><div class="grid" id="providers"></div></section>
  <section class="panel"><h2>Passos na rua</h2><div class="grid" id="steps"></div></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);let current=null;async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:20px;display:block"><code>${esc(b)}</code></b><span class="muted">${esc(c)}</span></div>`}async function copyText(t){try{await navigator.clipboard.writeText(t);alert('Copiado')}catch(e){prompt('Copia:',t)}}async function load(){const d=await api('/api/private-tunnel/dashboard');current=d;const r=d.report||{};const p=r.pairing_payload||{};qs('#hero').innerHTML=`Estado: <span class="${esc(r.status||'yellow')}">${esc(r.status||'unknown')}</span> · recomendado: ${esc(r.recommended_provider||'tailscale')}`;qs('#instruction').textContent=r.apk_instruction||'';qs('#cards').innerHTML=card('Local',r.local_base_url||'—')+card('Blockers',(r.blockers||[]).length)+card('Guarda segredos',r.security?.stores_tokens?'sim':'não')+card('Login manual',r.security?.manual_login_required?'sim':'não');qs('#pairingCards').innerHTML=card('Base URL',p.payload?.base_url||'—')+card('Deep link',p.deep_link||'—')+card('Contém segredo',p.security?.contains_secret?'sim':'não')+card('QR status',p.qr_status||'—');qs('#pairingText').value=p.payload_json||'';qs('#providers').innerHTML=(r.providers||[]).map(x=>card(x.label,x.apk_base_url||x.operator_note,`instalado: ${x.installed?'sim':'não'} · recomendado: ${x.recommended?'sim':'não'}`)).join('');qs('#steps').innerHTML=(r.street_mode_steps||[]).map(s=>card('Passo '+s.step,s.label,s.detail)).join('');qs('#out').textContent=JSON.stringify(d,null,2)}qs('#refresh').onclick=load;qs('#copyBase').onclick=()=>copyText(current?.report?.pairing_payload?.payload?.base_url||'');qs('#copyPayload').onclick=()=>copyText(current?.report?.pairing_payload?.payload_json||'');load();
</script>
</body></html>
"""


@router.get('/app/private-tunnel', response_class=HTMLResponse)
async def private_tunnel_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/street-mode', response_class=HTMLResponse)
async def street_mode_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
