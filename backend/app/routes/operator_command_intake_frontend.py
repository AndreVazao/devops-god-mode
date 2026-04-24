from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["operator-command-intake-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode Command Intake</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --danger:#ef4444; --ok:#22c55e; --warn:#f59e0b; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:16px; display:grid; gap:14px; grid-template-rows:auto 1fr auto; }
    .topbar, .panel, .composer, .bubble, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:14px; display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    h1 { font-size:20px; margin:0; }
    p { color:var(--muted); margin:6px 0 0; }
    .main { display:grid; grid-template-columns:1.1fr .9fr; gap:14px; min-height:0; }
    .panel { padding:14px; overflow:auto; }
    .feed { display:flex; flex-direction:column; gap:12px; }
    .bubble { padding:14px; background:rgba(15,23,41,.75); }
    .bubble .meta { display:flex; justify-content:space-between; gap:10px; color:var(--muted); font-size:12px; margin-bottom:8px; }
    .chip { padding:5px 9px; border-radius:999px; font-size:12px; font-weight:700; border:1px solid var(--line); display:inline-block; }
    .chip.critical { color:#fecaca; border-color:rgba(239,68,68,.45); background:rgba(239,68,68,.14); }
    .chip.high { color:#fde68a; border-color:rgba(245,158,11,.45); background:rgba(245,158,11,.14); }
    .chip.medium { color:#bfdbfe; border-color:rgba(96,165,250,.45); background:rgba(96,165,250,.14); }
    .composer { padding:12px; display:grid; grid-template-columns:1fr auto; gap:10px; align-items:end; }
    textarea, input, button { font:inherit; border-radius:14px; border:1px solid var(--line); background:#0f1729; color:var(--text); padding:10px 12px; }
    textarea { min-height:74px; resize:vertical; width:100%; }
    button { background:var(--accent); border:none; font-weight:700; cursor:pointer; }
    .card { padding:12px; background:rgba(15,23,41,.7); display:grid; gap:8px; margin-bottom:10px; }
    .step { display:flex; justify-content:space-between; gap:8px; padding:8px; border:1px solid var(--line); border-radius:12px; }
    .muted { color:var(--muted); }
    @media (max-width: 900px) { .page { padding:10px; } .main { grid-template-columns:1fr; } .composer { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>God Mode Command Intake</h1><p>Entrada natural do cockpit mobile para o cérebro local no PC.</p></div>
      <input id=\"projectHint\" placeholder=\"Projeto opcional: baribudos-studio\" />
    </section>

    <section class=\"main\">
      <section class=\"panel\"><div class=\"feed\" id=\"feed\"></div></section>
      <section class=\"panel\"><h2>Memória de projetos</h2><div id=\"projects\"></div></section>
    </section>

    <section class=\"composer\">
      <textarea id=\"commandText\" placeholder=\"Ex: Audita o Baribudos Studio e o Website, vê o que está partido e prepara PRs com aprovação.\"></textarea>
      <button id=\"sendBtn\">Enviar</button>
    </section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path, options) { const r = await fetch(path, options); if (!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function escapeHtml(value) { return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function commandCard(item) {
      const steps = (item.execution_plan || []).map(step => `<div class=\"step\"><span>${escapeHtml(step.label)}</span><span class=\"muted\">${escapeHtml(step.executor)}</span></div>`).join('');
      return `<div class=\"bubble\"><div class=\"meta\"><span>${escapeHtml(item.project?.project_name)} · ${escapeHtml(item.intent)}</span><span class=\"chip ${escapeHtml(item.priority)}\">${escapeHtml(item.priority)}</span></div><div>${escapeHtml(item.raw_text)}</div><div style=\"margin-top:10px;display:grid;gap:6px;\">${steps}</div></div>`;
    }
    async function load() {
      const commands = await api('/api/operator-command-intake/commands?tenant_id=owner-andre&limit=30');
      qs('#feed').innerHTML = (commands.commands || []).reverse().map(commandCard).join('') || '<div class=\"muted\">Sem comandos ainda.</div>';
      const projects = await api('/api/operator-command-intake/projects?tenant_id=owner-andre');
      qs('#projects').innerHTML = (projects.projects || []).map(item => `<div class=\"card\"><strong>${escapeHtml(item.project_name)}</strong><div class=\"muted\">${escapeHtml(item.project_id)}</div><div>${escapeHtml((item.known_repo_roles || []).join(', ') || 'sem roles')}</div><div>${escapeHtml((item.known_providers || []).join(', ') || 'sem providers')}</div></div>`).join('') || '<div class=\"muted\">Sem memória.</div>';
    }
    async function send() {
      const text = qs('#commandText').value.trim();
      if (!text) return;
      await api('/api/operator-command-intake/submit', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ command_text:text, project_hint:qs('#projectHint').value || null, tenant_id:'owner-andre', source_channel:'mobile_chat' }) });
      qs('#commandText').value = '';
      await load();
    }
    qs('#sendBtn').onclick = () => send();
    load();
    setInterval(load, 12000);
  </script>
</body>
</html>
"""


@router.get('/app/operator-command-intake', response_class=HTMLResponse)
async def operator_command_intake_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
