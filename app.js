const CLOUD_BASE = window.location.origin;
const DEFAULT_RELAY_API = `${CLOUD_BASE}/api`;

const KEY_CHATS = "god_mode_mobile_shell_chats_v3";
const KEY_ACTIVE_CHAT = "god_mode_mobile_shell_active_chat_v3";
const KEY_RELAY_TOKEN = "god_mode_relay_token";

const q = (selector) => document.querySelector(selector);
const chatMessages = q("#chatMessages");
const chatInput = q("#chatInput");
const chatSendBtn = q("#chatSendBtn");
const chatStatus = q("#chatStatus");
const sidebarChats = q("#sidebarChats");
const headlineBox = q("#headlineBox");
const decisionBadge = q("#decisionBadge");
const sidebar = q(".sidebar-nav");

let isLoading = false;

// Get token from URL or localStorage, fallback to dummy for dev only
const getRelayToken = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token') || localStorage.getItem(KEY_RELAY_TOKEN) || "GODMODE_SECURE_TOKEN";
    if (urlParams.get('token')) localStorage.setItem(KEY_RELAY_TOKEN, token);
    return token;
};

const RELAY_TOKEN = getRelayToken();

function uid(prefix = "item") {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function setLoading(loading) {
  isLoading = loading;
  document.body.classList.toggle("loading", loading);
}

function toggleSidebar() {
  sidebar.classList.toggle("active");
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

function createDefaultChat(name = "God Mode Relay") {
  return {
    id: uid("chat"),
    name,
    messages: [
      {
        id: uid("msg"),
        role: "system",
        text: "Shell mobile ligada ao relay cloud. Pronto para comandos.",
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
    item.className = `chat-sidebar-item ${chat.id === currentChat.id ? "active" : ""}`;
    item.innerHTML = `<span>${escapeHtml(chat.name)}</span>`;
    item.onclick = () => {
      currentChat = chat;
      persistChats();
      renderSidebar();
      renderChatMessages();
      if (window.innerWidth <= 600) toggleSidebar();
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

    if (msg.type === "approval") {
      div.innerHTML = `
        <div class="approval-card">
          <p><strong>⚠️ Pedido de Aprovação</strong></p>
          <p>${escapeHtml(msg.text)}</p>
          <div class="approval-actions">
            <button class="approve-btn" onclick="approveAction('${msg.actionId}', '${msg.id}')">Aceitar</button>
            <button class="reject-btn" onclick="rejectAction('${msg.actionId}', '${msg.id}')">Recusar</button>
          </div>
        </div>
      `;
    } else {
      div.textContent = msg.text;
    }

    chatMessages.appendChild(div);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function approveAction(actionId, msgId) {
  await sendTask("approve", { action_id: actionId, decision: "approved" });
  updateMessageStatus(msgId, "Aprovado ✔");
}

async function rejectAction(actionId, msgId) {
  await sendTask("approve", { action_id: actionId, decision: "rejected" });
  updateMessageStatus(msgId, "Recusado ✖");
}

function updateMessageStatus(msgId, statusText) {
  const msg = currentChat.messages.find(m => m.id === msgId);
  if (msg) {
    msg.type = "text";
    msg.text = `${msg.text} -> ${statusText}`;
    persistChats();
    renderChatMessages();
  }
}

function appendMessage(role, text, type = "text", actionId = null) {
  if (!currentChat) return;
  const msg = {
    id: uid("msg"),
    role,
    text,
    type,
    actionId,
    timestamp: new Date().toISOString(),
  };
  currentChat.messages.push(msg);
  persistChats();
  renderChatMessages();
  return msg;
}

async function apiRequest(path, options = {}) {
  const headers = {
    "Authorization": `Bearer ${RELAY_TOKEN}`,
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };
  const response = await fetch(`${DEFAULT_RELAY_API}${path}`, {
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
    chat_id: currentChat?.id,
    payload,
  };

  setLoading(true);
  try {
    await apiRequest("/push", { method: "POST", body: task });
    setDecision("pedido enviado", "info");
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
  try {
    await sendTask("chat", { message: value });
    setHeadline("A aguardar resposta do God Mode...");
  } catch (error) {
    appendMessage("system", `Erro no relay: ${error.message}`);
  }
}

async function sync() {
  try {
    const responses = await apiRequest("/responses");
    if (!responses || !responses.length) return;

    chatStatus.textContent = "online";
    chatStatus.className = "badge badge-success";

    responses.forEach((entry) => {
      const task = entry.task || {};
      const result = entry.result || {};
      const targetChat = chats.find((chat) => chat.id === (task.chat_id || entry.chat_id)) || currentChat;

      const type = result.type || "text";
      const text = result.message || result.error || JSON.stringify(result);

      appendMessage("gm", text, type, result.action_id || task.id);
    });

    setHeadline("Resposta recebida.");
    setDecision("sincronizado", "success");
  } catch (error) {
    console.warn("Sync failed", error);
    chatStatus.textContent = "offline";
    chatStatus.className = "badge badge-danger";
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

// Global functions
window.toggleSidebar = toggleSidebar;
window.newChat = newChat;
window.approveAction = approveAction;
window.rejectAction = rejectAction;
window.sendMessage = sendMessage;
window.setupEnv = () => sendTask("setup_env");

// Init
chatSendBtn.onclick = () => sendMessage();
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

renderSidebar();
renderChatMessages();
setInterval(sync, 2000);

setHeadline("Ligado ao Cloud Relay");
setDecision("cloud mode", "success");
