from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["godmode-diagnostics-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode Diagnostics</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --ok:#22c55e; --warn:#f59e0b; --danger:#ef4444; --accent:#60a5fa; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:20px; display:grid; gap:16px; }
    .topbar, .panel, .metric, .list-card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:16px; display:flex; justify-content:space-between; gap:16px; align-items:center; flex-wrap:wrap; }
    .title h1 { margin:0; font-size:22px; }
    .title p { margin:6px 0 0; color:var(--muted); }
    .controls { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    select, button { background:#0f1729; color:var(--text); border:1px solid var(--line); border-radius:12px; padding:10px 12px; font:inherit; }
    button { cursor:pointer; background:var(--accent); border:none; color:white; font-weight:600; }
    .status { padding:6px 10px; border-radius:999px; font-size:12px; border:1px solid transparent; }
    .status.ok { background:rgba(34,197,94,.14); border-color:rgba(34,197,94,.35); color:#86efac; }
    .status.warn { background:rgba(245,158,11,.14); border-color:rgba(245,158,11,.35); color:#fde68a; }
    .status.danger { background:rgba(239,68,68,.14); border-color:rgba(239,68,68,.35); color:#fecaca; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; }
    .metric { padding:16px; display:grid; gap:8px; }
    .metric .label { color:var(--muted); font-size:13px; }
    .metric .value { font-size:30px; font-weight:700; }
    .metric .summary { color:#cbd5e1; line-height:1.4; font-size:13px; }
    .stack { display:grid; gap:14px; grid-template-columns:1.1fr .9fr; }
    .list-card { padding:16px; display:grid; gap:12px; min-height:180px; }
    .list-card h2 { margin:0; font-size:16px; }
    .list { display:grid; gap:10px; }
    .item { padding:12px; border-radius:14px; border:1px solid var(--line); background:rgba(15,23,41,.7); }
    .item-top { display:flex; justify-content:space-between; gap:8px; align-items:center; }
    .item-title { font-weight:700; }
    .item-sub { color:var(--muted); font-size:12px; margin-top:6px; }
    .empty { color:var(--muted); }
    @media (max-width: 980px) { .stack { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div class=\"title\">
        <h1>God Mode Diagnostics Cockpit</h1>
        <p>Vista rápida para perceber bloqueios, falhas recentes, recuperação e prontidão operacional.</p>
      </div>
      <div class=\"controls\">
        <select id=\"tenantSelect\">
          <option value=\"owner-andre\">owner-andre</option>
          <option value=\"client-demo\">client-demo</option>
        </select>
        <button id=\"refreshBtn\">Atualizar</button>
        <span id=\"overallStatus\" class=\"status ok\">A carregar</span>
      </div>
    </section>

    <section id=\"metrics\" class=\"grid\"></section>

    <section class=\"stack\">
      <section class=\"list-card\">
        <h2>Bloqueios</h2>
        <div id=\"blockers\" class=\"list\"></div>
      </section>
      <section class=\"list-card\">
        <h2>Resumo rápido</h2>
        <div id=\"summary\" class=\"list\"></div>
      </section>
    </section>

    <section class=\"stack\">
      <section class=\"list-card\">
        <h2>Falhas recentes</h2>
        <div id=\"failures\" class=\"list\"></div>
      </section>
      <section class=\"list-card\">
        <h2>Recuperações recentes</h2>
        <div id=\"recoveries\" class=\"list\"></div>
      </section>
    </section>

    <section class=\"list-card\">
      <h2>Atividade de fila offline</h2>
      <div id=\"queueActivity\" class=\"list\"></div>
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
    function statusClass(severity) {
      if (severity === 'danger') return 'danger';
      if (severity === 'warning') return 'warn';
      return 'ok';
    }
    function renderMetrics(items) {
      const el = qs('#metrics');
      el.innerHTML = items.map(item => `
        <div class=\"metric\">
          <div class=\"item-top\"><span class=\"label\">${escapeHtml(item.label)}</span><span class=\"status ${statusClass(item.severity)}\">${escapeHtml(item.severity)}</span></div>
          <div class=\"value\">${escapeHtml(item.value)}</div>
          <div class=\"summary\">${escapeHtml(item.summary)}</div>
        </div>
      `).join('');
    }
    function renderSimpleList(id, items, formatter) {
      const el = qs(id);
      if (!items.length) { el.innerHTML = '<div class=\"empty\">Sem itens.</div>'; return; }
      el.innerHTML = items.map(formatter).join('');
    }
    function entryCard(entry) {
      return `
        <div class=\"item\">
          <div class=\"item-top\"><span class=\"item-title\">${escapeHtml(entry.event_type || entry.label || 'evento')}</span><span class=\"status ${statusClass(entry.outcome === 'failed' || entry.outcome === 'restart_required' ? 'danger' : 'ok')}\">${escapeHtml(entry.outcome || 'ok')}</span></div>
          <div class=\"item-sub\">${escapeHtml(entry.summary || '')}</div>
        </div>
      `;
    }
    async function loadDashboard() {
      const tenantId = qs('#tenantSelect').value;
      const data = await api(`/api/godmode-diagnostics/dashboard?tenant_id=${encodeURIComponent(tenantId)}`);
      qs('#overallStatus').textContent = data.blocker_count ? `Bloqueios: ${data.blocker_count}` : 'Sem bloqueios críticos';
      qs('#overallStatus').className = `status ${data.blocker_count ? 'warn' : 'ok'}`;
      renderMetrics(data.diagnostics || []);
      renderSimpleList('#blockers', data.blockers || [], (item) => `<div class=\"item\"><div class=\"item-title\">${escapeHtml(item)}</div></div>`);
      renderSimpleList('#summary', [
        { label: 'Threads', value: data.snapshot_summary?.thread_count ?? 0 },
        { label: 'Journal', value: data.snapshot_summary?.journal_entry_count ?? 0 },
        { label: 'Providers', value: data.provider_count ?? 0 },
        { label: 'Secrets', value: data.secret_count ?? 0 },
      ], (item) => `<div class=\"item\"><div class=\"item-top\"><span class=\"item-title\">${escapeHtml(item.label)}</span><span>${escapeHtml(item.value)}</span></div></div>`);
      renderSimpleList('#failures', data.recent_failures || [], entryCard);
      renderSimpleList('#recoveries', data.recent_recoveries || [], entryCard);
      renderSimpleList('#queueActivity', data.recent_queue_activity || [], entryCard);
    }
    qs('#refreshBtn').onclick = () => loadDashboard();
    qs('#tenantSelect').onchange = () => loadDashboard();
    loadDashboard();
    setInterval(loadDashboard, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/godmode-diagnostics', response_class=HTMLResponse)
async def godmode_diagnostics_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
