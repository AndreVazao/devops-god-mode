const CLOUD_BASE = window.location.origin;
const DEFAULT_RELAY_API = `${CLOUD_BASE}/api`;

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
let state = {
    chats: {},
    activeChat: null
};

// Get token from URL or localStorage
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

  let hasPendingApproval = false;

  currentChat.messages.forEach((msg) => {
    const div = document.createElement("div");
    div.className = `msg ${msg.role === "user" ? "user" : msg.role === "gm" ? "gm" : "system"}`;

    if (msg.type === "approval" || msg.type === "pending_approval") {
      hasPendingApproval = true;
      const provider = msg.provider || "GitHub";
      const icon = msg.providerIcon || "https://github.com/fluidicon.png";
      const title = msg.title || (msg.type === "approval" ? "Pedido de Aprovação" : "Executar Código?");
      const desc = msg.text || msg.code || "";
      const names = msg.names || "AndreVazao, owner-andre";
      const apiKeys = msg.apiKeys || "GOD_MODE";

      div.style.background = "none";
      div.style.padding = "0";
      div.style.maxWidth = "100%";

      div.innerHTML = `
        <div class="approval-card">
          <div class="approval-header">
            <img src="${icon}" class="provider-icon" alt="${provider}">
            <div class="provider-name">${provider}</div>
          </div>
          <div class="approval-title" style="text-align:center;">${title}</div>
          <div class="approval-description">${escapeHtml(desc)}</div>

          <div class="data-sharing">
            <div class="data-sharing-title">A partilha de dados inclui</div>
            <div class="data-row">
                <span class="data-label">Names</span>
                <span class="data-value">${escapeHtml(names)}</span>
            </div>
            <div class="data-row">
                <span class="data-label">APIKeys</span>
                <span class="data-value">${escapeHtml(apiKeys)}</span>
            </div>
          </div>

          <div class="approval-actions">
            <button class="approve-btn" onclick="${msg.type === 'approval' ? `approveAction('${msg.actionId}', '${msg.id}')` : `relayApprove(true, '${msg.id}')`}">Confirmar</button>
            <button class="reject-btn" onclick="${msg.type === 'approval' ? `rejectAction('${msg.actionId}', '${msg.id}')` : `relayApprove(false, '${msg.id}')`}">Recusar</button>
          </div>
        </div>
      `;

      // Update Floating Badge
      q("#activeTaskBadge").style.display = "flex";
      q("#activeTaskLabel").textContent = provider;
      q("#activeTaskBadge").querySelector("img").src = icon;

    } else {
      // Handle markdown-ish code blocks
      const text = escapeHtml(msg.text || "");
      div.innerHTML = text.replace(/```([\s\S]*?)```/g, '<pre style="background:#000; padding:10px; overflow:auto;">$1</pre>');
    }

    chatMessages.appendChild(div);
  });

  if (!hasPendingApproval) {
      q("#activeTaskBadge").style.display = "none";
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

window.closeActiveTask = () => {
    q("#activeTaskBadge").style.display = "none";
};

async function relayApprove(approve, msgId) {
    setLoading(true);
    try {
        await api("/relay", "PUT", { approve });
        const currentChat = state.chats[state.activeChat];
        const msg = currentChat.messages.find(m => m.id === msgId);
        if (msg) {
            msg.type = "text";
            msg.text = approve ? "✔ Execução aprovada e enviada para o PC." : "✖ Execução cancelada.";
            await api("/state", "POST", { type: "UPDATE_CHAT", payload: state.chats[state.activeChat] });
        }
        await sync();
    } catch (e) {
        console.error("Relay approve error", e);
    } finally {
        setLoading(false);
    }
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
    type: action, // consistency for relay_worker and relay.js
    source: "mobile-shell",
    chat_id: state.activeChat,
    chatId: state.activeChat,
    payload,
    content: payload.message || payload.content || ""
  };

  setLoading(true);
  try {
    const res = await api("/relay", "POST", task);
    if (res.requiresApproval) {
        // Add a pending approval message to the chat
        const msg = {
            id: uid("msg"),
            role: "system",
            type: "pending_approval",
            text: task.content,
            code: task.content
        };
        await api("/state", "POST", {
            type: "MESSAGE",
            payload: { chatId: state.activeChat, message: msg }
        });
        setDecision("aguarda aprovação", "info");
    } else {
        setDecision("pedido enviado", "info");
    }
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

    // Determine action based on simple prefix for manual control
    let action = "chat";
    let content = value;
    if (value.startsWith("run:")) {
        action = "run_code";
        content = value.replace("run:", "").trim();
    } else if (value.toLowerCase().includes("executar") || value.toLowerCase().includes("run code")) {
        action = "run_code";
    }

    await sendTask(action, { message: content, content: content });
    setHeadline("God Mode a processar...");
    await sync();
  } catch (error) {
    console.error("SendMessage error", error);
  }
}

async function sync() {
  try {
    const newState = await api("/state");
    state = newState;

    try {
        const metrics = await api("/cluster/metrics");
        const budget = await api("/cluster/budget");
        setHeadline(`Latency: ${metrics.avg_latency || 0}ms | Budget: ${(budget.remaining || 0).toFixed(2)} remaining`);
    } catch (e) {
        console.warn("Metrics/Budget fetch failed", e);
    }

    chatStatus.textContent = "ONLINE";
    chatStatus.className = "badge badge-success";

    renderSidebar();
    renderChatMessages();

    setDecision("CLOUD MODE", "success");
  } catch (error) {
    console.warn("Sync failed", error);
    chatStatus.textContent = "OFFLINE";
    chatStatus.className = "badge badge-danger";
  }
}

async function newChat() {
  const name = prompt("Nome do novo chat:", "Nova Conversa");
  if (!name) return;
  await api("/state", "POST", { type: "NEW_CHAT", payload: { name } });
  await sync();
}

// Global functions
window.toggleSidebar = toggleSidebar;
window.newChat = newChat;
window.approveAction = approveAction;
window.rejectAction = rejectAction;
window.relayApprove = relayApprove;
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
setInterval(sync, 3000);

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

setDecision("CLOUD MODE", "success");
