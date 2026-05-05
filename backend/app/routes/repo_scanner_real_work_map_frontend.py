from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["repo-scanner-real-work-map-frontend"])

HTML = """
<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>Repo Scanner</title><style>:root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 55%);color:var(--text)}.page{padding:10px;display:grid;gap:10px}.panel{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}h1,h2{margin:.1rem 0}.muted{color:var(--muted)}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}textarea{width:100%;min-height:160px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:520px;background:#081226;border:1px solid var(--line);border-radius:18px;padding:12px}@media(max-width:760px){.buttons{grid-template-columns:1fr}}</style></head><body><div class="page"><section class="panel"><h1>Repo Scanner → Real Work Map</h1><p class="muted">Cola/lista repos. O God Mode sugere grupo/frente, encontra pares website+studio e cria cards para dúvidas.</p><div class="buttons"><button onclick="location.href='/app/home'" class="dark">Home</button><button onclick="location.href='/app/real-work-fast-path'" class="dark">Trabalho Real</button><button onclick="dashboard()">Dashboard</button></div></section><section class="panel"><h2>Repos</h2><textarea id="repos" placeholder="AndreVazao/baribudos-website&#10;AndreVazao/baribudos-studio&#10;AndreVazao/devops-god-mode">AndreVazao/devops-god-mode
AndreVazao/andreos-memory
AndreVazao/godmode-smol-ai-lab</textarea><div class="buttons"><button onclick="scan(false)">Scan seguro</button><button onclick="scan(true)">Scan + aplicar high-confidence</button><button class="dark" onclick="cards()">Criar cards revisão</button></div></section><section class="panel"><h2>Resultado</h2><pre id="out"></pre></section></div><script>const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function show(x){qs('#out').textContent=JSON.stringify(x,null,2)}function listRepos(){return qs('#repos').value.split(/\n|,/).map(x=>x.trim()).filter(Boolean)}async function scan(auto){show(await api('/api/repo-scanner-real-work-map/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({repo_full_names:listRepos(),auto_apply_high_confidence:auto})}))}async function cards(){show(await api('/api/repo-scanner-real-work-map/create-review-cards',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}))}async function dashboard(){show(await api('/api/repo-scanner-real-work-map/dashboard'))}dashboard()</script></body></html>
"""


@router.get('/app/repo-scanner-real-work-map', response_class=HTMLResponse)
async def repo_scanner_real_work_map_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/repo-scanner', response_class=HTMLResponse)
async def repo_scanner_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
