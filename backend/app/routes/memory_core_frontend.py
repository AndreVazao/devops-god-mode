from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["memory-core-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AndreOS Memory Core</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --ok:#22c55e; --danger:#ef4444; }
    *{box-sizing:border-box} body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#09101d,#0b1220);color:var(--text)}
    .page{min-height:100vh;padding:14px;display:grid;gap:14px}.topbar,.panel,.card{background:var(--panel);border:1px solid var(--line);border-radius:18px}.topbar{padding:14px;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}h1{margin:0;font-size:20px}p{margin:5px 0 0;color:var(--muted)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.panel{padding:14px;overflow:auto}.card{padding:12px;background:rgba(15,23,41,.75);display:grid;gap:8px;margin-bottom:10px}input,textarea,button{font:inherit;border-radius:14px;border:1px solid var(--line);background:#0f1729;color:var(--text);padding:10px 12px}textarea{min-height:100px;resize:vertical}button{background:var(--accent);border:none;font-weight:700;cursor:pointer}.muted{color:var(--muted)}pre{white-space:pre-wrap;overflow:auto;font-size:12px}
    @media(max-width:900px){.grid{grid-template-columns:1fr}.page{padding:8px}}
  </style>
</head>
<body>
  <div class="page">
    <section class="topbar"><div><h1>AndreOS Memory Core</h1><p>Memória Obsidian persistente por projeto.</p></div><button id="initBtn">Inicializar memória</button></section>
    <section class="grid">
      <div class="panel"><h2>Projeto</h2><input id="project" value="GOD_MODE"><button id="readBtn">Ler memória</button><button id="contextBtn">Gerar contexto IA</button><button id="obsidianBtn">Abrir Obsidian</button></div>
      <div class="panel"><h2>Registar</h2><textarea id="text" placeholder="Decisão, histórico ou tarefa..."></textarea><button id="decisionBtn">Guardar decisão</button><button id="historyBtn">Guardar histórico</button><button id="backlogBtn">Adicionar backlog</button><button id="sessionBtn">Atualizar última sessão</button></div>
    </section>
    <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
  </div>
<script>
const qs=s=>document.querySelector(s); async function api(path,opts){const r=await fetch(path,opts); const t=await r.text(); let j; try{j=JSON.parse(t)}catch{j={raw:t}}; if(!r.ok) throw new Error(t); return j} function show(v){qs('#out').textContent=JSON.stringify(v,null,2)} function p(){return qs('#project').value||'GOD_MODE'} function body(o){return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)}}
qs('#initBtn').onclick=async()=>show(await api('/api/memory-core/initialize',{method:'POST'}));
qs('#readBtn').onclick=async()=>show(await api('/api/memory-core/projects/'+encodeURIComponent(p())));
qs('#contextBtn').onclick=async()=>show(await api('/api/memory-core/context/'+encodeURIComponent(p())+'?max_chars=6000'));
qs('#obsidianBtn').onclick=async()=>{const r=await api('/api/memory-core/obsidian/'+encodeURIComponent(p())+'/MEMORIA_MESTRE.md'); show(r); if(r.open_uri) location.href=r.open_uri};
qs('#decisionBtn').onclick=async()=>show(await api('/api/memory-core/decisions',body({project_name:p(),decision:qs('#text').value,reason:'Registado pelo cockpit'})));
qs('#historyBtn').onclick=async()=>show(await api('/api/memory-core/history',body({project_name:p(),action:qs('#text').value,result:'Registado pelo cockpit'})));
qs('#backlogBtn').onclick=async()=>show(await api('/api/memory-core/backlog',body({project_name:p(),task:qs('#text').value,priority:'medium'})));
qs('#sessionBtn').onclick=async()=>show(await api('/api/memory-core/last-session',body({project_name:p(),summary:qs('#text').value,next_steps:'Continuar a partir da memória AndreOS'})));
</script>
</body></html>
"""


@router.get('/app/memory-core', response_class=HTMLResponse)
async def memory_core_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
