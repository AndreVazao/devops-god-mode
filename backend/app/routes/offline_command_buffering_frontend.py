from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["offline-command-buffering-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Offline Buffer Bridge</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--accent:#38bdf8}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#312e81,#050816);color:var(--text)}.page{min-height:100vh;padding:10px;display:grid;gap:10px}.top,.panel,.card{background:rgba(15,23,42,.95);border:1px solid var(--line);border-radius:22px;padding:13px}.top h1{margin:0}.hero{font-size:28px;font-weight:1000}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.buttons{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}button,input,textarea,select{font:inherit;border-radius:16px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:12px}button{background:linear-gradient(135deg,#0284c7,#38bdf8);border:none;color:#02101b;font-weight:1000}button.good{background:linear-gradient(135deg,#16a34a,#84cc16)}button.dark{background:#0b1220;color:var(--text);border:1px solid var(--line)}pre{white-space:pre-wrap;overflow:auto;font-size:12px;max-height:420px}@media(max-width:720px){.buttons{grid-template-columns:1fr}.hero{font-size:23px}.page{padding:8px}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>Offline Buffer Bridge</h1><p class="muted">Guarda ordens do telemóvel quando o PC está offline e reenvia para jobs duráveis quando volta.</p><div class="hero" id="hero">A carregar...</div></section>
  <section class="panel grid"><input id="tenant" value="owner-andre"><select id="pc"><option value="true">PC online</option><option value="false">PC offline</option></select><select id="phone"><option value="true">Telefone online</option><option value="false">Telefone offline</option></select></section>
  <section class="panel"><textarea id="command" rows="4" placeholder="Ex: audita o God Mode e continua até precisares do meu OK"></textarea><div class="buttons"><button id="queue" class="good">Guardar ordem</button><button id="syncReplay">Sync + Replay</button><button id="refresh" class="dark">Atualizar</button><button onclick="location.href='/app/request-orchestrator'" class="dark">Ver jobs</button></div></section>
  <section class="panel buttons"><button id="connectivity">Atualizar ligação</button><button id="sync">Só sincronizar</button><button id="replay">Só replay</button><button onclick="location.href='/app/request-worker'" class="dark">Worker</button></section>
  <section class="grid" id="cards"></section>
  <section class="panel"><h2>Comandos</h2><div class="grid" id="commands"></div></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
let state=null;const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function card(a,b,c=''){return `<div class="card"><span class="muted">${esc(a)}</span><b style="font-size:22px;display:block">${esc(b)}</b><span class="muted">${esc(c)}</span></div>`}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(p){state=p;const c=p.connectivity||{};const commands=p.commands||[];const buffered=commands.filter(x=>x.sync_status==='buffered_on_phone_until_pc_returns').length;const ready=commands.filter(x=>x.sync_status==='ready_for_pc_execution').length;const replayed=commands.filter(x=>x.orchestrator_job_id).length;qs('#hero').textContent=`${c.link_mode||'—'} · ${buffered} no telefone · ${ready} prontos`;qs('#cards').innerHTML=card('PC',c.pc_online?'online':'offline')+card('Telefone',c.phone_online?'online':'offline')+card('Prontos para PC',ready)+card('Com job',replayed);qs('#commands').innerHTML=commands.slice().reverse().slice(0,12).map(x=>`<div class="card"><b>${esc(x.command_text)}</b><p>${esc(x.sync_status)} · ${esc(x.execution_status)}</p><p class="muted">job: ${esc(x.orchestrator_job_id||'—')}</p></div>`).join('')||'<p class="muted">Sem comandos.</p>'}async function load(){const p=await api('/api/offline-command-buffering/package');render(p.package);show(p)}async function setConn(){const payload={pc_online:qs('#pc').value==='true',phone_online:qs('#phone').value==='true'};show(await api('/api/offline-command-buffering/connectivity',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));await load()}async function queue(){const text=qs('#command').value.trim();if(!text)return;const payload={source_side:'phone',command_text:text,project_hint:'GOD_MODE'};show(await api('/api/offline-command-buffering/commands',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));qs('#command').value='';await load()}async function sync(){show(await api('/api/offline-command-buffering/sync',{method:'POST'}));await load()}async function replay(){const payload={tenant_id:qs('#tenant').value||'owner-andre',auto_run:true,max_commands:10};show(await api('/api/offline-command-buffering/replay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));await load()}async function syncReplay(){const payload={tenant_id:qs('#tenant').value||'owner-andre',auto_run:true,max_commands:10};show(await api('/api/offline-command-buffering/sync-and-replay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}));await load()}qs('#refresh').onclick=load;qs('#connectivity').onclick=setConn;qs('#queue').onclick=queue;qs('#sync').onclick=sync;qs('#replay').onclick=replay;qs('#syncReplay').onclick=syncReplay;load();
</script>
</body></html>
"""


@router.get('/app/offline-command-buffering', response_class=HTMLResponse)
async def offline_command_buffering_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)


@router.get('/app/offline-buffer', response_class=HTMLResponse)
async def offline_command_buffering_alias() -> HTMLResponse:
    return HTMLResponse(content=HTML)
