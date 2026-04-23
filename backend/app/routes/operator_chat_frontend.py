from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["operator-chat-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode Operator Chat</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1220;
      --panel: #111a2e;
      --panel-2: #0f1729;
      --line: #24314f;
      --text: #e6eefc;
      --muted: #98a7c7;
      --accent: #60a5fa;
      --accent-2: #22c55e;
      --warn: #f59e0b;
      --danger: #ef4444;
      --bubble-user: #1d4ed8;
      --bubble-god: #17233d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Arial, sans-serif;
      background: linear-gradient(180deg, #09101d 0%, #0b1220 100%);
      color: var(--text);
      min-height: 100vh;
    }
    .shell {
      display: grid;
      grid-template-columns: 330px 1fr;
      min-height: 100vh;
    }
    .sidebar {
      border-right: 1px solid var(--line);
      background: rgba(12, 18, 33, 0.92);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .brand {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .brand h1 {
      margin: 0;
      font-size: 18px;
    }
    .brand small { color: var(--muted); display: block; margin-top: 4px; }
    .status-pill {
      background: rgba(34, 197, 94, 0.14);
      color: #86efac;
      border: 1px solid rgba(34, 197, 94, 0.35);
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      white-space: nowrap;
    }
    .controls, .thread-list, .header-bar, .composer, .hint-card, .modal-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
    }
    .controls { padding: 14px; display: grid; gap: 10px; }
    .controls label { font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px; }
    .controls input, .controls select, .composer textarea, .modal-card input {
      width: 100%;
      background: var(--panel-2);
      border: 1px solid var(--line);
      color: var(--text);
      border-radius: 12px;
      padding: 10px 12px;
      font: inherit;
      outline: none;
    }
    .controls button, .composer button, .modal-actions button, .inline-actions button {
      background: var(--accent);
      border: none;
      color: white;
      border-radius: 12px;
      padding: 10px 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .controls button.secondary, .modal-actions button.secondary, .inline-actions button.secondary {
      background: #334155;
    }
    .thread-list {
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-height: 0;
      overflow: auto;
    }
    .thread-row {
      padding: 12px;
      border: 1px solid transparent;
      border-radius: 14px;
      background: rgba(15, 23, 41, 0.8);
      cursor: pointer;
    }
    .thread-row.active { border-color: var(--accent); }
    .thread-row:hover { border-color: #3b82f6; }
    .thread-top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
    .thread-title { font-size: 14px; font-weight: 600; }
    .thread-summary { color: var(--muted); font-size: 12px; margin-top: 6px; }
    .badge {
      min-width: 22px;
      height: 22px;
      padding: 0 7px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      background: var(--danger);
      color: white;
    }
    .main {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      padding: 16px;
      gap: 12px;
    }
    .header-bar {
      padding: 14px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }
    .header-bar h2 { margin: 0; font-size: 18px; }
    .header-meta { color: var(--muted); font-size: 12px; display: flex; gap: 12px; flex-wrap: wrap; }
    .conversation {
      flex: 1;
      min-height: 0;
      overflow: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding-right: 4px;
    }
    .message {
      max-width: min(840px, 90%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px;
      display: grid;
      gap: 8px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }
    .message.user { align-self: flex-end; background: var(--bubble-user); border-color: rgba(147, 197, 253, 0.3); }
    .message.god_mode { align-self: flex-start; background: var(--bubble-god); }
    .message.system { align-self: center; background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.3); }
    .message-top { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; color: var(--muted); }
    .message-role { text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em; }
    .message-content { white-space: pre-wrap; line-height: 1.45; }
    .inline-card {
      margin-top: 4px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(15, 23, 41, 0.75);
      padding: 12px;
      display: grid;
      gap: 10px;
    }
    .inline-title { font-weight: 700; }
    .inline-sub { color: var(--muted); font-size: 12px; }
    .inline-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .inline-input { display: grid; gap: 8px; }
    .hint-card { padding: 12px 14px; display: none; }
    .hint-title { font-size: 13px; color: var(--muted); margin-bottom: 8px; }
    .hint-list { display: flex; flex-wrap: wrap; gap: 8px; }
    .hint-chip {
      background: rgba(96, 165, 250, 0.14);
      color: #bfdbfe;
      border: 1px solid rgba(96, 165, 250, 0.35);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
    }
    .composer {
      padding: 12px;
      display: grid;
      gap: 10px;
      position: sticky;
      bottom: 0;
      background: rgba(17, 26, 46, 0.96);
      backdrop-filter: blur(10px);
    }
    .composer-row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: flex-end;
    }
    .composer-meta { color: var(--muted); font-size: 12px; }
    .modal-shell {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.55);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      z-index: 50;
    }
    .modal-card {
      width: min(560px, 100%);
      padding: 18px;
      display: grid;
      gap: 12px;
      background: #0f172a;
    }
    .modal-title { font-size: 18px; font-weight: 700; }
    .modal-sub { color: var(--muted); line-height: 1.4; }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; }
    .pill-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .small-pill {
      background: rgba(148, 163, 184, 0.12);
      border: 1px solid rgba(148, 163, 184, 0.24);
      color: #cbd5e1;
      padding: 5px 8px;
      border-radius: 999px;
      font-size: 12px;
    }
    @media (max-width: 980px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { min-height: auto; border-right: none; border-bottom: 1px solid var(--line); }
      .conversation { padding-bottom: 4px; }
      .message { max-width: 100%; }
    }
  </style>
</head>
<body>
  <div class=\"shell\">
    <aside class=\"sidebar\">
      <div class=\"brand\">
        <div>
          <h1>God Mode</h1>
          <small>Operator Chat contínuo</small>
        </div>
        <div id=\"backendStatus\" class=\"status-pill\">Backend</div>
      </div>

      <section class=\"controls\">
        <div>
          <label for=\"tenantSelect\">Tenant</label>
          <select id=\"tenantSelect\">
            <option value=\"owner-andre\">owner-andre</option>
            <option value=\"client-demo\">client-demo</option>
          </select>
        </div>
        <div>
          <label for=\"titleInput\">Nova conversa</label>
          <input id=\"titleInput\" value=\"God Mode live operator thread\" />
        </div>
        <button id=\"createThreadBtn\">Abrir conversa</button>
      </section>

      <section class=\"thread-list\" id=\"threadList\"></section>
    </aside>

    <main class=\"main\">
      <section class=\"header-bar\">
        <div>
          <h2 id=\"activeTitle\">Sem conversa ativa</h2>
          <div class=\"header-meta\">
            <span id=\"activeTenant\">tenant: -</span>
            <span id=\"activeThread\">thread: -</span>
            <span id=\"activePending\">pendências: 0</span>
          </div>
        </div>
        <div class=\"pill-row\">
          <span class=\"small-pill\" id=\"deliveryState\">popup: idle</span>
          <span class=\"small-pill\" id=\"resumeState\">resume: idle</span>
        </div>
      </section>

      <section id=\"hintCard\" class=\"hint-card\">
        <div class=\"hint-title\">Próximos passos sugeridos</div>
        <div id=\"hintList\" class=\"hint-list\"></div>
      </section>

      <section id=\"conversation\" class=\"conversation\"></section>

      <section class=\"composer\">
        <textarea id=\"messageInput\" rows=\"3\" placeholder=\"Fala com o God Mode aqui. A conversa segue no mesmo fio.\"></textarea>
        <div class=\"composer-row\">
          <div class=\"composer-meta\" id=\"composerMeta\">Sem thread ativa</div>
          <div style=\"display:flex; gap:10px;\">
            <button id=\"refreshBtn\" class=\"secondary\">Atualizar</button>
            <button id=\"sendBtn\">Enviar</button>
          </div>
        </div>
      </section>
    </main>
  </div>

  <div id=\"modalShell\" class=\"modal-shell\">
    <div class=\"modal-card\">
      <div class=\"modal-title\" id=\"modalTitle\">Pedido do God Mode</div>
      <div class=\"modal-sub\" id=\"modalSub\"></div>
      <div class=\"pill-row\" id=\"modalPills\"></div>
      <div id=\"modalInputWrap\" style=\"display:none;\">
        <input id=\"modalInput\" />
      </div>
      <div class=\"modal-actions\" id=\"modalActions\"></div>
    </div>
  </div>

  <script>
    const state = {
      tenantId: 'owner-andre',
      threadId: null,
      threads: [],
      pendingFeed: null,
      currentThread: null,
      lastGuidance: null,
      activePopup: null,
      activeResumableActionId: null,
    };

    const qs = (s) => document.querySelector(s);
    const threadList = qs('#threadList');
    const conversation = qs('#conversation');
    const modalShell = qs('#modalShell');
    const modalTitle = qs('#modalTitle');
    const modalSub = qs('#modalSub');
    const modalActions = qs('#modalActions');
    const modalInputWrap = qs('#modalInputWrap');
    const modalInput = qs('#modalInput');
    const modalPills = qs('#modalPills');

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `HTTP ${response.status}`);
      }
      return response.json();
    }

    function escapeHtml(value) {
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('\"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    function nowStamp() {
      return new Date().toLocaleString('pt-PT');
    }

    function setBackendStatus(ok = true) {
      const el = qs('#backendStatus');
      el.textContent = ok ? 'Backend online' : 'Backend offline';
      el.style.background = ok ? 'rgba(34, 197, 94, 0.14)' : 'rgba(239, 68, 68, 0.14)';
      el.style.borderColor = ok ? 'rgba(34, 197, 94, 0.35)' : 'rgba(239, 68, 68, 0.35)';
      el.style.color = ok ? '#86efac' : '#fecaca';
    }

    function renderThreads() {
      threadList.innerHTML = '';
      const feedMap = new Map((state.pendingFeed?.threads || []).map(item => [item.thread_id, item]));
      const sorted = [...state.threads].sort((a, b) => {
        const pa = feedMap.get(a.thread_id)?.badge_count || 0;
        const pb = feedMap.get(b.thread_id)?.badge_count || 0;
        if (pb !== pa) return pb - pa;
        return a.thread_id < b.thread_id ? 1 : -1;
      });
      for (const thread of sorted) {
        const feed = feedMap.get(thread.thread_id);
        const row = document.createElement('button');
        row.className = `thread-row ${state.threadId === thread.thread_id ? 'active' : ''}`;
        row.innerHTML = `
          <div class=\"thread-top\">
            <div class=\"thread-title\">${escapeHtml(thread.conversation_title || thread.thread_id)}</div>
            ${feed?.badge_count ? `<span class=\"badge\">${feed.badge_count}</span>` : ''}
          </div>
          <div class=\"thread-summary\">${escapeHtml(feed?.latest_summary || thread.latest_summary || 'Sem resumo ainda')}</div>
        `;
        row.onclick = () => activateThread(thread.thread_id);
        threadList.appendChild(row);
      }
    }

    function renderHints() {
      const card = qs('#hintCard');
      const list = qs('#hintList');
      const items = state.lastGuidance?.reply?.suggested_next_steps || [];
      if (!items.length) {
        card.style.display = 'none';
        list.innerHTML = '';
        return;
      }
      card.style.display = 'block';
      list.innerHTML = items.map(item => `<span class=\"hint-chip\">${escapeHtml(item)}</span>`).join('');
    }

    function renderConversation() {
      conversation.innerHTML = '';
      const thread = state.currentThread?.thread;
      if (!thread) {
        conversation.innerHTML = '<div class=\"message system\"><div class=\"message-content\">Abre ou seleciona uma conversa para começar.</div></div>';
        return;
      }
      for (const message of thread.messages || []) {
        const role = message.role === 'assistant' ? 'god_mode' : (message.role || 'system');
        const box = document.createElement('div');
        box.className = `message ${role}`;
        box.innerHTML = `
          <div class=\"message-top\">
            <span class=\"message-role\">${escapeHtml(role)}</span>
            <span>${escapeHtml(message.created_at || nowStamp())}</span>
          </div>
          <div class=\"message-content\">${escapeHtml(message.content || '')}</div>
        `;
        conversation.appendChild(box);
      }

      const pending = state.pendingFeed?.threads?.find(item => item.thread_id === state.threadId);
      if (pending?.has_pending_attention) {
        const card = document.createElement('div');
        card.className = 'message system';
        card.innerHTML = `
          <div class=\"message-top\"><span class=\"message-role\">pendência</span><span>${pending.badge_count} ações</span></div>
          <div class=\"message-content\">Esta conversa está à espera de ti. Existem ${pending.pending_gate_count} aprovações e ${pending.pending_input_count} pedidos de input.</div>
        `;
        conversation.appendChild(card);
      }

      injectInlineCards();
      conversation.scrollTop = conversation.scrollHeight;
    }

    async function injectInlineCards() {
      if (!state.threadId) return;
      const [requests, gates, deliveries, resumables] = await Promise.all([
        api(`/api/operator-input-request/list?thread_id=${encodeURIComponent(state.threadId)}`),
        api(`/api/operator-approval-gate/list?thread_id=${encodeURIComponent(state.threadId)}`),
        api(`/api/operator-popup-delivery/list?thread_id=${encodeURIComponent(state.threadId)}`),
        api(`/api/operator-resumable-action/list?thread_id=${encodeURIComponent(state.threadId)}`),
      ]).catch(() => [{ requests: [] }, { gates: [] }, { deliveries: [] }, { actions: [] }]);

      const pendingInput = (requests.requests || []).find(item => item.status === 'waiting_operator_input');
      const pendingGate = (gates.gates || []).find(item => item.status === 'awaiting_operator_decision');
      const reissue = (deliveries.deliveries || []).find(item => item.status === 'reissue_required');
      const resumable = (resumables.actions || []).slice().reverse()[0];

      qs('#deliveryState').textContent = `popup: ${reissue ? 'reemitir' : ((deliveries.deliveries || []).slice().reverse()[0]?.status || 'idle')}`;
      qs('#resumeState').textContent = `resume: ${resumable?.status || 'idle'}`;

      if (reissue) {
        const box = document.createElement('div');
        box.className = 'message system';
        box.innerHTML = `
          <div class=\"message-content\">Ligação interrompida. O pedido foi reenviado.</div>
          <div class=\"inline-card\">
            <div class=\"inline-title\">Popup por entregar</div>
            <div class=\"inline-sub\">O backend criou o popup mas o operador não o recebeu. Podes reabrir agora.</div>
            <div class=\"inline-actions\">
              <button id=\"reopenPopupBtn\">Reabrir popup</button>
            </div>
          </div>
        `;
        conversation.appendChild(box);
        setTimeout(() => {
          const btn = document.getElementById('reopenPopupBtn');
          if (btn) btn.onclick = () => handlePopupReissue(reissue, pendingInput);
        }, 0);
      }

      if (pendingInput) {
        const box = document.createElement('div');
        box.className = 'message god_mode';
        box.innerHTML = `
          <div class=\"message-top\"><span class=\"message-role\">god_mode</span><span>${escapeHtml(pendingInput.created_at || nowStamp())}</span></div>
          <div class=\"message-content\">${escapeHtml(pendingInput.prompt_text)}</div>
          <div class=\"inline-card\">
            <div class=\"inline-title\">${escapeHtml(pendingInput.title)}</div>
            <div class=\"inline-sub\">Campo: ${escapeHtml(pendingInput.field_label)} · provider: ${escapeHtml(pendingInput.provider_name)}</div>
            <div class=\"inline-actions\"><button id=\"answerInputBtn\">Responder agora</button></div>
          </div>
        `;
        conversation.appendChild(box);
        setTimeout(() => {
          const btn = document.getElementById('answerInputBtn');
          if (btn) btn.onclick = () => openInputModal(pendingInput);
        }, 0);
      }

      if (pendingGate) {
        const box = document.createElement('div');
        box.className = 'message god_mode';
        box.innerHTML = `
          <div class=\"message-top\"><span class=\"message-role\">god_mode</span><span>${escapeHtml(pendingGate.created_at || nowStamp())}</span></div>
          <div class=\"message-content\">É necessária a tua decisão antes de continuar.</div>
          <div class=\"inline-card\">
            <div class=\"inline-title\">${escapeHtml(pendingGate.action_label)}</div>
            <div class=\"inline-sub\">${escapeHtml(pendingGate.action_payload_summary)}</div>
            <div class=\"inline-actions\">
              <button id=\"approveBtn\">Aceitar</button>
              <button id=\"denyBtn\" class=\"secondary\">Negar</button>
            </div>
          </div>
        `;
        conversation.appendChild(box);
        setTimeout(() => {
          const approve = document.getElementById('approveBtn');
          const deny = document.getElementById('denyBtn');
          if (approve) approve.onclick = () => resolveGate(pendingGate.gate_id, 'approve');
          if (deny) deny.onclick = () => resolveGate(pendingGate.gate_id, 'deny');
        }, 0);
      }

      if (resumable) {
        const box = document.createElement('div');
        box.className = 'message system';
        box.innerHTML = `
          <div class=\"message-content\">Estado de retoma: ${escapeHtml(resumable.status)}</div>
          <div class=\"inline-card\">
            <div class=\"inline-title\">${escapeHtml(resumable.purpose_summary)}</div>
            <div class=\"inline-sub\">Estratégia: ${escapeHtml(resumable.resume_strategy)} · replay: ${escapeHtml(resumable.replay_count || 0)}</div>
            <div class=\"inline-actions\">
              <button id=\"resumeValidBtn\">Retomar com sessão válida</button>
              <button id=\"resumeExpiredBtn\" class=\"secondary\">Retomar com sessão expirada</button>
            </div>
          </div>
        `;
        conversation.appendChild(box);
        setTimeout(() => {
          const valid = document.getElementById('resumeValidBtn');
          const expired = document.getElementById('resumeExpiredBtn');
          if (valid) valid.onclick = () => resumeAction(resumable.action_id, true);
          if (expired) expired.onclick = () => resumeAction(resumable.action_id, false);
        }, 0);
      }
    }

    async function refreshThreads() {
      const tenant = state.tenantId;
      const [threads, feed] = await Promise.all([
        api(`/api/operator-conversation-thread/list?tenant_id=${encodeURIComponent(tenant)}`),
        api(`/api/operator-pending-attention/feed?tenant_id=${encodeURIComponent(tenant)}`),
      ]);
      state.threads = threads.threads || [];
      state.pendingFeed = feed;
      renderThreads();
      updateHeader();
    }

    async function activateThread(threadId) {
      state.threadId = threadId;
      const thread = await api(`/api/operator-conversation-thread/get/${encodeURIComponent(threadId)}`);
      state.currentThread = thread;
      try {
        state.lastGuidance = await api('/api/operator-response-guidance/build', {
          method: 'POST',
          body: JSON.stringify({ thread_id: threadId }),
        });
      } catch {
        state.lastGuidance = null;
      }
      renderThreads();
      renderHints();
      renderConversation();
      updateHeader();
    }

    function updateHeader() {
      const thread = state.currentThread?.thread;
      const feed = state.pendingFeed?.threads?.find(item => item.thread_id === state.threadId);
      qs('#activeTitle').textContent = thread?.conversation_title || 'Sem conversa ativa';
      qs('#activeTenant').textContent = `tenant: ${thread?.tenant_id || state.tenantId || '-'}`;
      qs('#activeThread').textContent = `thread: ${state.threadId || '-'}`;
      qs('#activePending').textContent = `pendências: ${feed?.badge_count || 0}`;
      qs('#composerMeta').textContent = state.threadId ? `A conversar em ${state.threadId}` : 'Sem thread ativa';
    }

    async function createThread() {
      const payload = {
        tenant_id: state.tenantId,
        conversation_title: qs('#titleInput').value.trim() || 'God Mode live operator thread',
        channel_mode: 'mobile_chat',
      };
      const opened = await api('/api/operator-conversation-thread/open', {
        method: 'POST', body: JSON.stringify(payload),
      });
      await refreshThreads();
      await activateThread(opened.thread.thread_id);
      await appendAssistantMessage('Conversa aberta. O God Mode vai manter este fio vivo e operar dentro do tenant selecionado.');
    }

    async function appendAssistantMessage(text) {
      if (!state.threadId) return;
      await api('/api/operator-conversation-thread/append', {
        method: 'POST',
        body: JSON.stringify({
          thread_id: state.threadId,
          role: 'assistant',
          content: text,
          operational_state: 'active',
          suggested_next_steps: ['Continuar conversa', 'Aguardar nova instrução'],
        }),
      });
      await activateThread(state.threadId);
      await refreshThreads();
    }

    async function sendMessage() {
      if (!state.threadId) {
        await createThread();
      }
      const input = qs('#messageInput');
      const content = input.value.trim();
      if (!content) return;
      await api('/api/operator-conversation-thread/append', {
        method: 'POST',
        body: JSON.stringify({
          thread_id: state.threadId,
          role: 'user',
          content,
          operational_state: 'active',
          suggested_next_steps: ['Ler contexto', 'Responder no mesmo fio'],
        }),
      });
      input.value = '';
      await appendAssistantMessage(`Recebido. Estou a acompanhar a conversa e a preservar o contexto operacional desta thread. Última instrução: ${content}`);
      await refreshThreads();
    }

    function openModal({ title, sub, pills = [], input = false, confirmText = 'Confirmar', onConfirm, secondaryText = 'Cancelar', onSecondary }) {
      modalTitle.textContent = title;
      modalSub.textContent = sub || '';
      modalPills.innerHTML = pills.map(item => `<span class=\"small-pill\">${escapeHtml(item)}</span>`).join('');
      modalInputWrap.style.display = input ? 'block' : 'none';
      modalInput.value = '';
      modalInput.type = input === 'password' ? 'password' : 'text';
      modalActions.innerHTML = '';
      const cancel = document.createElement('button');
      cancel.className = 'secondary';
      cancel.textContent = secondaryText;
      cancel.onclick = () => {
        modalShell.style.display = 'none';
        onSecondary && onSecondary();
      };
      const confirm = document.createElement('button');
      confirm.textContent = confirmText;
      confirm.onclick = async () => {
        await onConfirm(input ? modalInput.value : undefined);
        modalShell.style.display = 'none';
      };
      modalActions.append(cancel, confirm);
      modalShell.style.display = 'flex';
      if (input) setTimeout(() => modalInput.focus(), 50);
    }

    async function openInputModal(request) {
      openModal({
        title: request.title,
        sub: request.prompt_text,
        pills: [state.tenantId, request.provider_name, request.field_label],
        input: request.field_mode === 'password' ? 'password' : true,
        confirmText: 'Enviar valor',
        secondaryText: 'Fechar',
        onConfirm: async (value) => {
          await api('/api/operator-input-request/submit', {
            method: 'POST',
            body: JSON.stringify({ request_id: request.request_id, submitted_value: value || '' }),
          });
          const deliveries = await api(`/api/operator-popup-delivery/list?thread_id=${encodeURIComponent(state.threadId)}`);
          const delivery = (deliveries.deliveries || []).find(item => item.popup_ref_id === request.request_id && item.status !== 'operator_response_acknowledged');
          if (delivery) {
            await api('/api/operator-popup-delivery/acknowledge-response', {
              method: 'POST', body: JSON.stringify({ delivery_id: delivery.delivery_id }),
            });
          }
          await appendAssistantMessage('Input recebido. Vou continuar o fluxo e preservar a intenção original.');
          await refreshThreads();
          await activateThread(state.threadId);
        },
      });
    }

    async function handlePopupReissue(delivery, pendingInput) {
      await api('/api/operator-popup-delivery/mark-delivered', {
        method: 'POST', body: JSON.stringify({ delivery_id: delivery.delivery_id }),
      });
      await appendAssistantMessage('O popup foi reenviado depois da falha de ligação.');
      await refreshThreads();
      await activateThread(state.threadId);
      if (pendingInput) openInputModal(pendingInput);
    }

    async function resolveGate(gateId, decision) {
      await api('/api/operator-approval-gate/resolve', {
        method: 'POST', body: JSON.stringify({ gate_id: gateId, decision }),
      });
      await appendAssistantMessage(decision === 'approve' ? 'Ação aprovada. Vou continuar.' : 'Ação negada. O fluxo foi travado por decisão do operador.');
      await refreshThreads();
      await activateThread(state.threadId);
    }

    async function resumeAction(actionId, providerSessionStillValid) {
      await api('/api/operator-resumable-action/resume', {
        method: 'POST',
        body: JSON.stringify({ action_id: actionId, provider_session_still_valid: providerSessionStillValid }),
      });
      await appendAssistantMessage(providerSessionStillValid
        ? 'Retomei o fluxo a partir do último checkpoint seguro.'
        : 'A sessão do provider expirou. Reiniciei o fluxo e vou reaplicar o propósito original.');
      await refreshThreads();
      await activateThread(state.threadId);
    }

    async function bootstrap() {
      try {
        await api('/health');
        setBackendStatus(true);
      } catch {
        setBackendStatus(false);
      }
      state.tenantId = qs('#tenantSelect').value;
      await refreshThreads();
      if (state.threads[0]) {
        await activateThread(state.threads[0].thread_id);
      } else {
        renderConversation();
      }
    }

    qs('#tenantSelect').addEventListener('change', async (event) => {
      state.tenantId = event.target.value;
      state.threadId = null;
      state.currentThread = null;
      await refreshThreads();
      renderConversation();
      renderHints();
      updateHeader();
    });
    qs('#createThreadBtn').onclick = () => createThread();
    qs('#refreshBtn').onclick = async () => { await refreshThreads(); if (state.threadId) await activateThread(state.threadId); };
    qs('#sendBtn').onclick = () => sendMessage();
    qs('#messageInput').addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });
    modalShell.addEventListener('click', (event) => {
      if (event.target === modalShell) modalShell.style.display = 'none';
    });
    bootstrap();
  </script>
</body>
</html>
"""


@router.get('/app/operator-chat', response_class=HTMLResponse)
async def operator_chat_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
