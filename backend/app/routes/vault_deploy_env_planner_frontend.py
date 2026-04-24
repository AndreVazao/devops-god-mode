from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["vault-deploy-env-planner-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Vault Deploy Env Planner</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --warn:#f59e0b; --danger:#ef4444; --ok:#22c55e; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); }
    .page { min-height:100vh; padding:16px; display:grid; gap:14px; }
    .topbar, .panel, .card { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
    .topbar { padding:14px; display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }
    h1 { font-size:20px; margin:0; } h2 { margin:0 0 10px; font-size:17px; }
    p { color:var(--muted); margin:6px 0 0; }
    .summary { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .panel { padding:14px; overflow:auto; }
    .card { padding:12px; background:rgba(15,23,41,.75); display:grid; gap:8px; margin-bottom:10px; }
    .row { display:flex; justify-content:space-between; align-items:center; gap:10px; }
    .muted { color:var(--muted); }
    .chip { padding:4px 8px; border-radius:999px; border:1px solid var(--line); font-size:12px; font-weight:700; }
    .chip.ready_for_env_binding { color:#bbf7d0; border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.12); }
    .chip.blocked_missing_secrets { color:#fecaca; border-color:rgba(239,68,68,.4); background:rgba(239,68,68,.12); }
    input, button { font:inherit; border-radius:14px; border:1px solid var(--line); background:#0f1729; color:var(--text); padding:10px 12px; }
    button { background:var(--accent); border:none; font-weight:700; cursor:pointer; }
    .form { display:grid; gap:10px; }
    @media (max-width: 900px) { .page { padding:10px; } .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Vault Deploy Env Planner</h1><p>Planeador de env/secrets sem expor valores.</p></div>
      <div><button id=\"seedBtn\">Seed demo secrets</button> <button id=\"refreshBtn\">Atualizar</button></div>
    </section>

    <section class=\"summary\" id=\"summary\"></section>

    <section class=\"grid\">
      <section class=\"panel\">
        <h2>Gerar readiness</h2>
        <div class=\"form\">
          <input id=\"projectId\" value=\"baribudos-studio\" />
          <button id=\"reportBtn\">Gerar relatório</button>
        </div>
      </section>
      <section class=\"panel\">
        <h2>Registar presença de secret</h2>
        <div class=\"form\">
          <input id=\"secretName\" placeholder=\"SUPABASE_SERVICE_ROLE_KEY\" />
          <input id=\"provider\" placeholder=\"supabase\" />
          <input id=\"scope\" value=\"baribudos-studio\" />
          <button id=\"secretBtn\">Marcar como presente</button>
        </div>
      </section>
    </section>

    <section class=\"grid\">
      <section class=\"panel\"><h2>Relatórios recentes</h2><div id=\"reports\"></div></section>
      <section class=\"panel\"><h2>Secrets registados</h2><div id=\"secrets\"></div></section>
    </section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path, options) { const r = await fetch(path, options); if (!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function escapeHtml(value) { return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function renderSummary(data) {
      const items = [['Manifests', data.manifest_count], ['Secrets', data.secret_presence_count], ['Reports', data.readiness_report_count], ['Blocked', data.blocked_project_count]];
      qs('#summary').innerHTML = items.map(([label,value]) => `<div class=\"card\"><div class=\"muted\">${escapeHtml(label)}</div><div style=\"font-size:28px;font-weight:800;\">${escapeHtml(value ?? 0)}</div></div>`).join('');
    }
    function renderReports(reports) {
      qs('#reports').innerHTML = (reports || []).slice().reverse().map(item => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.project_name)}</strong><span class=\"chip ${escapeHtml(item.status)}\">${escapeHtml(item.status)}</span></div><div>Score: ${escapeHtml(item.readiness_score)} · Missing: ${escapeHtml(item.missing_secret_count)} · Public: ${escapeHtml(item.public_env_count)}</div><div class=\"muted\">${escapeHtml((item.blockers || []).join(' | ') || 'sem blockers')}</div></div>`).join('') || '<div class=\"muted\">Sem relatórios.</div>';
    }
    function renderSecrets(secrets) {
      qs('#secrets').innerHTML = (secrets || []).map(item => `<div class=\"card\"><strong>${escapeHtml(item.secret_name)}</strong><div class=\"muted\">${escapeHtml(item.provider)} · ${escapeHtml(item.scope)}</div><div>present: ${escapeHtml(item.present)}</div></div>`).join('') || '<div class=\"muted\">Sem secrets.</div>';
    }
    async function load() { const data = await api('/api/vault-deploy-env-planner/dashboard?tenant_id=owner-andre'); renderSummary(data); renderReports(data.recent_reports); renderSecrets(data.secret_presence); }
    async function report() { await api('/api/vault-deploy-env-planner/readiness-report', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ project_id:qs('#projectId').value, tenant_id:'owner-andre' }) }); await load(); }
    async function secret() { await api('/api/vault-deploy-env-planner/secret-presence', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ secret_name:qs('#secretName').value, provider:qs('#provider').value || 'unknown', scope:qs('#scope').value || 'owner-andre', present:true, tenant_id:'owner-andre' }) }); await load(); }
    async function seed() { await api('/api/vault-deploy-env-planner/seed-demo-baribudos-secrets?tenant_id=owner-andre', { method:'POST' }); await load(); }
    qs('#refreshBtn').onclick = () => load(); qs('#reportBtn').onclick = () => report(); qs('#secretBtn').onclick = () => secret(); qs('#seedBtn').onclick = () => seed(); load(); setInterval(load, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/vault-deploy-env-planner', response_class=HTMLResponse)
async def vault_deploy_env_planner_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
