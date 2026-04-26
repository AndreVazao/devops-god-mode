from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["real-work-command-pipeline-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Real Work Command Pipeline</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#7f1d1d,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;font-weight:1000}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}textarea{width:100%;min-height:120px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:460px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Real Work Command Pipeline</h1><p class="muted">Dá uma ordem. O backend resolve o projeto pela tua prioridade e trabalha até acabar ou bloquear.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel"><textarea id="cmd">continua o God Mode até precisares do meu OK</textarea><input id="project" placeholder="Projeto opcional, ex: GOD_MODE"><div class="buttons"><button id="submit">Executar</button><button id="refresh">Atualizar</button><button onclick="location.href='/app/operator-priority'" class="dark">Prioridades</button><button onclick="location.href='/app/mobile-approval-cockpit-v2'" class="dark">Aprovações</button></div></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:20px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}async function load(){const d=await api('/api/real-work/package');const s=d.package?.status||{};const l=d.package?.latest||{};qs('#hero').textContent=`Ativo: ${s.active_project||'—'} · money priority off`;qs('#cards').innerHTML=card('Estado',s.status||'—')+card('Comandos',s.command_count||0)+card('Último projeto',l.report?.project_id||'—')+card('Último job',l.report?.job_id||'—');qs('#out').textContent=JSON.stringify(d,null,2)}async function submit(){const payload={command_text:qs('#cmd').value,requested_project:qs('#project').value.trim()||null,auto_run:true};const d=await api('/api/real-work/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});qs('#out').textContent=JSON.stringify(d,null,2);await load()}qs('#refresh').onclick=load;qs('#submit').onclick=submit;load();
</script>
</body></html>
"""


@router.get('/app/real-work', response_class=HTMLResponse)
async def real_work_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/work-command', response_class=HTMLResponse)
async def work_command_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
