from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pc-autopilot-loop-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PC Autopilot Loop</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--blue:#38bdf8;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#064e3b,#020617);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.96);border:1px solid var(--line);border-radius:22px;padding:12px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;font-weight:1000}.danger{background:linear-gradient(135deg,#991b1b,#ef4444)!important;color:white!important}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:460px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>PC Autopilot Loop</h1><p class="muted">Mantém o backend a trabalhar no PC mesmo que o APK esteja fechado. Nunca contorna aprovações.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel"><div class="grid"><label>Intervalo segundos<input id="interval" type="number" min="5" max="3600" value="30"></label><label>Rondas por ciclo<input id="rounds" type="number" min="1" max="20" value="3"></label><label>Jobs por ronda<input id="jobs" type="number" min="1" max="20" value="4"></label></div><div class="buttons"><button id="start">Ligar</button><button id="cycle">Ciclo agora</button><button id="stop" class="danger">Parar</button><button id="refresh" class="dark">Atualizar</button><button onclick="location.href='/app/operator-chat-sync-cards'" class="dark">Chat</button><button onclick="location.href='/app/mobile-approval-cockpit-v2'" class="dark">Aprovações</button></div></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Últimos ciclos</h2><div class="grid" id="cycles"></div></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);let current=null;async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:20px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}async function load(){const d=await api('/api/pc-autopilot/dashboard');current=d;const s=d.status||{};const set=s.settings||{};qs('#hero').textContent=`${s.status||'—'} · thread ${s.thread_alive?'ativa':'parada'}`;qs('#interval').value=set.interval_seconds||30;qs('#rounds').value=set.max_rounds_per_cycle||3;qs('#jobs').value=set.max_jobs_per_round||4;qs('#cards').innerHTML=card('Enabled',set.enabled?'sim':'não')+card('APK disconnect safe',s.apk_disconnect_safe?'sim':'não')+card('Approval bypass',s.approval_bypass?'sim':'não')+card('Ciclos',s.cycle_count||0);qs('#cycles').innerHTML=(d.recent_cycles||[]).slice(-8).reverse().map(x=>card(x.stop_reason||'cycle',x.processed_total||0,`${x.started_at||''} · needs operator: ${x.needs_operator?'sim':'não'}`)).join('')||'<p class="muted">Sem ciclos.</p>';qs('#out').textContent=JSON.stringify(d,null,2)}async function configureAnd(path,body={}){await api('/api/pc-autopilot/configure',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({interval_seconds:+qs('#interval').value,max_rounds_per_cycle:+qs('#rounds').value,max_jobs_per_round:+qs('#jobs').value})});const d=await api(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});qs('#out').textContent=JSON.stringify(d,null,2);await load()}qs('#start').onclick=()=>configureAnd('/api/pc-autopilot/start');qs('#stop').onclick=()=>configureAnd('/api/pc-autopilot/stop');qs('#cycle').onclick=()=>configureAnd('/api/pc-autopilot/cycle',{reason:'mobile_button_cycle'});qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/pc-autopilot', response_class=HTMLResponse)
async def pc_autopilot_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/autopilot-loop', response_class=HTMLResponse)
async def autopilot_loop_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
