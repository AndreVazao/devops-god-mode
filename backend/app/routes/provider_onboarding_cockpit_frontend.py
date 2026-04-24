from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["provider-onboarding-cockpit-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Provider Onboarding Cockpit</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --ok:#22c55e; --warn:#f59e0b; --danger:#ef4444; --accent:#60a5fa; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:20px; display:grid; gap:16px; }
    .topbar, .panel, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:16px; display:flex; justify-content:space-between; gap:16px; align-items:center; flex-wrap:wrap; }
    .title h1 { margin:0; font-size:22px; }
    .title p { margin:6px 0 0; color:var(--muted); }
    .controls { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    input, select, button { background:#0f1729; color:var(--text); border:1px solid var(--line); border-radius:12px; padding:10px 12px; font:inherit; }
    button { cursor:pointer; background:var(--accent); border:none; color:white; font-weight:600; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:14px; }
    .panel { padding:16px; display:grid; gap:12px; }
    .card { padding:14px; display:grid; gap:8px; background:rgba(15,23,41,.72); }
    .row { display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .chip { padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700; }
    .chip.ok { background:rgba(34,197,94,.14); color:#86efac; border:1px solid rgba(34,197,94,.35); }
    .chip.warning { background:rgba(245,158,11,.14); color:#fde68a; border:1px solid rgba(245,158,11,.35); }
    .chip.danger { background:rgba(239,68,68,.14); color:#fecaca; border:1px solid rgba(239,68,68,.35); }
    .muted { color:var(--muted); }
    .list { display:grid; gap:10px; }
    .empty { color:var(--muted); }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div class=\"title\">
        <h1>Provider Onboarding Cockpit</h1>
        <p>Vista direta para preparar providers, plano first-run e estrutura multi-repo para os próximos projetos.</p>
      </div>
      <div class=\"controls\">
        <select id=\"tenantSelect\"><option value=\"owner-andre\">owner-andre</option><option value=\"client-demo\">client-demo</option></select>
        <input id=\"projectName\" value=\"baribudos-studio\" />
        <button id=\"refreshBtn\">Atualizar</button>
      </div>
    </section>

    <section class=\"grid\" id=\"summary\"></section>

    <section class=\"grid\">
      <section class=\"panel\">
        <h2>Providers</h2>
        <div id=\"providers\" class=\"list\"></div>
      </section>
      <section class=\"panel\">
        <h2>Blockers</h2>
        <div id=\"blockers\" class=\"list\"></div>
      </section>
    </section>

    <section class=\"grid\">
      <section class=\"panel\">
        <h2>Plano first-run</h2>
        <div id=\"steps\" class=\"list\"></div>
      </section>
      <section class=\"panel\">
        <h2>Repo plan</h2>
        <div id=\"repoPlan\" class=\"list\"></div>
      </section>
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
    function renderSummary(data) {
      const items = [
        ['Providers pedidos', data.provider_count],
        ['Providers no registry', data.registry_provider_count],
        ['Providers com capability', data.capability_provider_count],
        ['Tenants', data.tenant_count],
        ['Blockers', data.blocker_count],
      ];
      qs('#summary').innerHTML = items.map(([label, value]) => `<div class=\"card\"><div class=\"muted\">${escapeHtml(label)}</div><div style=\"font-size:30px;font-weight:700;\">${escapeHtml(value)}</div></div>`).join('');
    }
    function renderProviders(items) {
      const el = qs('#providers');
      if (!items.length) { el.innerHTML = '<div class=\"empty\">Sem providers.</div>'; return; }
      el.innerHTML = items.map(item => `
        <div class=\"card\">
          <div class=\"row\"><strong>${escapeHtml(item.provider_name)}</strong><span class=\"chip ${escapeHtml(item.severity)}\">${escapeHtml(item.severity)}</span></div>
          <div class=\"muted\">Secret sync real: ${escapeHtml(item.real_secret_sync_available)}</div>
          <div class=\"muted\">Deploy real: ${escapeHtml(item.real_deploy_dispatch_available)}</div>
          <div>${escapeHtml(item.next_step)}</div>
        </div>
      `).join('');
    }
    function renderBlockers(items) {
      const el = qs('#blockers');
      if (!items.length) { el.innerHTML = '<div class=\"empty\">Sem blockers críticos nesta leitura.</div>'; return; }
      el.innerHTML = items.map(item => `<div class=\"card\">${escapeHtml(item)}</div>`).join('');
    }
    function renderSteps(items) {
      const el = qs('#steps');
      if (!items.length) { el.innerHTML = '<div class=\"empty\">Sem passos.</div>'; return; }
      el.innerHTML = items.map(item => `
        <div class=\"card\">
          <div class=\"row\"><strong>${escapeHtml(item.provider_name)}</strong><span class=\"chip warning\">${escapeHtml(item.status)}</span></div>
          <div>${escapeHtml(item.step)}</div>
          <div class=\"muted\">Login necessário: ${escapeHtml(item.requires_user_login)}</div>
        </div>
      `).join('');
    }
    function renderRepoPlan(plan) {
      const el = qs('#repoPlan');
      const entries = Object.entries(plan || {});
      if (!entries.length) { el.innerHTML = '<div class=\"empty\">Sem plano de repo.</div>'; return; }
      el.innerHTML = entries.map(([key, value]) => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(key)}</strong><span>${escapeHtml(value)}</span></div></div>`).join('');
    }
    async function loadDashboard() {
      const tenantId = qs('#tenantSelect').value;
      const projectName = qs('#projectName').value || 'baribudos-studio';
      const data = await api(`/api/provider-onboarding-cockpit/dashboard?tenant_id=${encodeURIComponent(tenantId)}&project_name=${encodeURIComponent(projectName)}&providers=github,vercel,supabase,render&multirepo_mode=true`);
      renderSummary(data);
      renderProviders(data.providers || []);
      renderBlockers(data.blockers || []);
      renderSteps(data.first_run_steps || []);
      renderRepoPlan(data.repo_plan || {});
    }
    qs('#refreshBtn').onclick = () => loadDashboard();
    qs('#tenantSelect').onchange = () => loadDashboard();
    loadDashboard();
    setInterval(loadDashboard, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/provider-onboarding', response_class=HTMLResponse)
async def provider_onboarding_cockpit_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
