from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["mobile-approval-cockpit-v2-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Mobile Approval Cockpit v2</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --ok:#22c55e; --warn:#f59e0b; --danger:#ef4444; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:12px; display:grid; gap:12px; grid-template-rows:auto 1fr auto; }
    .topbar, .panel, .composer, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:12px; display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    h1 { margin:0; font-size:19px; } p { margin:4px 0 0; color:var(--muted); }
    .summary { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
    .stat { padding:10px; border:1px solid var(--line); border-radius:16px; background:rgba(15,23,41,.75); }
    .stat strong { display:block; font-size:24px; }
    .panel { padding:12px; overflow:auto; }
    .feed { display:grid; gap:10px; }
    .card { padding:12px; background:rgba(15,23,41,.75); display:grid; gap:8px; }
    .row { display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .muted { color:var(--muted); }
    .chip { padding:4px 8px; border-radius:999px; border:1px solid var(--line); font-size:12px; font-weight:700; }
    .chip.pending_approval { color:#fde68a; border-color:rgba(245,158,11,.4); background:rgba(245,158,11,.12); }
    .chip.approved { color:#bbf7d0; border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.12); }
    .chip.rejected { color:#fecaca; border-color:rgba(239,68,68,.4); background:rgba(239,68,68,.12); }
    .actions { display:flex; gap:8px; flex-wrap:wrap; }
    button, input, textarea { font:inherit; border-radius:14px; border:1px solid var(--line); background:#0f1729; color:var(--text); padding:10px 12px; }
    button { background:var(--accent); border:none; font-weight:700; cursor:pointer; }
    button.reject { background:var(--danger); }
    button.ok { background:var(--ok); }
    textarea { width:100%; min-height:70px; resize:vertical; }
    .composer { padding:10px; display:grid; gap:8px; }
    @media (max-width:700px){ .summary{grid-template-columns:1fr 1fr 1fr;} .page{padding:8px;} }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Mobile Approval Cockpit v2</h1><p>Cartões de aprovação para o cérebro local no PC.</p></div>
      <button id=\"refreshBtn\">Atualizar</button>
    </section>
    <section class=\"summary\" id=\"summary\"></section>
    <section class=\"panel\"><div class=\"feed\" id=\"feed\"></div></section>
    <section class=\"composer\">
      <textarea id=\"body\" placeholder=\"Criar cartão manual para o telemóvel...\"></textarea>
      <button id=\"createBtn\">Criar update</button>
    </section>
  </div>
  <script>
    const qs = s => document.querySelector(s);
    async function api(path, options){ const r = await fetch(path, options); if(!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function esc(v){ return String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function renderSummary(d){ qs('#summary').innerHTML = [['Cards',d.card_count],['Pendentes',d.pending_approval_count],['Alta',d.high_priority_count]].map(([l,v])=>`<div class=\"stat\"><span class=\"muted\">${esc(l)}</span><strong>${esc(v)}</strong></div>`).join(''); }
    function renderCards(cards){ qs('#feed').innerHTML = (cards||[]).slice().reverse().map(c=>`<div class=\"card\"><div class=\"row\"><strong>${esc(c.title)}</strong><span class=\"chip ${esc(c.status)}\">${esc(c.status)}</span></div><div class=\"muted\">${esc(c.project_id)} · ${esc(c.card_type)} · ${esc(c.priority)}</div><div>${esc(c.body)}</div><div class=\"actions\">${(c.actions||[]).map(a=>`<button class=\"${a.decision==='approved'?'ok':a.decision==='rejected'?'reject':''}\" onclick=\"decide('${esc(c.card_id)}','${esc(a.decision)}')\">${esc(a.label)}</button>`).join('')}</div></div>`).join('') || '<div class=\"muted\">Sem cartões.</div>'; }
    async function load(){ const d = await api('/api/mobile-approval-cockpit-v2/dashboard?tenant_id=owner-andre'); renderSummary(d); renderCards(d.recent_cards); }
    async function decide(cardId, decision){ await api('/api/mobile-approval-cockpit-v2/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card_id:cardId,decision,tenant_id:'owner-andre'})}); await load(); }
    async function create(){ const body = qs('#body').value.trim(); if(!body) return; await api('/api/mobile-approval-cockpit-v2/cards',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:'Update manual',body,card_type:'progress_update',project_id:'general-intake',tenant_id:'owner-andre',priority:'medium',requires_approval:false})}); qs('#body').value=''; await load(); }
    qs('#refreshBtn').onclick=load; qs('#createBtn').onclick=create; load(); setInterval(load,10000);
  </script>
</body>
</html>
"""


@router.get('/app/mobile-approval-cockpit-v2', response_class=HTMLResponse)
async def mobile_approval_cockpit_v2_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
