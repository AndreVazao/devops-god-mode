from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["operator-chat-sync-frontend"])

HTML = """
<!doctype html>
<html lang=\"pt-PT\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>God Mode Operator Chat Sync</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#111a2e; --panel-2:#0f1729; --line:#24314f; --text:#e6eefc; --muted:#98a7c7; --accent:#60a5fa; --danger:#ef4444; --warn:#f59e0b; --ok:#22c55e; --bubble-user:#1d4ed8; --bubble-god:#17233d; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:linear-gradient(180deg,#09101d 0%,#0b1220 100%); color:var(--text); min-height:100vh; }
    .shell { display:grid; grid-template-columns:330px 1fr; min-height:100vh; }
    .sidebar { border-right:1px solid var(--line); background:rgba(12,18,33,.92); padding:16px; display:flex; flex-direction:column; gap:16px; }
    .brand { display:flex; justify-content:space-between; gap:12px; align-items:center; }
    .brand h1 { margin:0; font-size:18px; }
    .brand small { display:block; color:var(--muted); margin-top:4px; }
    .stack { display:grid; gap:8px; justify-items:end; }
    .pill, .net-pill, .banner, .controls, .thread-list, .header-bar, .composer, .hint-card, .modal-card { background:var(--panel); border:1px solid var(--line); border-radius:16px; }
    .pill, .net-pill { border-radius:999px; padding:6px 10px; font-size:12px; }
    .ok { color:#86efac; border-color:rgba(34,197,94,.35); background:rgba(34,197,94,.14); }
    .off { color:#fecaca; border-color:rgba(239,68,68,.35); background:rgba(239,68,68,.14); }
    .warn { color:#fde68a; border-color:rgba(245,158,11,.35); background:rgba(245,158,11,.14); }
    .controls { padding:14px; display:grid; gap:10px; }
    .controls label { font-size:12px; color:var(--muted); display:block; margin-bottom:6px; }
    input, select, textarea { width:100%; background:var(--panel-2); border:1px solid var(--line); color:var(--text); border-radius:12px; padding:10px 12px; font:inherit; outline:none; }
    button { background:var(--accent); border:none; color:white; border-radius:12px; padding:10px 14px; font-weight:600; cursor:pointer; }
    button.secondary { background:#334155; }
    .thread-list { padding:10px; display:flex; flex-direction:column; gap:8px; min-height:0; overflow:auto; }
    .thread-row { padding:12px; border:1px solid transparent; border-radius:14px; background:rgba(15,23,41,.8); cursor:pointer; }
    .thread-row.active { border-color:var(--accent); }
    .thread-top { display:flex; justify-content:space-between; gap:8px; align-items:center; }
    .thread-title { font-size:14px; font-weight:600; }
    .thread-summary { color:var(--muted); font-size:12px; margin-top:6px; }
    .badge { min-width:22px; height:22px; padding:0 7px; border-radius:999px; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; background:var(--danger); color:white; }
    .main { display:flex; flex-direction:column; min-height:100vh; padding:16px; gap:12px; }
    .banner { display:none; padding:12px 14px; }
    .header-bar { padding:14px 16px; display:flex; justify-content:space-between; align-items:center; gap:16px; }
    .header-bar h2 { margin:0; font-size:18px; }
    .header-meta { color:var(--muted); font-size:12px; display:flex; gap:12px; flex-wrap:wrap; }
    .conversation { flex:1; min-height:0; overflow:auto; display:flex; flex-direction:column; gap:12px; padding-right:4px; }
    .message { max-width:min(840px,90%); border:1px solid var(--line); border-radius:18px; padding:14px; display:grid; gap:8px; box-shadow:0 10px 24px rgba(0,0,0,.15); }
    .message.user { align-self:flex-end; background:var(--bubble-user); }
    .message.god_mode { align-self:flex-start; background:var(--bubble-god); }
    .message.system { align-self:center; background:rgba(245,158,11,.12); border-color:rgba(245,158,11,.3); }
    .message.local { align-self:flex-end; background:rgba(51,65,85,.85); }
    .message-top { display:flex; justify-content:space-between; gap:10px; font-size:12px; color:var(--muted); }
    .message-role { text-transform:uppercase; font-weight:700; letter-spacing:.06em; }
    .message-content { white-space:pre-wrap; line-height:1.45; }
    .inline-card { margin-top:4px; border:1px solid var(--line); border-radius:14px; background:rgba(15,23,41,.75); padding:12px; display:grid; gap:10px; }
    .inline-title { font-weight:700; }
    .inline-sub { color:var(--muted); font-size:12px; }
    .inline-actions { display:flex; gap:8px; flex-wrap:wrap; }
    .hint-card { padding:12px 14px; display:none; }
    .hint-title { font-size:13px; color:var(--muted); margin-bottom:8px; }
    .hint-list { display:flex; gap:8px; flex-wrap:wrap; }
    .hint-chip { background:rgba(96,165,250,.14); color:#bfdbfe; border:1px solid rgba(96,165,250,.35); border-radius:999px; padding:6px 10px; font-size:12px; }
    .composer { padding:12px; display:grid; gap:10px; position:sticky; bottom:0; background:rgba(17,26,46,.96); backdrop-filter:blur(10px); }
    .composer-row { display:flex; justify-content:space-between; gap:10px; align-items:flex-end; }
    .composer-meta { color:var(--muted); font-size:12px; }
    .modal-shell { position:fixed; inset:0; background:rgba(0,0,0,.55); display:none; align-items:center; justify-content:center; padding:18px; z-index:50; }
    .modal-card { width:min(560px,100%); padding:18px; display:grid; gap:12px; background:#0f172a; }
    .modal-title { font-size:18px; font-weight:700; }
    .modal-sub { color:var(--muted); line-height:1.4; }
    .modal-actions { display:flex; gap:10px; justify-content:flex-end; }
    .pill-row { display:flex; gap:8px; flex-wrap:wrap; }
    .small-pill { background:rgba(148,163,184,.12); border:1px solid rgba(148,163,184,.24); color:#cbd5e1; padding:5px 8px; border-radius:999px; font-size:12px; }
    @media (max-width:980px){ .shell{grid-template-columns:1fr;} .sidebar{border-right:none; border-bottom:1px solid var(--line);} .message{max-width:100%;} }
  </style>
</head>
<body>
  <div class=\"shell\">
    <aside class=\"sidebar\">
      <div class=\"brand\"><div><h1>God Mode</h1><small>Operator Chat sync cockpit</small></div><div class=\"stack\"><div id=\"backendStatus\" class=\"pill ok\">Backend online</div><div id=\"networkStatus\" class=\"net-pill ok\">Rede online</div></div></div>
      <section class=\"controls\">
        <div><label for=\"tenantSelect\">Tenant</label><select id=\"tenantSelect\"><option value=\"owner-andre\">owner-andre</option><option value=\"client-demo\">client-demo</option></select></div>
        <div><label for=\"titleInput\">Nova conversa</label><input id=\"titleInput\" value=\"God Mode live operator thread\" /></div>
        <button id=\"createThreadBtn\">Abrir conversa</button>
      </section>
      <section class=\"thread-list\" id=\"threadList\"></section>
    </aside>
    <main class=\"main\">
      <section id=\"syncBanner\" class=\"banner\"></section>
      <section class=\"header-bar\">
        <div><h2 id=\"activeTitle\">Sem conversa ativa</h2><div class=\"header-meta\"><span id=\"activeTenant\">tenant: -</span><span id=\"activeThread\">thread: -</span><span id=\"activePending\">pendências: 0</span><span id=\"activeQueue\">fila local: 0</span></div></div>
        <div class=\"pill-row\"><span class=\"small-pill\" id=\"deliveryState\">popup: idle</span><span class=\"small-pill\" id=\"resumeState\">resume: idle</span><span class=\"small-pill\" id=\"snapshotState\">snapshot: -</span></div>
      </section>
      <section id=\"hintCard\" class=\"hint-card\"><div class=\"hint-title\">Próximos passos sugeridos</div><div id=\"hintList\" class=\"hint-list\"></div></section>
      <section id=\"conversation\" class=\"conversation\"></section>
      <section class=\"composer\"><textarea id=\"messageInput\" rows=\"3\" placeholder=\"Fala com o God Mode aqui. A conversa segue no mesmo fio.\"></textarea><div class=\"composer-row\"><div class=\"composer-meta\" id=\"composerMeta\">Sem thread ativa</div><div style=\"display:flex; gap:10px;\"><button id=\"syncBtn\" class=\"secondary\">Sync</button><button id=\"refreshBtn\" class=\"secondary\">Atualizar</button><button id=\"sendBtn\">Enviar</button></div></div></section>
    </main>
  </div>
  <div id=\"modalShell\" class=\"modal-shell\"><div class=\"modal-card\"><div class=\"modal-title\" id=\"modalTitle\">Pedido do God Mode</div><div class=\"modal-sub\" id=\"modalSub\"></div><div class=\"pill-row\" id=\"modalPills\"></div><div id=\"modalInputWrap\" style=\"display:none;\"><input id=\"modalInput\" /></div><div class=\"modal-actions\" id=\"modalActions\"></div></div></div>
  <script>
    const PREFIX = 'godmode.operator.chat.';
    const state = { tenantId:'owner-andre', threadId:null, snapshot:null, offlineQueue:[] };
    const qs = (s) => document.querySelector(s);
    const conversation = qs('#conversation');
    const threadList = qs('#threadList');
    const modalShell = qs('#modalShell');
    const modalTitle = qs('#modalTitle');
    const modalSub = qs('#modalSub');
    const modalActions = qs('#modalActions');
    const modalInputWrap = qs('#modalInputWrap');
    const modalInput = qs('#modalInput');
    const modalPills = qs('#modalPills');
    const cacheKey = () => `${PREFIX}snapshot.${state.tenantId}`;
    const queueKey = () => `${PREFIX}queue.${state.tenantId}`;
    const threadKey = () => `${PREFIX}thread.${state.tenantId}`;
    const readJson = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } };
    const writeJson = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
    const latest = (arr, predicate = null) => { const items = predicate ? arr.filter(predicate) : arr; return items.length ? items[items.length - 1] : null; };
    const escapeHtml = (value) => String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\"','&quot;').replaceAll("'",'&#039;');
    const nowStamp = () => new Date().toLocaleString('pt-PT');

    async function api(path, options = {}) {
      const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
      if (!response.ok) throw new Error(await response.text() || `HTTP ${response.status}`);
      return response.json();
    }
    function setBackendStatus(ok) { const el = qs('#backendStatus'); el.textContent = ok ? 'Backend online' : 'Backend offline'; el.className = `pill ${ok ? 'ok' : 'off'}`; }
    function setNetworkStatus() { const online = navigator.onLine; const el = qs('#networkStatus'); el.textContent = online ? 'Rede online' : 'Rede offline'; el.className = `net-pill ${online ? 'ok' : 'off'}`; }
    function getFeed(threadId) { return state.snapshot?.attention?.threads?.find(item => item.thread_id === threadId); }
    function queuedForThread(threadId) { return state.offlineQueue.filter(item => item.thread_id === threadId); }
    function updateBanner(text = '', mode = 'warn') { const el = qs('#syncBanner'); if (!text) { el.style.display='none'; el.textContent=''; return; } el.style.display='block'; el.textContent=text; el.className = `banner ${mode}`; }
    function updateQueueMeta() { qs('#activeQueue').textContent = `fila local: ${state.offlineQueue.length}`; if (state.offlineQueue.length) updateBanner(`Existem ${state.offlineQueue.length} ações em fila local. Vou sincronizar quando houver rede.`, navigator.onLine ? 'warn' : 'off'); else if (!navigator.onLine) updateBanner('Estás offline. O cockpit usa cache local e volta a sincronizar depois.', 'off'); else updateBanner(''); }
    function rememberSnapshot(snapshot) { state.snapshot = snapshot; writeJson(cacheKey(), snapshot); qs('#snapshotState').textContent = `snapshot: ${snapshot ? 'ativo' : '-'}`; }
    function applySnapshot(snapshot) { if (!snapshot) return; rememberSnapshot(snapshot); renderThreads(); renderHints(); renderConversation(); updateHeader(); }
    async function fetchSnapshot(allowCache = true) {
      try {
        const path = `/api/operator-chat-runtime-snapshot/snapshot?tenant_id=${encodeURIComponent(state.tenantId)}${state.threadId ? `&thread_id=${encodeURIComponent(state.threadId)}` : ''}`;
        const snapshot = await api(path);
        setBackendStatus(true);
        applySnapshot(snapshot);
        writeJson(threadKey(), state.threadId || null);
        return snapshot;
      } catch (error) {
        setBackendStatus(false);
        if (allowCache) {
          const cached = readJson(cacheKey(), null);
          if (cached) { applySnapshot(cached); updateBanner('A usar snapshot local em cache até o backend voltar.', 'off'); return cached; }
        }
        throw error;
      }
    }
    function renderThreads() {
      threadList.innerHTML = '';
      const threads = state.snapshot?.threads || [];
      const sorted = [...threads].sort((a, b) => { const pa = getFeed(a.thread_id)?.badge_count || 0; const pb = getFeed(b.thread_id)?.badge_count || 0; if (pb !== pa) return pb - pa; return a.thread_id < b.thread_id ? 1 : -1; });
      for (const thread of sorted) {
        const feed = getFeed(thread.thread_id);
        const row = document.createElement('button');
        row.className = `thread-row ${state.threadId === thread.thread_id ? 'active' : ''}`;
        row.innerHTML = `<div class=\"thread-top\"><div class=\"thread-title\">${escapeHtml(thread.conversation_title || thread.thread_id)}</div>${feed?.badge_count ? `<span class=\"badge\">${feed.badge_count}</span>` : ''}</div><div class=\"thread-summary\">${escapeHtml(feed?.latest_summary || thread.latest_summary || 'Sem resumo ainda')}</div>`;
        row.onclick = () => activateThread(thread.thread_id);
        threadList.appendChild(row);
      }
    }
    function renderHints() { const items = state.snapshot?.guidance?.reply?.suggested_next_steps || []; const card = qs('#hintCard'); const list = qs('#hintList'); if (!items.length) { card.style.display='none'; list.innerHTML=''; return; } card.style.display='block'; list.innerHTML = items.map(item => `<span class=\"hint-chip\">${escapeHtml(item)}</span>`).join(''); }
    function renderConversation() {
      conversation.innerHTML = '';
      const thread = state.snapshot?.active_thread?.thread;
      if (!thread) { conversation.innerHTML = '<div class=\"message system\"><div class=\"message-content\">Abre ou seleciona uma conversa para começar.</div></div>'; return; }
      for (const message of thread.messages || []) {
        const role = message.role === 'assistant' ? 'god_mode' : (message.role || 'system');
        const box = document.createElement('div');
        box.className = `message ${role}`;
        box.innerHTML = `<div class=\"message-top\"><span class=\"message-role\">${escapeHtml(role)}</span><span>${escapeHtml(message.created_at || nowStamp())}</span></div><div class=\"message-content\">${escapeHtml(message.content || '')}</div>`;
        conversation.appendChild(box);
      }
      for (const item of queuedForThread(state.threadId)) {
        const box = document.createElement('div');
        box.className = 'message local';
        box.innerHTML = `<div class=\"message-top\"><span class=\"message-role\">local_queue</span><span>${escapeHtml(item.queued_at)}</span></div><div class=\"message-content\">${escapeHtml(item.preview || 'Ação pendente na fila local.')}</div>`;
        conversation.appendChild(box);
      }
      const pending = getFeed(state.threadId);
      if (pending?.has_pending_attention) {
        const card = document.createElement('div');
        card.className = 'message system';
        card.innerHTML = `<div class=\"message-top\"><span class=\"message-role\">pendência</span><span>${pending.badge_count} ações</span></div><div class=\"message-content\">Esta conversa está à espera de ti. Existem ${pending.pending_gate_count} aprovações e ${pending.pending_input_count} pedidos de input.</div>`;
        conversation.appendChild(card);
      }
      injectInlineCards();
      conversation.scrollTop = conversation.scrollHeight;
    }
    function injectInlineCards() {
      const requests = state.snapshot?.input_requests || [];
      const gates = state.snapshot?.approval_gates || [];
      const deliveries = state.snapshot?.popup_deliveries || [];
      const resumables = state.snapshot?.resumable_actions || [];
      const pendingInput = latest(requests, item => item.status === 'waiting_operator_input');
      const pendingGate = latest(gates, item => item.status === 'awaiting_operator_decision');
      const reissue = latest(deliveries, item => item.status === 'reissue_required');
      const resumable = latest(resumables);
      qs('#deliveryState').textContent = `popup: ${reissue ? 'reemitir' : (latest(deliveries)?.status || 'idle')}`;
      qs('#resumeState').textContent = `resume: ${resumable?.status || 'idle'}`;
      if (reissue) {
        const box = document.createElement('div');
        box.className = 'message system';
        box.innerHTML = `<div class=\"message-content\">Ligação interrompida. O pedido foi reenviado.</div><div class=\"inline-card\"><div class=\"inline-title\">Popup por entregar</div><div class=\"inline-sub\">O backend criou o popup mas o operador não o recebeu. Podes reabrir agora.</div><div class=\"inline-actions\"><button id=\"reopenPopupBtn\">Reabrir popup</button></div></div>`;
        conversation.appendChild(box);
        setTimeout(() => { const btn = document.getElementById('reopenPopupBtn'); if (btn) btn.onclick = () => handlePopupReissue(reissue, pendingInput); }, 0);
      }
      if (pendingInput) {
        const box = document.createElement('div');
        box.className = 'message god_mode';
        box.innerHTML = `<div class=\"message-top\"><span class=\"message-role\">god_mode</span><span>${escapeHtml(pendingInput.created_at || nowStamp())}</span></div><div class=\"message-content\">${escapeHtml(pendingInput.prompt_text)}</div><div class=\"inline-card\"><div class=\"inline-title\">${escapeHtml(pendingInput.title)}</div><div class=\"inline-sub\">Campo: ${escapeHtml(pendingInput.field_label)} · provider: ${escapeHtml(pendingInput.provider_name)}</div><div class=\"inline-actions\"><button id=\"answerInputBtn\">Responder agora</button></div></div>`;
        conversation.appendChild(box);
        setTimeout(() => { const btn = document.getElementById('answerInputBtn'); if (btn) btn.onclick = () => openInputModal(pendingInput); }, 0);
      }
      if (pendingGate) {
        const box = document.createElement('div');
        box.className = 'message god_mode';
        box.innerHTML = `<div class=\"message-top\"><span class=\"message-role\">god_mode</span><span>${escapeHtml(pendingGate.created_at || nowStamp())}</span></div><div class=\"message-content\">É necessária a tua decisão antes de continuar.</div><div class=\"inline-card\"><div class=\"inline-title\">${escapeHtml(pendingGate.action_label)}</div><div class=\"inline-sub\">${escapeHtml(pendingGate.action_payload_summary)}</div><div class=\"inline-actions\"><button id=\"approveBtn\">Aceitar</button><button id=\"denyBtn\" class=\"secondary\">Negar</button></div></div>`;
        conversation.appendChild(box);
        setTimeout(() => { const approve = document.getElementById('approveBtn'); const deny = document.getElementById('denyBtn'); if (approve) approve.onclick = () => resolveGate(pendingGate.gate_id, 'approve'); if (deny) deny.onclick = () => resolveGate(pendingGate.gate_id, 'deny'); }, 0);
      }
      if (resumable) {
        const box = document.createElement('div');
        box.className = 'message system';
        box.innerHTML = `<div class=\"message-content\">Estado de retoma: ${escapeHtml(resumable.status)}</div><div class=\"inline-card\"><div class=\"inline-title\">${escapeHtml(resumable.purpose_summary)}</div><div class=\"inline-sub\">Estratégia: ${escapeHtml(resumable.resume_strategy)} · replay: ${escapeHtml(resumable.replay_count || 0)}</div><div class=\"inline-actions\"><button id=\"resumeValidBtn\">Retomar com sessão válida</button><button id=\"resumeExpiredBtn\" class=\"secondary\">Retomar com sessão expirada</button></div></div>`;
        conversation.appendChild(box);
        setTimeout(() => { const valid = document.getElementById('resumeValidBtn'); const expired = document.getElementById('resumeExpiredBtn'); if (valid) valid.onclick = () => resumeAction(resumable.action_id, true); if (expired) expired.onclick = () => resumeAction(resumable.action_id, false); }, 0);
      }
    }
    function updateHeader() {
      const thread = state.snapshot?.active_thread?.thread;
      const feed = getFeed(state.threadId);
      qs('#activeTitle').textContent = thread?.conversation_title || 'Sem conversa ativa';
      qs('#activeTenant').textContent = `tenant: ${thread?.tenant_id || state.tenantId || '-'}`;
      qs('#activeThread').textContent = `thread: ${state.threadId || '-'}`;
      qs('#activePending').textContent = `pendências: ${feed?.badge_count || 0}`;
      qs('#composerMeta').textContent = state.threadId ? `A conversar em ${state.threadId}` : 'Sem thread ativa';
      qs('#activeQueue').textContent = `fila local: ${state.offlineQueue.length}`;
    }
    function queueAction(action) { state.offlineQueue.push({ ...action, queued_at: nowStamp() }); writeJson(queueKey(), state.offlineQueue); updateQueueMeta(); renderConversation(); }
    async function flushQueue() {
      if (!navigator.onLine || !state.offlineQueue.length) return;
      const pending = [...state.offlineQueue]; const remaining = [];
      for (const item of pending) {
        try {
          if (item.type === 'append_message') await api('/api/operator-conversation-thread/append', { method:'POST', body: JSON.stringify(item.payload) });
          else if (item.type === 'submit_input') await api('/api/operator-input-request/submit', { method:'POST', body: JSON.stringify(item.payload) });
        } catch { remaining.push(item); }
      }
      state.offlineQueue = remaining; writeJson(queueKey(), state.offlineQueue); updateQueueMeta();
      if (!remaining.length) updateBanner('Fila local sincronizada com sucesso.', 'warn');
      await fetchSnapshot(true).catch(() => {});
    }
    async function activateThread(threadId) { state.threadId = threadId; writeJson(threadKey(), threadId); await fetchSnapshot(true); }
    async function createThread() { const payload = { tenant_id: state.tenantId, conversation_title: qs('#titleInput').value.trim() || 'God Mode live operator thread', channel_mode:'mobile_chat' }; const opened = await api('/api/operator-conversation-thread/open', { method:'POST', body: JSON.stringify(payload) }); state.threadId = opened.thread.thread_id; await fetchSnapshot(true); await appendAssistantMessage('Conversa aberta. O God Mode vai manter este fio vivo e operar dentro do tenant selecionado.'); }
    async function appendAssistantMessage(text) { if (!state.threadId) return; const payload = { thread_id: state.threadId, role:'assistant', content:text, operational_state:'active', suggested_next_steps:['Continuar conversa','Aguardar nova instrução'] }; await api('/api/operator-conversation-thread/append', { method:'POST', body: JSON.stringify(payload) }); await fetchSnapshot(true); }
    async function sendMessage() { if (!state.threadId) await createThread(); const input = qs('#messageInput'); const content = input.value.trim(); if (!content) return; const payload = { thread_id: state.threadId, role:'user', content, operational_state:'active', suggested_next_steps:['Ler contexto','Responder no mesmo fio'] }; input.value = ''; if (!navigator.onLine) { queueAction({ type:'append_message', payload, thread_id: state.threadId, preview: content }); return; } await api('/api/operator-conversation-thread/append', { method:'POST', body: JSON.stringify(payload) }); await appendAssistantMessage(`Recebido. Estou a acompanhar a conversa e a preservar o contexto operacional desta thread. Última instrução: ${content}`); }
    function openModal({ title, sub, pills = [], input = false, confirmText = 'Confirmar', onConfirm, secondaryText = 'Cancelar' }) { modalTitle.textContent = title; modalSub.textContent = sub || ''; modalPills.innerHTML = pills.map(item => `<span class=\"small-pill\">${escapeHtml(item)}</span>`).join(''); modalInputWrap.style.display = input ? 'block' : 'none'; modalInput.value = ''; modalInput.type = input === 'password' ? 'password' : 'text'; modalActions.innerHTML = ''; const cancel = document.createElement('button'); cancel.className = 'secondary'; cancel.textContent = secondaryText; cancel.onclick = () => { modalShell.style.display = 'none'; }; const confirm = document.createElement('button'); confirm.textContent = confirmText; confirm.onclick = async () => { await onConfirm(input ? modalInput.value : undefined); modalShell.style.display = 'none'; }; modalActions.append(cancel, confirm); modalShell.style.display = 'flex'; if (input) setTimeout(() => modalInput.focus(), 50); }
    async function openInputModal(request) { openModal({ title: request.title, sub: request.prompt_text, pills:[state.tenantId, request.provider_name, request.field_label], input: request.field_mode === 'password' ? 'password' : true, confirmText:'Enviar valor', secondaryText:'Fechar', onConfirm: async (value) => { const payload = { request_id: request.request_id, submitted_value: value || '' }; if (!navigator.onLine) { queueAction({ type:'submit_input', payload, thread_id: state.threadId, preview:`Input pendente para ${request.field_label}` }); return; } await api('/api/operator-input-request/submit', { method:'POST', body: JSON.stringify(payload) }); const delivery = latest(state.snapshot?.popup_deliveries || [], item => item.popup_ref_id === request.request_id && item.status !== 'operator_response_acknowledged'); if (delivery) await api('/api/operator-popup-delivery/acknowledge-response', { method:'POST', body: JSON.stringify({ delivery_id: delivery.delivery_id }) }); await appendAssistantMessage('Input recebido. Vou continuar o fluxo e preservar a intenção original.'); } }); }
    async function handlePopupReissue(delivery, pendingInput) { await api('/api/operator-popup-delivery/mark-delivered', { method:'POST', body: JSON.stringify({ delivery_id: delivery.delivery_id }) }); await appendAssistantMessage('O popup foi reenviado depois da falha de ligação.'); await fetchSnapshot(true); if (pendingInput) openInputModal(pendingInput); }
    async function resolveGate(gateId, decision) { await api('/api/operator-approval-gate/resolve', { method:'POST', body: JSON.stringify({ gate_id: gateId, decision }) }); await appendAssistantMessage(decision === 'approve' ? 'Ação aprovada. Vou continuar.' : 'Ação negada. O fluxo foi travado por decisão do operador.'); }
    async function resumeAction(actionId, valid) { await api('/api/operator-resumable-action/resume', { method:'POST', body: JSON.stringify({ action_id: actionId, provider_session_still_valid: valid }) }); await appendAssistantMessage(valid ? 'Retomei o fluxo a partir do último checkpoint seguro.' : 'A sessão do provider expirou. Reiniciei o fluxo e vou reaplicar o propósito original.'); }
    async function fetchSnapshot(allowCache = true) { try { const query = `/api/operator-chat-runtime-snapshot/snapshot?tenant_id=${encodeURIComponent(state.tenantId)}${state.threadId ? `&thread_id=${encodeURIComponent(state.threadId)}` : ''}`; const snapshot = await api(query); setBackendStatus(true); rememberSnapshot(snapshot); renderThreads(); renderHints(); renderConversation(); updateHeader(); return snapshot; } catch (error) { setBackendStatus(false); if (allowCache) { const cached = readJson(cacheKey(), null); if (cached) { rememberSnapshot(cached); renderThreads(); renderHints(); renderConversation(); updateHeader(); updateBanner('A usar snapshot local em cache até o backend voltar.', 'off'); return cached; } } throw error; } }
    async function bootstrap() { setNetworkStatus(); state.offlineQueue = readJson(queueKey(), []); state.threadId = readJson(threadKey(), null); if (!state.threadId) state.threadId = null; await fetchSnapshot(true).catch(() => {}); if (!state.snapshot?.active_thread?.thread && state.snapshot?.threads?.[0] && !state.threadId) { state.threadId = state.snapshot.threads[0].thread_id; await fetchSnapshot(true).catch(() => {}); } updateQueueMeta(); if (navigator.onLine) await flushQueue(); setInterval(async () => { if (navigator.onLine) { await flushQueue(); await fetchSnapshot(true).catch(() => {}); } }, 12000); }
    qs('#tenantSelect').addEventListener('change', async (event) => { state.tenantId = event.target.value; state.offlineQueue = readJson(queueKey(), []); state.threadId = readJson(threadKey(), null); await fetchSnapshot(true).catch(() => {}); updateQueueMeta(); });
    qs('#createThreadBtn').onclick = () => createThread();
    qs('#refreshBtn').onclick = () => fetchSnapshot(true).catch(() => {});
    qs('#syncBtn').onclick = async () => { await flushQueue(); await fetchSnapshot(true).catch(() => {}); };
    qs('#sendBtn').onclick = () => sendMessage();
    qs('#messageInput').addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); } });
    modalShell.addEventListener('click', (event) => { if (event.target === modalShell) modalShell.style.display = 'none'; });
    window.addEventListener('online', async () => { setNetworkStatus(); await flushQueue(); await fetchSnapshot(true).catch(() => {}); });
    window.addEventListener('offline', () => { setNetworkStatus(); updateQueueMeta(); });
    bootstrap();
  </script>
</body>
</html>
"""


@router.get('/app/operator-chat-sync', response_class=HTMLResponse)
async def operator_chat_sync_frontend() -> HTMLResponse:
    return HTMLResponse(content=HTML)
