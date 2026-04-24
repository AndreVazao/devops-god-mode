from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["learning-router-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Learning Router</title>
  <style>
    :root{color-scheme:dark;--bg:#07101e;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#a78bfa;--ok:#22c55e;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#111827,#07101e);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px}.top{padding:14px;position:sticky;top:0;z-index:2}.top h1{margin:0;font-size:20px}.top p{margin:5px 0 0;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.panel{padding:12px}.card{padding:12px;background:rgba(17,28,49,.8);display:grid;gap:8px}button,select,textarea,input{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#7c3aed,#a78bfa);border:none;font-weight:900}textarea{width:100%;min-height:110px;resize:vertical}.muted{color:var(--muted)}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px}pre{white-space:pre-wrap;overflow:auto;font-size:12px}@media(max-width:720px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Learning Router</h1><p>Conversa normal. Se entender, encaminha. Se não entender, guarda para aprender.</p></section>
  <section class="panel"><h2>Mensagem natural</h2><div class="row"><select id="project"><option>GOD_MODE</option><option>PROVENTIL</option><option>VERBAFORGE</option><option>BOT_LORDS_MOBILE</option><option>ECU_REPRO</option><option>BUILD_CONTROL_CENTER</option></select><button id="send">Interpretar / Encaminhar</button></div><textarea id="msg" placeholder="Ex: vê se os builds do God Mode estão bons e diz o próximo passo..."></textarea></section>
  <section class="panel"><h2>Ensinar frase</h2><div class="row"><input id="phrase" placeholder="frase ou expressão"><select id="intent"><option>continue_project</option><option>deep_audit</option><option>build_check</option><option>memory_review</option><option>fix_plan</option><option>delivery_summary</option></select></div><button id="learn">Aprender</button></section>
  <section class="grid" id="stats"></section>
  <section class="panel"><h2>Desconhecidos recentes</h2><div id="unknowns"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:24px">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}
function render(d){const s=d.stats||{};qs('#stats').innerHTML=card('Tratados',s.handled||0)+card('Desconhecidos',s.unknown||0)+card('Padrões',d.pattern_count||0)+card('Intents',(d.intents||[]).length);qs('#unknowns').innerHTML=(d.recent_unknowns||[]).map(x=>`<div class="card"><b>${esc(x.message)}</b><span class="muted">${esc(x.project)} · ${esc(x.created_at)}</span></div>`).join('')||'<p class="muted">Sem desconhecidos.</p>';show(d)}
async function load(){const d=await api('/api/learning-router/dashboard');render(d)}
qs('#send').onclick=async()=>{const r=await api('/api/learning-router/route',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:qs('#msg').value,project_hint:qs('#project').value})});show(r);load()};
qs('#learn').onclick=async()=>{const r=await api('/api/learning-router/learn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phrase:qs('#phrase').value,intent:qs('#intent').value,project:qs('#project').value})});show(r);load()};
load();setInterval(load,15000);
</script>
</body></html>
"""


@router.get('/app/learning-router', response_class=HTMLResponse)
async def learning_router_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
