from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["godmode-remediation-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode Remediation</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --critical:#ef4444; --high:#f59e0b; --medium:#60a5fa; --low:#94a3b8; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:20px; display:grid; gap:16px; }
    .topbar, .panel, .action-card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:16px; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; align-items:center; }
    .title h1 { margin:0; font-size:22px; }
    .title p { margin:6px 0 0; color:var(--muted); }
    .controls { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    select, button { background:#0f1729; color:var(--text); border:1px solid var(--line); border-radius:12px; padding:10px 12px; font:inherit; }
    button { cursor:pointer; background:#60a5fa; border:none; color:white; font-weight:600; }
    .summary { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:12px; }
    .panel { padding:16px; }
    .metric { border:1px solid var(--line); border-radius:14px; background:rgba(15,23,41,.7); padding:12px; }
    .metric .label { color:var(--muted); font-size:12px; }
    .metric .value { font-size:28px; font-weight:700; margin-top:6px; }
    .actions { display:grid; gap:12px; }
    .action-card { padding:16px; display:grid; gap:10px; }
    .action-top { display:flex; justify-content:space-between; gap:8px; align-items:center; }
    .chip { padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700; color:white; }
    .chip.critical { background:var(--critical); }
    .chip.high { background:var(--high); color:#111827; }
    .chip.medium { background:var(--medium); }
    .chip.low { background:var(--low); color:#111827; }
    .reason, .gain { color:#cbd5e1; line-height:1.45; }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div class=\"title\">
        <h1>God Mode Remediation Cockpit</h1>
        <p>Plano de próximas ações para desimpedir providers, vault, threads pendentes e falhas recentes.</p>
      </div>
      <div class=\"controls\">
        <select id=\"tenantSelect\"><option value=\"owner-andre\">owner-andre</option><option value=\"client-demo\">client-demo</option></select>
        <button id=\"refreshBtn\">Atualizar</button>
      </div>
    </section>

    <section class=\"summary panel\" id=\"summary\"></section>
    <section class=\"panel\">
      <div class=\"actions\" id=\"actions\"></div>
    </section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path) {
      const response = await fetch(path);
      if (!response.ok) throw new Error(await response.text() || `HTTP ${response.status}`);
      return response.json();
    }
    function escapeHtml(value) {
      return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;');
    }
    function renderSummary(summary) {
      const items = [
        ['Blockers', summary.blocker_count ?? 0],
        ['Providers', summary.provider_count ?? 0],
        ['Secrets', summary.secret_count ?? 0],
        ['Threads pendentes', summary.pending_threads ?? 0],
        ['Falhas recentes', summary.recent_failures ?? 0],
      ];
      qs('#summary').innerHTML = items.map(([label, value]) => `<div class=\"metric\"><div class=\"label\">${escapeHtml(label)}</div><div class=\"value\">${escapeHtml(value)}</div></div>`).join('');
    }
    function renderActions(actions) {
      const el = qs('#actions');
      if (!actions.length) {
        el.innerHTML = '<div class=\"action-card\"><div class=\"reason\">Sem ações pendentes nesta leitura.</div></div>';
        return;
      }
      el.innerHTML = actions.map(item => `
        <div class=\"action-card\">
          <div class=\"action-top\"><strong>${escapeHtml(item.title)}</strong><span class=\"chip ${escapeHtml(item.priority)}\">${escapeHtml(item.priority)}</span></div>
          <div class=\"reason\"><strong>Porque:</strong> ${escapeHtml(item.reason)}</div>
          <div class=\"gain\"><strong>Ganho:</strong> ${escapeHtml(item.expected_gain)}</div>
          <div class=\"gain\"><strong>Área:</strong> ${escapeHtml(item.target_area)}</div>
        </div>
      `).join('');
    }
    async function loadPlan() {
      const tenantId = qs('#tenantSelect').value;
      const data = await api(`/api/godmode-remediation/plan?tenant_id=${encodeURIComponent(tenantId)}`);
      renderSummary(data.diagnostics_summary || {});
      renderActions(data.actions || []);
    }
    qs('#refreshBtn').onclick = () => loadPlan();
    qs('#tenantSelect').onchange = () => loadPlan();
    loadPlan();
    setInterval(loadPlan, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/godmode-remediation', response_class=HTMLResponse)
async def godmode_remediation_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
