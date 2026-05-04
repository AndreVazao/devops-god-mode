from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class HomeVisualShellService:
    """Backend-served visual cockpit for desktop/APK/WebView.

    This shell intentionally consumes `/api/home-control-surface/package` instead
    of hardcoding module state. Desktop launchers and Android WebViews can load
    `/app/home` and receive the same real control surface.
    """

    SERVICE_ID = "home_visual_shell"
    VERSION = "phase_173_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "created_at": self._now(),
            "entrypoints": ["/app/home", "/api/home-visual-shell/page"],
            "data_contract": "/api/home-control-surface/package",
            "targets": ["pc_desktop_launcher", "android_apk_webview", "browser"],
            "dangerous_actions_directly_exposed": False,
            "requires_confirmation_supported": True,
        }

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "assets": {
                "html_entrypoint": "/app/home",
                "api_entrypoint": "/api/home-visual-shell/page",
                "control_surface_package": "/api/home-control-surface/package",
            },
            "render_features": [
                "module cards",
                "traffic-light status",
                "real endpoint buttons",
                "payload editor for POST actions",
                "confirmation gate for risky buttons",
                "mobile responsive layout",
                "dark cockpit UI",
            ],
        }

    def html(self) -> str:
        return """<!doctype html>
<html lang=\"pt\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode — Home Control Surface</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #070b13;
      --panel: #0f1726;
      --panel-2: #111c2e;
      --stroke: #22324d;
      --text: #eaf2ff;
      --muted: #91a4bf;
      --green: #28d17c;
      --yellow: #f1c84b;
      --red: #ff5d5d;
      --blue: #64a8ff;
      --orange: #ff9d4d;
      --shadow: 0 18px 60px rgba(0,0,0,.35);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top left, rgba(66,126,255,.18), transparent 35%), var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    .wrap { max-width: 1380px; margin: 0 auto; padding: 22px; }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
      background: rgba(15,23,38,.82);
      border: 1px solid var(--stroke);
      border-radius: 22px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }
    h1 { margin: 0; font-size: clamp(24px, 4vw, 42px); letter-spacing: -.04em; }
    .subtitle { margin-top: 6px; color: var(--muted); font-size: 14px; }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding: 10px 14px;
      border: 1px solid var(--stroke);
      border-radius: 999px;
      background: rgba(17,28,46,.88);
      white-space: nowrap;
      font-weight: 700;
    }
    .dot { width: 12px; height: 12px; border-radius: 999px; background: var(--yellow); box-shadow: 0 0 18px currentColor; }
    .dot.green { background: var(--green); color: var(--green); }
    .dot.yellow { background: var(--yellow); color: var(--yellow); }
    .dot.red { background: var(--red); color: var(--red); }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 18px 0;
    }
    button, .ghost {
      border: 1px solid var(--stroke);
      background: linear-gradient(180deg, #182640, #101a2d);
      color: var(--text);
      border-radius: 14px;
      padding: 10px 13px;
      font-weight: 750;
      cursor: pointer;
      transition: transform .12s ease, border-color .12s ease, background .12s ease;
    }
    button:hover { transform: translateY(-1px); border-color: #416392; }
    button.safe { border-color: rgba(40,209,124,.45); }
    button.low { border-color: rgba(100,168,255,.55); }
    button.approval_required { border-color: rgba(255,157,77,.7); }
    button:disabled { opacity: .55; cursor: not-allowed; transform: none; }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }
    .card {
      background: linear-gradient(180deg, rgba(17,28,46,.96), rgba(10,17,30,.96));
      border: 1px solid var(--stroke);
      border-radius: 22px;
      padding: 18px;
      box-shadow: var(--shadow);
      min-height: 260px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
    .card h2 { margin: 0; font-size: 19px; letter-spacing: -.02em; }
    .desc { color: var(--muted); line-height: 1.45; font-size: 13px; }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .tag { border: 1px solid var(--stroke); border-radius: 999px; padding: 5px 8px; background: rgba(7,11,19,.45); }
    .buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: auto; }
    .output {
      margin-top: 18px;
      background: #050812;
      border: 1px solid var(--stroke);
      border-radius: 18px;
      padding: 14px;
      min-height: 170px;
      box-shadow: var(--shadow);
    }
    .output pre {
      white-space: pre-wrap;
      word-break: break-word;
      margin: 0;
      color: #b8c7df;
      font-size: 12px;
      max-height: 360px;
      overflow: auto;
    }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,.68);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      z-index: 20;
    }
    .modal {
      width: min(760px, 100%);
      background: var(--panel);
      border: 1px solid var(--stroke);
      border-radius: 22px;
      padding: 18px;
      box-shadow: var(--shadow);
    }
    .modal h3 { margin: 0 0 8px; }
    textarea {
      width: 100%;
      min-height: 190px;
      margin-top: 10px;
      background: #060a13;
      color: var(--text);
      border: 1px solid var(--stroke);
      border-radius: 14px;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; }
    .warning { color: var(--orange); font-weight: 800; }
    .empty { color: var(--muted); padding: 28px; text-align: center; }
    @media (max-width: 1080px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 720px) {
      .wrap { padding: 12px; }
      header { align-items: flex-start; flex-direction: column; }
      .grid { grid-template-columns: 1fr; }
      .status-pill { width: 100%; justify-content: center; }
    }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <header>
      <div>
        <h1>God Mode</h1>
        <div class=\"subtitle\" id=\"subtitle\">A carregar cockpit real do backend...</div>
      </div>
      <div class=\"status-pill\"><span id=\"globalDot\" class=\"dot yellow\"></span><span id=\"globalStatus\">A carregar</span></div>
    </header>

    <div class=\"toolbar\">
      <button class=\"safe\" onclick=\"loadCockpit()\">Atualizar cockpit</button>
      <button class=\"safe\" onclick=\"openEndpoint('/api/home-control-surface/package')\">Ver package</button>
      <button class=\"safe\" onclick=\"openEndpoint('/api/home-control-surface/buttons')\">Ver botões</button>
      <button class=\"safe\" onclick=\"openEndpoint('/health')\">Health</button>
    </div>

    <section class=\"grid\" id=\"cards\"><div class=\"empty\">A carregar módulos...</div></section>

    <section class=\"output\"><pre id=\"output\">Sem output ainda.</pre></section>
  </div>

  <div class=\"modal-backdrop\" id=\"modalBackdrop\">
    <div class=\"modal\">
      <h3 id=\"modalTitle\">Executar ação</h3>
      <div id=\"modalDesc\" class=\"desc\"></div>
      <div id=\"modalWarn\" class=\"warning\"></div>
      <textarea id=\"payloadBox\"></textarea>
      <div class=\"modal-actions\">
        <button onclick=\"closeModal()\">Cancelar</button>
        <button class=\"approval_required\" id=\"confirmButton\">Executar</button>
      </div>
    </div>
  </div>

  <script>
    const API_PACKAGE = '/api/home-control-surface/package';
    let pendingAction = null;

    const $ = (id) => document.getElementById(id);

    function setOutput(value) {
      $('output').textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
    }

    function dotClass(light) {
      if (light === 'green') return 'dot green';
      if (light === 'red') return 'dot red';
      return 'dot yellow';
    }

    async function fetchJson(endpoint, options = {}) {
      const res = await fetch(endpoint, options);
      const text = await res.text();
      let data;
      try { data = JSON.parse(text); } catch { data = { raw: text }; }
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 260)}`);
      return data;
    }

    async function loadCockpit() {
      $('cards').innerHTML = '<div class=\"empty\">A carregar módulos...</div>';
      try {
        const pkg = await fetchJson(API_PACKAGE);
        const panel = pkg.panel || {};
        const modules = panel.modules || [];
        $('subtitle').textContent = panel.description || 'Cockpit operacional';
        $('globalDot').className = dotClass(panel.traffic_light || 'yellow');
        $('globalStatus').textContent = (panel.traffic_light || 'yellow').toUpperCase();
        renderModules(modules);
        setOutput({ loaded: true, status: pkg.status, modules: modules.length, buttons: pkg.buttons?.button_count });
      } catch (err) {
        $('globalDot').className = dotClass('red');
        $('globalStatus').textContent = 'ERRO';
        $('cards').innerHTML = `<div class=\"empty\">Erro a carregar cockpit: ${escapeHtml(err.message)}</div>`;
        setOutput(String(err.stack || err));
      }
    }

    function renderModules(modules) {
      if (!modules.length) {
        $('cards').innerHTML = '<div class=\"empty\">Nenhum módulo encontrado.</div>';
        return;
      }
      $('cards').innerHTML = modules.map(module => `
        <article class=\"card\">
          <div class=\"card-head\">
            <div>
              <h2>${escapeHtml(module.label || module.id)}</h2>
              <div class=\"desc\">${escapeHtml(module.description || '')}</div>
            </div>
            <span class=\"${dotClass(module.traffic_light)}\"></span>
          </div>
          <div class=\"meta\">
            <span class=\"tag\">${escapeHtml(module.id)}</span>
            <span class=\"tag\">${escapeHtml(module.panel_endpoint || '')}</span>
            <span class=\"tag\">${escapeHtml(module.traffic_light || 'yellow')}</span>
          </div>
          <div class=\"buttons\">
            ${(module.buttons || []).map(buttonHtml).join('')}
          </div>
        </article>
      `).join('');
    }

    function buttonHtml(btn) {
      const risk = btn.risk || 'safe';
      return `<button class=\"${escapeHtml(risk)}\" onclick='prepareAction(${JSON.stringify(btn)})'>${escapeHtml(btn.label || btn.id)}</button>`;
    }

    function prepareAction(btn) {
      pendingAction = btn;
      const method = (btn.method || 'GET').toUpperCase();
      if (method === 'GET') {
        openEndpoint(btn.endpoint);
        return;
      }
      $('modalTitle').textContent = btn.label || btn.id;
      $('modalDesc').textContent = `${method} ${btn.endpoint}`;
      $('modalWarn').textContent = btn.requires_confirmation ? 'Esta ação exige confirmação. Confirma o payload antes de executar.' : '';
      $('payloadBox').value = JSON.stringify(btn.default_payload || {}, null, 2);
      $('confirmButton').onclick = executePendingAction;
      $('modalBackdrop').style.display = 'flex';
    }

    async function executePendingAction() {
      if (!pendingAction) return;
      let payload = {};
      try { payload = JSON.parse($('payloadBox').value || '{}'); }
      catch (err) { setOutput('Payload JSON inválido: ' + err.message); return; }
      closeModal();
      try {
        const data = await fetchJson(pendingAction.endpoint, {
          method: pendingAction.method || 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        setOutput(data);
      } catch (err) {
        setOutput(String(err.stack || err));
      }
    }

    async function openEndpoint(endpoint) {
      try { setOutput(await fetchJson(endpoint)); }
      catch (err) { setOutput(String(err.stack || err)); }
    }

    function closeModal() {
      $('modalBackdrop').style.display = 'none';
      pendingAction = null;
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>'\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));
    }

    window.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeModal(); });
    loadCockpit();
  </script>
</body>
</html>"""


home_visual_shell_service = HomeVisualShellService()
