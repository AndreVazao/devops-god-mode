from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ai-handoff-frontend"])

HTML = """
<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode AI Handoff</title>
  <style>
    :root{color-scheme:dark;--panel:#0f172a;--line:#26344f;--text:#eef5ff;--muted:#9fb0d0;--accent:#f97316;--ok:#22c55e}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#1c1207,#070b14);color:var(--text)}.page{min-height:100vh;padding:12px;display:grid;gap:12px}.top,.panel,.card{background:rgba(15,23,42,.94);border:1px solid var(--line);border-radius:20px}.top,.panel,.card{padding:12px}.top h1{margin:0;font-size:20px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}button,select,textarea,input{font:inherit;border-radius:15px;border:1px solid var(--line);background:#0b1220;color:var(--text);padding:11px}button{background:linear-gradient(135deg,#ea580c,#fb923c);border:none;font-weight:900}textarea{width:100%;min-height:140px;resize:vertical}pre{white-space:pre-wrap;overflow:auto;font-size:12px}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:5px 8px;font-size:12px}@media(max-width:720px){.row{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="page">
  <section class="top"><h1>AI Handoff Bridge</h1><p class="muted">Quando o God Mode não entende, prepara prompt para ChatGPT/Gemini/Claude/Grok/DeepSeek, com aprovação.</p></section>
  <section class="panel row"><select id="provider"><option>chatgpt</option><option>gemini</option><option>claude</option><option>grok</option><option>deepseek</option></select><button id="latest">Criar handoff do último desconhecido</button></section>
  <section class="panel"><h2>Handoffs recentes</h2><div id="handoffs" class="grid"></div></section>
  <section class="panel"><h2>Prompt externo</h2><textarea id="prompt" readonly></textarea><button id="copy">Copiar prompt</button><a id="open" href="#">Abrir provider</a></section>
  <section class="panel"><h2>Resolver e ensinar</h2><div class="row"><input id="handoffId" placeholder="handoff_id"><select id="intent"><option>unknown</option><option>continue_project</option><option>deep_audit</option><option>build_check</option><option>memory_review</option><option>fix_plan</option><option>delivery_summary</option></select></div><input id="phrase" placeholder="frase para aprender"><textarea id="response" placeholder="cola aqui a resposta da IA externa"></textarea><button id="resolve">Resolver handoff</button></section>
  <section class="panel"><h2>Resultado</h2><pre id="out"></pre></section>
</div>
<script>
const qs=s=>document.querySelector(s);async function api(p,o){const r=await fetch(p,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}};if(!r.ok)throw new Error(t);return j}function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function show(v){qs('#out').textContent=JSON.stringify(v,null,2)}function render(d){const list=d.recent_handoffs||[];qs('#handoffs').innerHTML=list.slice().reverse().map(h=>`<div class="card"><b>${esc(h.provider)} · ${esc(h.status)}</b><span class="muted">${esc(h.handoff_id)}</span><p>${esc(h.unknown?.message||'')}</p><button onclick="selectHandoff('${esc(h.handoff_id)}')">Ver prompt</button></div>`).join('')||'<p class="muted">Sem handoffs.</p>';show(d)}async function load(){render(await api('/api/ai-handoff/dashboard'))}async function selectHandoff(id){const r=await api('/api/ai-handoff/handoffs/'+encodeURIComponent(id));const h=r.handoff;qs('#handoffId').value=h.handoff_id;qs('#prompt').value=h.external_prompt;qs('#open').href=h.provider_url;show(r)}qs('#latest').onclick=async()=>{const r=await api('/api/ai-handoff/from-latest-unknown',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider:qs('#provider').value})});show(r);if(r.handoff){qs('#handoffId').value=r.handoff.handoff_id;qs('#prompt').value=r.handoff.external_prompt;qs('#open').href=r.handoff.provider_url}load()};qs('#copy').onclick=async()=>{await navigator.clipboard.writeText(qs('#prompt').value);show({ok:true,copied:true})};qs('#resolve').onclick=async()=>{const r=await api('/api/ai-handoff/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({handoff_id:qs('#handoffId').value,provider_response:qs('#response').value,learn_phrase:qs('#phrase').value,intent:qs('#intent').value})});show(r);load()};load();setInterval(load,15000);
</script>
</body></html>
"""


@router.get('/app/ai-handoff', response_class=HTMLResponse)
async def ai_handoff_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
