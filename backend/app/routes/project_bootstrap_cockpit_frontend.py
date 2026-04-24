from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["project-bootstrap-cockpit-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Project Bootstrap Cockpit</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --ok:#22c55e; --warn:#f59e0b; --danger:#ef4444; --accent:#60a5fa; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:20px; display:grid; gap:16px; }
    .topbar, .panel, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:16px; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; align-items:center; }
    .title h1 { margin:0; font-size:22px; }
    .title p { margin:6px 0 0; color:var(--muted); }
    .controls { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    input, select, button { background:#0f1729; color:var(--text); border:1px solid var(--line); border-radius:12px; padding:10px 12px; font:inherit; }
    button { cursor:pointer; background:var(--accent); border:none; color:white; font-weight:600; }
    .summary { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:12px; }
    .panel { padding:16px; display:grid; gap:12px; }
    .card { padding:14px; display:grid; gap:8px; background:rgba(15,23,41,.72); }
    .row { display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .chip { padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700; }
    .chip.ready { background:rgba(34,197,94,.14); color:#86efac; border:1px solid rgba(34,197,94,.35); }
    .chip.blocked, .chip.hold { background:rgba(239,68,68,.14); color:#fecaca; border:1px solid rgba(239,68,68,.35); }
    .chip.attention_required { background:rgba(245,158,11,.14); color:#fde68a; border:1px solid rgba(245,158,11,.35); }
    .muted { color:var(--muted); }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
    @media (max-width: 980px) { .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div class=\"title\">
        <h1>Project Bootstrap Cockpit</h1>
        <p>Vista go/no-go para arrancar um projeto novo sem andar às cegas entre diagnostics, remediation e provider onboarding.</p>
      </div>
      <div class=\"controls\">
        <select id=\"tenantSelect\"><option value=\"owner-andre\">owner-andre</option><option value=\"client-demo\">client-demo</option></select>
        <input id=\"projectName\" value=\"baribudos-studio\" />
        <button id=\"refreshBtn\">Atualizar</button>
      </div>
    </section>

    <section class=\"summary\" id=\"summary\"></section>

    <section class=\"grid\">
      <section class=\"panel\"><h2>Fases de lançamento</h2><div id=\"phases\"></div></section>
      <section class=\"panel\"><h2>Blockers</h2><div id=\"blockers\"></div></section>
    </section>

    <section class=\"grid\">
      <section class=\"panel\"><h2>Ações de remediação</h2><div id=\"actions\"></div></section>
      <section class=\"panel\"><h2>Repo plan</h2><div id=\"repoPlan\"></div></section>
    </section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path) { const response = await fetch(path); if (!response.ok) throw new Error(await response.text() || `HTTP ${response.status}`); return response.json(); }
    function escapeHtml(value) { return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function renderSummary(data) {
      const items = [
        ['Launch ready', data.launch_ready],
        ['Readiness score', data.readiness_score],
        ['Blockers', data.blocker_count],
        ['Providers', data.onboarding?.provider_count ?? 0],
        ['Remediation actions', data.remediation?.action_count ?? 0],
      ];
      qs('#summary').innerHTML = items.map(([label, value]) => `<div class=\"card\"><div class=\"muted\">${escapeHtml(label)}</div><div style=\"font-size:30px;font-weight:700;\">${escapeHtml(value)}</div></div>`).join('');
    }
    function renderCards(id, items, formatter, emptyText) {
      const el = qs(id);
      if (!items.length) { el.innerHTML = `<div class=\"muted\">${escapeHtml(emptyText)}</div>`; return; }
      el.innerHTML = items.map(formatter).join('');
    }
    async function loadDashboard() {
      const tenantId = qs('#tenantSelect').value;
      const projectName = qs('#projectName').value || 'baribudos-studio';
      const data = await api(`/api/project-bootstrap-cockpit/dashboard?tenant_id=${encodeURIComponent(tenantId)}&project_name=${encodeURIComponent(projectName)}&providers=github,vercel,supabase,render&multirepo_mode=true`);
      renderSummary(data);
      renderCards('#phases', data.launch_phases || [], (item) => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.label)}</strong><span class=\"chip ${escapeHtml(item.status)}\">${escapeHtml(item.status)}</span></div><div>${escapeHtml(item.summary)}</div></div>`, 'Sem fases.');
      renderCards('#blockers', data.blockers || [], (item) => `<div class=\"card\">${escapeHtml(item)}</div>`, 'Sem blockers críticos.');
      renderCards('#actions', data.remediation?.actions || [], (item) => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.title)}</strong><span class=\"chip attention_required\">${escapeHtml(item.priority)}</span></div><div>${escapeHtml(item.reason)}</div><div class=\"muted\">${escapeHtml(item.expected_gain)}</div></div>`, 'Sem ações pendentes.');
      const repoPlanEntries = Object.entries(data.onboarding?.repo_plan || {});
      renderCards('#repoPlan', repoPlanEntries, ([key, value]) => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(key)}</strong><span>${escapeHtml(value)}</span></div></div>`, 'Sem repo plan.');
    }
    qs('#refreshBtn').onclick = () => loadDashboard();
    qs('#tenantSelect').onchange = () => loadDashboard();
    loadDashboard();
    setInterval(loadDashboard, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/project-bootstrap', response_class=HTMLResponse)
async def project_bootstrap_cockpit_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
