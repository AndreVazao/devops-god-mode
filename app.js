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

let state = {
    chats: {},
    activeChat: null
};

function renderSidebar() {
  if (!sidebarChats) return;
  sidebarChats.innerHTML = "";
  Object.values(state.chats).forEach((chat) => {
    const item = document.createElement("div");
    item.className = `chat-sidebar-item ${chat.id === state.activeChat ? "active" : ""}`;
    item.innerHTML = `<span>${escapeHtml(chat.name)}</span>`;
    item.onclick = async () => {
      await api("/state", "POST", { type: "SET_ACTIVE", payload: { chatId: chat.id } });
      await sync();
      if (window.innerWidth <= 600) toggleSidebar();
    };
    sidebarChats.appendChild(item);
  });
}

function renderChatMessages() {
  if (!chatMessages) return;
  const currentChat = state.chats[state.activeChat];
  chatMessages.innerHTML = "";
  if (!currentChat) return;

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
  const currentChat = state.chats[state.activeChat];
  const msg = currentChat.messages.find(m => m.id === msgId);
  if (msg) {
      msg.type = "text";
      msg.text += " -> Aprovado ✔";
      await api("/state", "POST", { type: "UPDATE_CHAT", payload: state.chats[state.activeChat] });
  }
  await sync();
}

async function rejectAction(actionId, msgId) {
  await sendTask("approve", { action_id: actionId, decision: "rejected" });
  const currentChat = state.chats[state.activeChat];
  const msg = currentChat.messages.find(m => m.id === msgId);
  if (msg) {
      msg.type = "text";
      msg.text += " -> Recusado ✖";
      await api("/state", "POST", { type: "UPDATE_CHAT", payload: state.chats[state.activeChat] });
  }
  await sync();
}

async function api(path, method = "GET", body) {
  const headers = {
    "Authorization": `Bearer ${RELAY_TOKEN}`,
    ...(body ? { "Content-Type": "application/json" } : {}),
  };
  const response = await fetch(`${DEFAULT_RELAY_API}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
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
    chat_id: state.activeChat,
    payload,
  };

  setLoading(true);
  try {
    await api("/relay", "POST", task);
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

  const msg = { role: "user", text: value };

  try {
    await api("/state", "POST", {
        type: "MESSAGE",
        payload: { chatId: state.activeChat, message: msg }
    });
    await sendTask("chat", { message: value });
    setHeadline("A aguardar resposta do God Mode...");
    await sync();
  } catch (error) {
    console.error("SendMessage error", error);
  }
}

async function sync() {
  try {
    const newState = await api("/state");
    state = newState;

    chatStatus.textContent = "online";
    chatStatus.className = "badge badge-success";

    renderSidebar();
    renderChatMessages();

    setDecision("sincronizado", "success");
  } catch (error) {
    console.warn("Sync failed", error);
    chatStatus.textContent = "offline";
    chatStatus.className = "badge badge-danger";
  }
}

async function newChat() {
  await api("/state", "POST", { type: "NEW_CHAT" });
  await sync();
}

// Global functions
window.toggleSidebar = toggleSidebar;
window.newChat = newChat;
window.approveAction = approveAction;
window.rejectAction = rejectAction;
window.sendMessage = sendMessage;
window.setupEnv = () => sendTask("setup_env");

async function handleDrop(e) {
  e.preventDefault();
  document.body.classList.remove("dragging");
  const file = e.dataTransfer.files[0];
  if (!file) return;

  const text = await file.text();
  await sendTask("file", {
    name: file.name,
    content: text
  });
  setHeadline(`Ficheiro ${file.name} enviado.`);
}

// Init
sync();
setInterval(sync, 2000);

document.body.ondragover = (e) => {
    e.preventDefault();
    document.body.classList.add("dragging");
};
document.body.ondragleave = (e) => {
    if (e.relatedTarget === null) {
        document.body.classList.remove("dragging");
    }
};
document.body.ondrop = handleDrop;

chatSendBtn.onclick = () => sendMessage();
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

renderSidebar();
renderChatMessages();
setInterval(sync, 2000);

setHeadline("Ligado ao Cloud Relay");
setDecision("cloud mode", "success");
