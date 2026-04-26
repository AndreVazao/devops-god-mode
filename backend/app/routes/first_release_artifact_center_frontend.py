from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["first-release-artifact-center-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>First Release Artifacts</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#7c2d12,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,a.btn{font:inherit;border-radius:16px;border:none;background:linear-gradient(135deg,#0284c7,#38bdf8);color:#02101b;padding:12px;font-weight:1000;text-align:center;text-decoration:none}.dark{background:#0b1220!important;color:var(--text)!important;border:1px solid var(--line)!important}.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>First Release Artifacts</h1><p class="muted">Verdade dos builds: o que dá para instalar agora e o que ainda é placeholder.</p><div class="hero" id="hero">A carregar...</div><p id="truth" class="muted"></p></section>
  <section class="panel buttons"><button id="refresh">Atualizar</button><a class="btn" href="https://github.com/AndreVazao/devops-god-mode/actions" target="_blank">GitHub Actions</a><button onclick="location.href='/app/first-use'">First Use</button><button onclick="location.href='/app/install-readiness'" class="dark">Readiness</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Artifacts</h2><div class="grid" id="artifacts"></div></section>
  <section class="panel"><h2>Próximas ações</h2><div class="grid" id="actions"></div></section>
  <section class="panel"><h2>Detalhes</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:21px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}async function load(){const d=await api('/api/first-release-artifacts/dashboard');const r=d.report||{};qs('#hero').innerHTML=`Estado: <span class="${esc(r.status||'yellow')}">${esc(r.status||'unknown')}</span>`;qs('#truth').textContent=r.release_truth||'';qs('#cards').innerHTML=card('Blockers',(r.blockers||[]).length)+card('Artifacts',(r.artifacts||[]).length)+card('EXE',(r.artifacts||[]).find(x=>x.artifact_id==='windows_exe')?.installable_now?'instalável':'não')+card('APK',(r.artifacts||[]).find(x=>x.artifact_id==='android_apk')?.placeholder?'placeholder':'real');qs('#artifacts').innerHTML=(r.artifacts||[]).map(a=>card(a.label,a.installable_now?'instalável':(a.placeholder?'placeholder':'não instalável'),a.operator_instruction)).join('');qs('#actions').innerHTML=(r.next_actions||[]).map(a=>card(a.priority,a.label,a.detail)).join('');qs('#out').textContent=JSON.stringify(d,null,2)}qs('#refresh').onclick=load;load();
</script>
</body></html>
"""


@router.get('/app/first-release-artifacts', response_class=HTMLResponse)
async def first_release_artifact_center_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/release-artifacts', response_class=HTMLResponse)
async def release_artifacts_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
