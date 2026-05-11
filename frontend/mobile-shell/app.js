const RELAY_TOKEN = "GODMODE_SECURE_TOKEN";
const DEFAULT_RELAY_BASE = (() => {
  try {
    return new URL("/api", window.location.origin).toString().replace(/\/$/, "");
  } catch {
    return "https://devops-god-mode.vercel.app/api";
  }
})();

const PRESETS = {
  relay: {
    label: "Vercel Relay",
    backend: DEFAULT_RELAY_BASE,
    shell: new URL("/app/mobile", window.location.origin).toString(),
  },
  manual: {
    label: "Manual",
    backend: "",
    shell: "",
  },
};

const KEY_API = "god_mode_api_base";
const KEY_MODE = "god_mode_shell_mode";
const KEY_PRESET = "god_mode_backend_preset";
const KEY_CHATS = "god_mode_mobile_shell_chats_v2";
const KEY_ACTIVE_CHAT = "god_mode_mobile_shell_active_chat_v2";

const q = (selector) => document.querySelector(selector);
const apiInput = q("#apiBaseInput");
const shellUrlInput = q("#shellUrlInput");
const presetSelect = q("#backendPresetSelect");
const presetValue = q("#backendPresetValue");
const connectionBadge = q("#connectionBadge");
const profileBadge = q("#profileBadge");
const backendStatusValue = q("#backendStatusValue");
const backendProfileValue = q("#backendProfileValue");
const modeSummary = q("#modeSummary");
const assistedFields = q("#assistedFields");
const quickSummaryOutput = q("#quickSummaryOutput");
const chatMessages = q("#chatMessages");
const chatInput = q("#chatInput");
const chatSendBtn = q("#chatSendBtn");
const chatStatus = q("#chatStatus");
const unreadBadge = q("#unreadBadge");
const sidebarChats = q("#sidebarChats");
const headlineBox = q("#headlineBox");
const decisionBadge = q("#decisionBadge");
const compactCards = q("#compactCards");

let isLoading = false;
let unreadCount = 0;

function uid(prefix = "item") {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function setLoading(loading) {
  isLoading = loading;
  document.body.classList.toggle("loading", loading);
  const loader = q("#globalLoader");
  if (loader) loader.style.display = loading ? "block" : "none";
}

function goBack() {
  window.history.back();
}

function setQuickSummary(text) {
  if (quickSummaryOutput) quickSummaryOutput.textContent = text;
}

function setDecision(text, tone = "neutral") {
  if (!decisionBadge) return;
  decisionBadge.textContent = text;
  decisionBadge.className = `badge badge-${tone}`;
}

function setHeadline(text) {
  if (headlineBox) headlineBox.textContent = text;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function isManualMode() {
  return presetSelect && presetSelect.value === "manual";
}

function getBaseUrl() {
  if (isManualMode()) {
    const manual = (apiInput?.value || localStorage.getItem(KEY_API) || "").trim().replace(/\/$/, "");
    return manual || DEFAULT_RELAY_BASE;
  }
  return DEFAULT_RELAY_BASE;
}

function saveUrls() {
  localStorage.setItem(KEY_PRESET, presetSelect?.value || "relay");
  if (isManualMode()) {
    localStorage.setItem(KEY_API, (apiInput?.value || "").trim());
  } else {
    localStorage.removeItem(KEY_API);
  }
}

function applyPreset() {
  const preset = PRESETS[presetSelect?.value] || PRESETS.relay;
  if (apiInput) {
    apiInput.value = presetSelect.value === "manual"
      ? (localStorage.getItem(KEY_API) || "")
      : preset.backend;
    apiInput.readOnly = presetSelect.value !== "manual";
  }
  if (shellUrlInput) {
    shellUrlInput.value = preset.shell || new URL("/app/mobile", window.location.origin).toString();
    shellUrlInput.readOnly = true;
  }
  if (presetValue) presetValue.textContent = presetSelect?.value || "relay";
  saveUrls();
  refreshStatus();
}

function createDefaultChat(name = "God Mode Relay") {
  return {
    id: uid("chat"),
    name,
    unread: false,
    messages: [
      {
        id: uid("msg"),
        role: "system",
        text: "Shell mobile ligada ao relay cloud da Vercel. O APK já não precisa de procurar IP local por defeito.",
        timestamp: new Date().toISOString(),
      },
    ],
  };
}

function loadChats() {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY_CHATS) || "[]");
    if (Array.isArray(parsed) && parsed.length) return parsed;
  } catch {}
  return [createDefaultChat()];
}

const chats = loadChats();
let currentChat = chats.find((chat) => chat.id === localStorage.getItem(KEY_ACTIVE_CHAT)) || chats[0];

function persistChats() {
  localStorage.setItem(KEY_CHATS, JSON.stringify(chats));
  localStorage.setItem(KEY_ACTIVE_CHAT, currentChat?.id || "");
}

