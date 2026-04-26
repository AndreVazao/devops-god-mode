from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["apk-router-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode APK Start</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#38bdf8;--green:#22c55e;--warn:#f59e0b;--bad:#ef4444}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at top,#123256,#050816 58%);color:var(--text)}.page{min-height:100vh;display:grid;place-items:center;padding:16px}.box{width:min(720px,100%);background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:28px;padding:20px;box-shadow:0 20px 60px rgba(0,0,0,.35)}h1{margin:0 0 8px}.hero{font-size:28px;font-weight:1000;margin:10px 0}.muted{color:var(--muted)}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:14px}button,input,select{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:300px;margin-top:12px}.green{color:var(--green)}.yellow{color:var(--warn)}.red{color:var(--bad)}@media(max-width:720px){.hero{font-size:23px}.buttons{grid-template-columns:1fr}.box{border-radius:22px}}
  </style>
</head>
<body>
<div class="page"><main class="box"><h1>God Mode APK Start</h1><p class="muted">Vou perguntar ao backend qual é a melhor superfície para abrir.</p><div class="hero" id="hero">A resolver rota...</div><div class="buttons"><input id="tenant" value="owner-andre"><select id="prefer"><option value="auto">auto</option><option value="legacy">legacy</option><option value="home">home</option></select></div><div class="buttons"><button id="go" class="good">Abrir rota recomendada</button><button id="resolve">Resolver de novo</button><button id="fallback" class="dark">Fallback</button><button id="home" class="dark">Home</button></div><pre id="out"></pre></main></div>
<script>
let resolution=null;const qs=s=>document.querySelector(s);async function api(p){const r=await fetch(p);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}async function resolve(){try{const tenant=encodeURIComponent(qs('#tenant').value||'owner-andre');const prefer=encodeURIComponent(qs('#prefer').value||'auto');const r=await api(`/api/apk-router/resolve?tenant_id=${tenant}&device_id=apk-start&prefer=${prefer}`);resolution=r.resolution;localStorage.setItem('godmode.apk.lastRoute',resolution.route);localStorage.setItem('godmode.apk.lastFallback',resolution.fallback_route);qs('#hero').innerHTML=`Rota: <span class="green">${resolution.route}</span>`;show(r);return r}catch(e){const last=localStorage.getItem('godmode.apk.lastRoute')||'/app/home';resolution={route:last,fallback_route:'/app/operator-chat-sync',safe_fallback_route:'/app/home'};qs('#hero').innerHTML=`Backend indisponível. Última rota: <span class="yellow">${last}</span>`;show({ok:false,error:String(e),resolution});return {ok:false,resolution}}}qs('#go').onclick=async()=>{if(!resolution)await resolve();location.href=resolution.route||'/app/operator-chat-sync-cards'};qs('#resolve').onclick=resolve;qs('#fallback').onclick=()=>{const r=resolution?.fallback_route||localStorage.getItem('godmode.apk.lastFallback')||'/app/operator-chat-sync';location.href=r};qs('#home').onclick=()=>location.href='/app/home';resolve();setTimeout(()=>{if(resolution?.route)location.href=resolution.route},1800);
</script>
</body></html>
"""


@router.get('/app/apk-start', response_class=HTMLResponse)
async def apk_start_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/start', response_class=HTMLResponse)
async def apk_start_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
