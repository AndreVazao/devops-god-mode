from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["repo-relationship-graph-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Repo Relationship Graph</title>
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
    input, textarea, button { font:inherit; border-radius:14px; border:1px solid var(--line); background:#0f1729; color:var(--text); padding:10px 12px; }
    textarea { min-height:70px; resize:vertical; }
    button { background:var(--accent); border:none; font-weight:700; cursor:pointer; }
    .form { display:grid; gap:10px; }
    .step { padding:8px; border:1px solid var(--line); border-radius:12px; margin-top:6px; }
    @media (max-width: 900px) { .page { padding:10px; } .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"topbar\">
      <div><h1>Repo Relationship Graph</h1><p>Grafo projeto/conversas/repos e planeador de auditoria profunda.</p></div>
      <div><button id=\"seedBtn\">Seed Baribudos demo</button> <button id=\"refreshBtn\">Atualizar</button></div>
    </section>

    <section class=\"summary\" id=\"summary\"></section>

    <section class=\"grid\">
      <section class=\"panel\">
        <h2>Ligar repo a projeto</h2>
        <div class=\"form\">
          <input id=\"repoName\" placeholder=\"AndreVazao/baribudos-studio\" />
          <input id=\"projectId\" placeholder=\"baribudos-studio\" />
          <input id=\"projectName\" placeholder=\"Baribudos Studio\" />
          <input id=\"roles\" placeholder=\"studio,backend,frontend,vault\" />
          <input id=\"deployTargets\" placeholder=\"vercel,supabase,github-actions\" />
          <textarea id=\"description\" placeholder=\"Descrição/stack do repo\"></textarea>
          <button id=\"saveRepoBtn\">Guardar repo</button>
        </div>
      </section>
      <section class=\"panel\"><h2>Projetos</h2><div id=\"projects\"></div></section>
    </section>

    <section class=\"grid\">
      <section class=\"panel\"><h2>Planos de auditoria</h2><div id=\"plans\"></div></section>
      <section class=\"panel\"><h2>Repos</h2><div id=\"repos\"></div></section>
    </section>
  </div>

  <script>
    const qs = (s) => document.querySelector(s);
    async function api(path, options) { const r = await fetch(path, options); if (!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`); return r.json(); }
    function escapeHtml(value) { return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;'); }
    function splitCsv(value) { return String(value || '').split(',').map(x => x.trim()).filter(Boolean); }
    function renderSummary(data) {
      const items = [['Projetos', data.project_count], ['Repos', data.repository_count], ['Planos', data.audit_plan_count], ['Sem repos', data.projects_without_repos]];
      qs('#summary').innerHTML = items.map(([label,value]) => `<div class=\"card\"><div class=\"muted\">${escapeHtml(label)}</div><div style=\"font-size:28px;font-weight:800;\">${escapeHtml(value ?? 0)}</div></div>`).join('');
    }
    function renderProjects(projects) {
      qs('#projects').innerHTML = (projects || []).map(item => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(item.project_name)}</strong><button onclick=\"auditProject('${escapeHtml(item.project_id)}')\">Auditar</button></div><div class=\"muted\">${escapeHtml(item.project_id)}</div><div>Repos: ${escapeHtml(item.repository_count)} · Conversas: ${escapeHtml(item.conversation_count)}</div><div>Roles: ${escapeHtml((item.roles || []).join(', ') || '-')}</div></div>`).join('') || '<div class=\"muted\">Sem projetos.</div>';
    }
    function renderRepos(projects) {
      const repos = (projects || []).flatMap(p => p.repositories || []);
      qs('#repos').innerHTML = repos.map(repo => `<div class=\"card\"><strong>${escapeHtml(repo.repository_full_name)}</strong><div class=\"muted\">${escapeHtml(repo.project_name)}</div><div>Roles: ${escapeHtml((repo.roles || []).join(', '))}</div><div>Stack: ${escapeHtml((repo.stack || []).join(', ') || '-')}</div></div>`).join('') || '<div class=\"muted\">Sem repos.</div>';
    }
    function renderPlans(plans) {
      qs('#plans').innerHTML = (plans || []).slice().reverse().map(plan => `<div class=\"card\"><div class=\"row\"><strong>${escapeHtml(plan.project_name)}</strong><span class=\"chip\">${escapeHtml(plan.status)}</span></div><div>${escapeHtml(plan.repository_count)} repos · ${escapeHtml(plan.conversation_count)} conversas</div>${(plan.repo_plans || []).map(r => `<div class=\"step\">${escapeHtml(r.repository_full_name)} · ${escapeHtml((r.roles || []).join(', '))}</div>`).join('')}</div>`).join('') || '<div class=\"muted\">Sem planos.</div>';
    }
    async function load() { const data = await api('/api/repo-relationship-graph/dashboard?tenant_id=owner-andre'); renderSummary(data); renderProjects(data.projects); renderRepos(data.projects); renderPlans(data.recent_audit_plans); }
    async function saveRepo() { const payload = { repository_full_name:qs('#repoName').value, project_id:qs('#projectId').value || null, project_name:qs('#projectName').value || null, roles:splitCsv(qs('#roles').value), deploy_targets:splitCsv(qs('#deployTargets').value), description:qs('#description').value, tenant_id:'owner-andre' }; await api('/api/repo-relationship-graph/repositories', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) }); await load(); }
    async function auditProject(projectId) { await api('/api/repo-relationship-graph/audit-plan', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ project_id:projectId, tenant_id:'owner-andre', include_repair_plan:true }) }); await load(); }
    async function seedDemo() { await api('/api/repo-relationship-graph/seed-demo-baribudos?tenant_id=owner-andre', { method:'POST' }); await load(); }
    qs('#refreshBtn').onclick = () => load(); qs('#saveRepoBtn').onclick = () => saveRepo(); qs('#seedBtn').onclick = () => seedDemo(); load(); setInterval(load, 15000);
  </script>
</body>
</html>
"""


@router.get('/app/repo-relationship-graph', response_class=HTMLResponse)
async def repo_relationship_graph_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