function renderSidebar() {
  if (!sidebarChats) return;
  sidebarChats.innerHTML = "";
  chats.forEach((chat) => {
    const item = document.createElement("div");
    item.className = "chat-sidebar-item";
    if (chat.unread) item.classList.add("unread");
    item.innerHTML = `<span>${escapeHtml(chat.name)}</span>${chat.unread ? '<span class="unread-dot"></span>' : ""}`;
    item.onclick = () => {
      currentChat = chat;
      chat.unread = false;
      unreadCount = 0;
      updateUnreadBadge();
      persistChats();
      renderSidebar();
      renderChatMessages();
    };
    sidebarChats.appendChild(item);
  });
}

function renderChatMessages() {
  if (!chatMessages || !currentChat) return;
  chatMessages.innerHTML = "";
  currentChat.messages.forEach((msg) => {
    const div = document.createElement("div");
    div.className = `msg ${msg.role === "user" ? "user" : msg.role === "gm" ? "gm" : "system"}`;
    div.textContent = msg.text;
    chatMessages.appendChild(div);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendMessage(role, text, chat = currentChat) {
  if (!chat) return;
  chat.messages.push({
    id: uid("msg"),
    role,
    text,
    timestamp: new Date().toISOString(),
  });
  persistChats();
  renderChatMessages();
}

function updateUnreadBadge() {
  if (!unreadBadge) return;
  if (unreadCount > 0) {
    unreadBadge.style.display = "inline-flex";
    unreadBadge.textContent = String(unreadCount);
  } else {
    unreadBadge.style.display = "none";
  }
}

function newChat() {
  const chat = createDefaultChat(`Chat ${chats.length + 1}`);
  chats.unshift(chat);
  currentChat = chat;
  persistChats();
  renderSidebar();
  renderChatMessages();
}

async function apiRequest(path, options = {}) {
  const headers = {
    "Authorization": `Bearer ${RELAY_TOKEN}`,
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };
  const response = await fetch(`${getBaseUrl()}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (!response.ok) {
    throw new Error(`${path} -> ${response.status}`);
  }
  return response.json();
}

async function sendTask(action, payload = {}) {
  const task = {
    id: uid("task"),
    action,
    source: "mobile-shell",
    created_at: new Date().toISOString(),
    chat_id: currentChat?.id,
    ...payload,
  };

  setLoading(true);
  try {
    await apiRequest("/push", { method: "POST", body: task });
    setDecision("pedido enviado", "info");
    setQuickSummary(`Pedido enviado para ${getBaseUrl()}`);
    return task;
  } finally {
    setLoading(false);
  }
}

async function sendMessage(text) {
  const value = (text || chatInput?.value || "").trim();
  if (!value) return;
  if (chatInput) chatInput.value = "";
  appendMessage("user", value);
  setHeadline("A aguardar resposta do God Mode...");
  try {
    await sendTask("chat", { message: value });
  } catch (error) {
    appendMessage("system", `Falha a enviar para o relay: ${error.message}`);
    setDecision("erro no relay", "danger");
  }
}

async function fetchResponses() {
  try {
    const responses = await apiRequest("/responses");
    return Array.isArray(responses) ? responses : [];
  } catch (error) {
    console.warn("Failed to fetch responses", error);
    return [];
  }
}

async function sync() {
  const responses = await fetchResponses();
  if (!responses.length) return;

  chatStatus.textContent = "online";
  chatStatus.className = "badge badge-success";

  responses.forEach((entry) => {
    const task = entry.task || {};
    const result = entry.result || {};
    const targetChat = chats.find((chat) => chat.id === task.chat_id) || currentChat;
    const text = result.message || result.error || JSON.stringify(result);
    targetChat.messages.push({
      id: uid("msg"),
      role: "gm",
      text,
      timestamp: new Date().toISOString(),
    });
    targetChat.unread = targetChat !== currentChat;
    if (targetChat !== currentChat && document.visibilityState !== "visible") {
      unreadCount += 1;
    }
  });

  persistChats();
  renderSidebar();
  renderChatMessages();
  updateUnreadBadge();
  setHeadline("Resposta recebida do God Mode.");
  setDecision("resposta pronta", "success");
}

async function refreshStatus() {
  connectionBadge.textContent = "a validar";
  connectionBadge.className = "badge badge-warning";

  try {
    const health = await fetch(`${getBaseUrl()}/health`).then((response) => {
      if (!response.ok) throw new Error(`health -> ${response.status}`);
      return response.json();
    });

    backendStatusValue.textContent = health.status || "ok";
    backendProfileValue.textContent = health.storage || "relay";
    profileBadge.textContent = isManualMode() ? "manual" : "cloud relay";
    connectionBadge.textContent = "online";
    connectionBadge.className = "badge badge-success";
    chatStatus.textContent = "online";
    chatStatus.className = "badge badge-success";
    setQuickSummary(`Ligado ao relay ${getBaseUrl()}`);
    setDecision("relay ativo", "success");
  } catch (error) {
    backendStatusValue.textContent = "erro";
    backendProfileValue.textContent = "offline";
    profileBadge.textContent = isManualMode() ? "manual" : "cloud relay";
    connectionBadge.textContent = "offline";
    connectionBadge.className = "badge badge-danger";
    chatStatus.textContent = "offline";
    chatStatus.className = "badge badge-danger";
    setQuickSummary(`Falha na ligação a ${getBaseUrl()}`);
    setDecision("relay offline", "danger");
  }
}

async function setupEnv() {
  try {
    await sendTask("goal", { text: "preparar ambiente local automaticamente e confirmar readiness" });
    appendMessage("system", "Pedido de preparação automática enviado ao backend.");
  } catch (error) {
    appendMessage("system", `Não consegui pedir a preparação automática: ${error.message}`);
  }
}

function buildGoalText() {
  return (q("#textInput")?.value || "").trim();
}

function submitGoal() {
  const goal = buildGoalText();
  if (!goal) {
    setQuickSummary("Falta o texto do pedido principal.");
    return;
  }
  sendTask("goal", { text: goal })
    .then(() => setHeadline("Objetivo enviado para a fila operacional."))
    .catch((error) => setQuickSummary(`Falha ao enviar objetivo: ${error.message}`));
}

function submitAnalysis() {
  const goal = buildGoalText();
  if (!goal) {
    setQuickSummary("Falta o texto do pedido principal.");
    return;
  }
  sendTask("think", { goal })
    .then(() => setHeadline("Pedido de análise enviado ao God Brain."))
    .catch((error) => setQuickSummary(`Falha ao pedir análise: ${error.message}`));
}

function setMode(mode) {
  localStorage.setItem(KEY_MODE, mode);
  q("#drivingModeBtn")?.classList.toggle("mode-btn-active", mode === "driving");
  q("#assistedModeBtn")?.classList.toggle("mode-btn-active", mode === "assisted");
  if (assistedFields) assistedFields.style.display = mode === "assisted" ? "block" : "none";
  if (modeSummary) {
    modeSummary.textContent = mode === "driving"
      ? "Driving: shell fixa no relay cloud e reduz decisões de infraestrutura no telemóvel."
      : "Assisted: mantém contexto extra, mas continua a usar o relay cloud como destino principal.";
  }
}

function renderCompactCards() {
  if (!compactCards) return;
  compactCards.innerHTML = `
    <div class="compact-card">
      <div class="label">Destino principal</div>
      <div class="value">${escapeHtml(DEFAULT_RELAY_BASE)}</div>
    </div>
    <div class="compact-card">
      <div class="label">Entrada APK</div>
      <div class="value">${escapeHtml(new URL("/app/mobile", window.location.origin).toString())}</div>
    </div>
  `;
}

if (apiInput) apiInput.value = localStorage.getItem(KEY_API) || DEFAULT_RELAY_BASE;
if (shellUrlInput) shellUrlInput.value = new URL("/app/mobile", window.location.origin).toString();
if (presetSelect) presetSelect.value = localStorage.getItem(KEY_PRESET) || "relay";
applyPreset();
setMode(localStorage.getItem(KEY_MODE) || "driving");
renderCompactCards();
renderSidebar();
renderChatMessages();
refreshStatus();
setHeadline("APK e shell mobile apontam para o relay cloud.");
setDecision("cloud-first", "info");

if (q("#refreshStatusBtn")) q("#refreshStatusBtn").onclick = refreshStatus;
if (q("#applyPresetBtn")) q("#applyPresetBtn").onclick = applyPreset;
if (q("#saveApiBtn")) q("#saveApiBtn").onclick = () => {
  saveUrls();
  refreshStatus();
};
if (q("#drivingModeBtn")) q("#drivingModeBtn").onclick = () => setMode("driving");
if (q("#assistedModeBtn")) q("#assistedModeBtn").onclick = () => setMode("assisted");
if (q("#mobileCockpitBtn")) q("#mobileCockpitBtn").onclick = submitGoal;
if (q("#executionBtn")) q("#executionBtn").onclick = submitAnalysis;
if (q("#setupEnvBtn")) q("#setupEnvBtn").onclick = setupEnv;
if (chatSendBtn) chatSendBtn.onclick = () => sendMessage();
if (chatInput) {
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    unreadCount = 0;
    chats.forEach((chat) => {
      chat.unread = false;
    });
    updateUnreadBadge();
    persistChats();
    renderSidebar();
  }
});

window.goBack = goBack;
window.setupEnv = setupEnv;
window.sendMessage = sendMessage;
window.newChat = newChat;

setInterval(sync, 3000);
setInterval(refreshStatus, 15000);
