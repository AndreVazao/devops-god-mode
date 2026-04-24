from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["multi-ai-conversation-inventory-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Multi-AI Conversation Inventory</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --warn:#f59e0b; --ok:#22c55e; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:16px; display:grid; gap:14px; }
    .topbar, .panel, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:14px; display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    h1 { font-size:20px; margin:0; } h2 { margin:0 0 10px; font-size:17px; }
    p { color:var(--muted); margin:6px 0 0; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .panel { padding:14px; overflow:auto; }
    .card { padding:12px; background:rgba(15,23,41,.75); display:grid; gap:8px; margin-bottom:10px; }
    .summary { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }
    input, select, textarea, button { font:inherit; border-radius:14px; border:1px solid var(--line); background:#0f1729; color:var(--text); padding:10px 12px; }
    textarea { min-height:90px; resize:vertical; }
    button { background:var(--accent); border:none; font-weight:700; cursor:pointer; }
    .form { display:grid; gap:10px; }
    .row { display:flex; justify-content:space-between; align-items:center; gap:10px; }
    .muted { color:var(--muted); }
    .chip { padding:4px 8px; border-radius:999px; border:1px solid var(--line); font-size:12px; font-weight:700; }
    .chip.mapped { color:#bbf7d0; border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.12); }
    .chip.needs_review { color:#fde68a; border-color:rgba(245,158,11,.4); background:rgba(245,158,11,.12); }
    @media (max-width: 900px) { .page { padding:10px; } .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Multi-AI Conversation Inventory</h1><p>Mapa local-first de conversas ChatGPT, Claude, Gemini, Grok, DeepSeek e projetos.</p></div>
      <button id=\"refreshBtn\">Atualizar</button>
    </section>

    <section class=\"summary\" id=\"summary\"></section>

    <section class=\"grid\">
      <section class=\"panel\">
        <h2>Adicionar conversa capturada</h2>
        <div class=\"form\">
          <select id=\"provider\"><option>chatgpt</option><option>claude</option><option>gemini</option><option>grok</option><option>deepseek</option><option>unknown</option></select>
          <input id=\"projectHint\" placeholder=\"Projeto opcional: baribudos-studio\" />
          <input id=\"title\" placeholder=\"Título da conversa\" />
          <textarea id=\"snippet\" placeholder=\"Resumo/snippet/código importante da conversa\"></textarea>
          <button id=\"stageBtn\">Guardar no inventário</button>
        </div>
      </section>
      <section class=\"panel\"><h2>Projetos detetados</h2><div id=\"projects\"></div></section>
    </section>

    <section class=\"panel\"><h2>Conversas recentes</h2><div id=\"conversations\"></div></section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path, options) { const r = await fetch(path, options); if (!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function escapeHtml(value) { return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function renderSummary(data) {
      const items = [['Conversas', data.conversation_count], ['Projetos', data.project_count], ['Needs review', data.needs_review_count], ['Providers', Object.keys(data.provider_counts || {}).length]];
      qs('#summary').innerHTML = items.map(([label,value]) => `<div class=\"card\"><div class=\"muted\">${escapeHtml(label)}</div><div style=\"font-size:28px;font-weight:800;\">${escapeHtml(value ?? 0)}</div></div>`).join('');
    }
    function renderProjects(projects) {
      qs('#projects').innerHTML = (projects || []).map(item => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.project_name)}</strong><span class=\"chip\">${escapeHtml((item.conversation_ids || []).length)} conv</span></div><div class=\"muted\">${escapeHtml(item.project_id)}</div><div>Providers: ${escapeHtml((item.providers || []).join(', ') || '-')}</div><div>Roles: ${escapeHtml((item.repo_roles || []).join(', ') || '-')}</div></div>`).join('') || '<div class=\"muted\">Sem projetos.</div>';
    }
    function renderConversations(conversations) {
      qs('#conversations').innerHTML = (conversations || []).slice().reverse().map(item => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.title)}</strong><span class=\"chip ${escapeHtml(item.mapping_status)}\">${escapeHtml(item.provider)} · ${escapeHtml(item.mapping_status)}</span></div><div class=\"muted\">${escapeHtml(item.project?.project_name)} · ${escapeHtml((item.repo_roles || []).join(', ') || 'sem roles')}</div><div>${escapeHtml(item.summary)}</div></div>`).join('') || '<div class=\"muted\">Sem conversas.</div>';
    }
    async function load() {
      const data = await api('/api/multi-ai-conversation-inventory/dashboard?tenant_id=owner-andre');
      renderSummary(data); renderProjects(data.projects || []); renderConversations(data.recent_conversations || []);
    }
    async function stage() {
      const payload = { provider:qs('#provider').value, project_hint:qs('#projectHint').value || null, title:qs('#title').value || 'Untitled conversation', snippet:qs('#snippet').value || '', tenant_id:'owner-andre', source_status:'manual_seed' };
      await api('/api/multi-ai-conversation-inventory/stage', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
      qs('#title').value=''; qs('#snippet').value=''; await load();
    }
    qs('#refreshBtn').onclick = () => load(); qs('#stageBtn').onclick = () => stage(); load(); setInterval(load, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/multi-ai-conversation-inventory', response_class=HTMLResponse)
async def multi_ai_conversation_inventory_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
