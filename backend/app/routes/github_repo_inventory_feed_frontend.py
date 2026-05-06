from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["github-repo-inventory-feed-frontend"])

HTML = """
<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>GitHub Repo Inventory</title><style>:root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 55%);color:var(--text)}.page{padding:10px;display:grid;gap:10px}.panel{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:22px;padding:13px}h1,h2{margin:.1rem 0}.muted{color:var(--muted)}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,textarea{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}textarea{width:100%;min-height:180px}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:520px;background:#081226;border:1px solid var(--line);border-radius:18px;padding:12px}@media(max-width:760px){.buttons{grid-template-columns:1fr}}</style></head><body><div class="page"><section class="panel"><h1>GitHub Repo Inventory Feed</h1><p class="muted">Importa inventário real/fallback manual de repos e alimenta o Repo Scanner + Real Work Map.</p><div class="buttons"><button onclick="location.href='/app/home'" class="dark">Home</button><button onclick="location.href='/app/repo-scanner-real-work-map'" class="dark">Repo Scanner</button><button onclick="dashboard()">Dashboard</button></div></section><section class="panel"><h2>Seed visto pelo connector</h2><p class="muted">Usa o snapshot de repos já visto nesta sessão pelo GitHub connector.</p><div class="buttons"><button onclick="seed()">Seed + scanner</button><button onclick="seedNoApply()" class="dark">Seed sem auto-apply</button></div></section><section class="panel"><h2>Fallback manual</h2><textarea id="repos" placeholder="AndreVazao/devops-god-mode&#10;AndreVazao/baribudos-studio&#10;AndreVazao/proventil">AndreVazao/devops-god-mode
AndreVazao/andreos-memory
AndreVazao/baribudos-studio
AndreVazao/baribudos-studio-website
AndreVazao/proventil
AndreVazao/godmode-smol-ai-lab</textarea><div class="buttons"><button onclick="manual(false)">Importar lista</button><button onclick="manual(true)">Importar + aplicar high-confidence</button></div></section><section class="panel"><h2>Resultado</h2><pre id="out"></pre></section></div><script>const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function show(x){qs('#out').textContent=JSON.stringify(x,null,2)}function listRepos(){return qs('#repos').value.split(/\n|,/).map(x=>x.trim()).filter(Boolean)}async function seed(){show(await api('/api/github-repo-inventory-feed/seed-connector-seen?auto_apply_high_confidence=true',{method:'POST'}))}async function seedNoApply(){show(await api('/api/github-repo-inventory-feed/seed-connector-seen?auto_apply_high_confidence=false',{method:'POST'}))}async function manual(auto){show(await api('/api/github-repo-inventory-feed/import-repo-names',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({repo_full_names:listRepos(),auto_apply_high_confidence:auto})}))}async function dashboard(){show(await api('/api/github-repo-inventory-feed/dashboard'))}dashboard()</script></body></html>
"""


@router.get('/app/github-repo-inventory-feed', response_class=HTMLResponse)
async def github_repo_inventory_feed_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/repo-inventory', response_class=HTMLResponse)
async def repo_inventory_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
