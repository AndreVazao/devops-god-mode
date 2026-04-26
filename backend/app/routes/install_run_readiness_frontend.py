from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["install-run-readiness-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode Install Readiness</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#064e3b,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:30px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button{font:inherit;border-radius:16px;border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;padding:12px;font-weight:1000}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}ul{margin:8px 0;padding-left:20px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:24px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>God Mode Install Readiness</h1><p class="muted">Resposta direta: está pronto para instalar no PC e usar pelo APK?</p><div class="hero" id="hero">A carregar...</div><p id="decision" class="muted"></p></section>
  <section class="panel buttons"><button id="refresh">Atualizar</button><button onclick="location.href='/app/mobile-first-run'">First Run</button><button onclick="location.href='/app/apk-start'">APK Start</button><button onclick="location.href='/app/operator-chat-sync-cards'">Chat</button><button onclick="location.href='/app/offline-buffer'" class="dark">Offline</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Blockers</h2><div id="blockers"></div></section>
  <section class="panel"><h2>Próximas ações</h2><div id="actions"></div></section>
  <section class="panel"><h2>Resultado completo</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function list(items){return items&&items.length?`<ul>${items.map(i=>`<li><b>${esc(i.label||i.priority||i.id)}</b> <span class="muted">${esc(i.detail||i.id||'')}</span></li>`).join('')}</ul>`:'<p class="muted">Nada crítico.</p>'}async function load(){const d=await api('/api/install-run-readiness/dashboard');const r=d.report||{};qs('#hero').innerHTML=`Estado: <span class="${esc(r.status||'yellow')}">${esc(r.status||'unknown')}</span> · ${esc(r.score||0)}%`;qs('#decision').textContent=r.install_decision||'';qs('#cards').innerHTML=card('Checks',r.checks_count||0)+card('Críticos OK',`${r.passed_critical||0}/${r.critical_count||0}`)+card('Blockers',(r.blockers||[]).length)+card('Warnings',(r.warnings||[]).length);qs('#blockers').innerHTML=list(r.blockers||[]);qs('#actions').innerHTML=list(r.next_actions||[]);qs('#out').textContent=JSON.stringify(d,null,2)}qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/install-run-readiness', response_class=HTMLResponse)
async def install_run_readiness_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/install-readiness', response_class=HTMLResponse)
async def install_readiness_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
