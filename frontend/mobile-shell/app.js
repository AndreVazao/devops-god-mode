const PRESETS = {
  relay: {
    label: "Vercel Relay",
    backend: "https://devops-god-mode.vercel.app/api",
    shell: "",
  },
  render: {
    label: "Render",
    backend: "https://devops-god-mode-backend.onrender.com",
    shell: "",
  },
  local_pc: {
    label: "PC local",
    backend: "http://127.0.0.1:8787",
    shell: "http://127.0.0.1:4173",
  },
  private_tunnel: {
    label: "Túnel privado/free",
    backend: "",
    shell: "",
  },
  manual: {
    label: "Manual",
    backend: "",
    shell: "",
  },
};

const KEY_API = "god_mode_api_base";
const KEY_SHELL = "god_mode_shell_url";
const KEY_MODE = "god_mode_shell_mode";
const KEY_PRESET = "god_mode_backend_preset";

const q = (selector) => document.querySelector(selector);

const apiInput = q("#apiBaseInput");
const shellUrlInput = q("#shellUrlInput");
const presetSelect = q("#backendPresetSelect");
const presetValue = q("#backendPresetValue");

const connectionBadge = q("#connectionBadge");
const profileBadge = q("#profileBadge");
const backendStatusValue = q("#backendStatusValue");
const backendProfileValue = q("#backendProfileValue");

const decisionBadge = q("#decisionBadge");
const headlineBox = q("#headlineBox");
const compactCards = q("#compactCards");
const modeSummary = q("#modeSummary");
const assistedFields = q("#assistedFields");

const executionOutput = q("#executionOutput");
const cockpitOutput = q("#cockpitOutput");
const quickSummaryOutput = q("#quickSummaryOutput");

const chatMessages = q("#chatMessages");
const chatInput = q("#chatInput");
const chatSendBtn = q("#chatSendBtn");
const chatStatus = q("#chatStatus");
const unreadBadge = q("#unreadBadge");

const approvalCards = q("#approvalCards");
const approvalEmptyState = q("#approvalEmptyState");
const approvalCountBadge = q("#approvalCountBadge");

const executionCards = q("#executionCards");
const executionEmptyState = q("#executionEmptyState");
const executionCountBadge = q("#executionCountBadge");

const reconstructionCards = q("#reconstructionCards");
const reconstructionEmptyState = q("#reconstructionEmptyState");
const reconstructionCountBadge = q("#reconstructionCountBadge");

const sidebarChats = q("#sidebarChats");

let isLoading = false;
const RELAY_TOKEN = "GODMODE_SECURE_TOKEN";

function setLoading(loading) {
  isLoading = loading;
  document.body.classList.toggle("loading", loading);
  const loader = q("#globalLoader");
  if (loader) loader.style.display = loading ? "block" : "none";
}

function goBack() {
  window.history.back();
}

function isRelayMode() {
  return presetSelect.value === "relay";
}

function getBaseUrl() {
  return (apiInput.value || localStorage.getItem(KEY_API) || PRESETS.relay.backend)
    .trim()
    .replace(/\/$/, "");
}

// Phase 222: Robust Task Sending
async function sendTask(action, payload) {
  setLoading(true);
  try {
    const res = await fetch(getBaseUrl() + "/push", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RELAY_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ action, payload, id: Date.now() })
    });
    const data = await res.json();
    setQuickSummary(`Tarefa enviada: ${action}`);
    return data;
  } catch (e) {
    setQuickSummary(`Erro ao enviar tarefa: ${e.message}`);
    console.error(e);
  } finally {
    setLoading(false);
  }
}

// Phase 222: Robust Response Fetching
async function fetchResponses() {
  try {
    const res = await fetch(getBaseUrl() + "/responses", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RELAY_TOKEN}`
      }
    });
    return await res.json();
  } catch (e) {
    console.warn("Failed to fetch responses", e);
    return [];
  }
}

// Phase 222: Chat Engine
let chats = [];
let currentChat = null;

function newChat() {
  const chat = {
    id: Date.now(),
    name: `Chat ${new Date().toLocaleTimeString()}`,
    messages: [],
    unread: false
  };
  chats.push(chat);
  currentChat = chat;
  renderSidebar(chats);
  renderChatMessages();
}

async function sendMessage(text) {
  if (!currentChat) newChat();

  const msg = {
    role: "user",
    text,
    timestamp: new Date().toISOString()
  };

  currentChat.messages.push(msg);
  renderChatMessages();

  await sendTask("chat", { text });
}

async function sync() {
  const responses = await fetchResponses();

  if (responses.length > 0) {
    chatStatus.textContent = "online";
    chatStatus.className = "badge badge-success";

    responses.forEach(r => {
      if (currentChat) {
        currentChat.messages.push({
          role: "gm",
          text: r.result?.message || r.result || JSON.stringify(r),
          timestamp: new Date().toISOString()
        });
      }

      if (document.visibilityState !== "visible") {
        unreadCount++;
        updateUnreadBadge();
      }
    });
    renderChatMessages();
  }
}

function renderChatMessages() {
  if (!currentChat) return;
  chatMessages.innerHTML = "";
  currentChat.messages.forEach(msg => {
    const div = document.createElement("div");
    div.className = `msg ${msg.role === 'user' ? 'user' : 'bot'}`;
    div.textContent = msg.text;
    chatMessages.appendChild(div);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Environment Setup
async function setupEnv() {
  await sendTask("setup_env", {});
  setQuickSummary("Pedido de configuração de ambiente enviado ao PC.");
}

// Original UI logic preservation and adaptation
function getRelatedRepos() {
  return (q("#relatedReposInput")?.value || "")
    .split(/\n+/)
    .map((value) => value.trim())
    .filter(Boolean);
}

function saveUrls() {
  localStorage.setItem(KEY_API, apiInput.value.trim());
  localStorage.setItem(KEY_SHELL, shellUrlInput.value.trim());
  localStorage.setItem(KEY_PRESET, presetSelect.value);
}

function applyPreset() {
  const preset = PRESETS[presetSelect.value] || PRESETS.relay;
  if (preset.backend) apiInput.value = preset.backend;
  if (preset.shell) shellUrlInput.value = preset.shell;
  presetValue.textContent = presetSelect.value;
  saveUrls();
  refreshStatus();
}

function buildPayload() {
  return {
    goal: q("#textInput")?.value,
    repo: q("#repoInput")?.value,
    context: `Preferred path: ${q("#pathInput")?.value} | Branch: ${q("#branchInput")?.value} | Base: ${q("#baseBranchInput")?.value}`,
    priority: "normal",
    visibility: q("#visibilityInput")?.value,
    lifecycle: q("#lifecycleInput")?.value,
    related_repos: getRelatedRepos()
  };
}

function setQuickSummary(text) {
  if (quickSummaryOutput) quickSummaryOutput.textContent = text;
}

function setMode(mode) {
  localStorage.setItem(KEY_MODE, mode);
  q("#drivingModeBtn")?.classList.toggle("mode-btn-active", mode === "driving");
  q("#assistedModeBtn")?.classList.toggle("mode-btn-active", mode === "assisted");
  if (assistedFields) assistedFields.style.display = mode === "assisted" ? "block" : "none";
  if (modeSummary) modeSummary.textContent =
    mode === "driving"
      ? "Driving: menos distração, headline curta e decisão rápida."
      : "Assisted: mais campos, mais contexto e mais controlo manual.";
}

async function refreshStatus() {
  connectionBadge.textContent = "a validar";
  connectionBadge.className = "badge badge-warning";
  presetValue.textContent = presetSelect.value;
  try {
    const healthRes = await fetch(`${getBaseUrl()}/health`, { signal: AbortSignal.timeout(3000) });
    const health = await healthRes.json();

    backendStatusValue.textContent = health.status || "ok";
    backendProfileValue.textContent = isRelayMode() ? "relay" : "local/custom";
    profileBadge.textContent = isRelayMode() ? "cloud relay" : "backend";
    connectionBadge.textContent = "online";
    connectionBadge.className = "badge badge-success";
    setQuickSummary(`Ligação OK em ${getBaseUrl()}`);
  } catch (error) {
    backendStatusValue.textContent = "erro";
    backendProfileValue.textContent = "offline";
    connectionBadge.textContent = "offline";
    connectionBadge.className = "badge badge-danger";
    setQuickSummary(`Falha na ligação a ${getBaseUrl()}`);
  }
}

function renderSidebar(chats) {
  if (!sidebarChats) return;
  sidebarChats.innerHTML = "";
  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "chat-sidebar-item";
    if (chat.unread) item.classList.add("unread");
    item.innerHTML = `
      <span>${chat.name}</span>
      ${chat.unread ? '<span class="unread-dot"></span>' : ''}
    `;
    item.onclick = () => {
      currentChat = chat;
      chat.unread = false;
      renderSidebar(chats);
      renderChatMessages();
    };
    sidebarChats.appendChild(item);
  });
}

// Initializing UI
if (apiInput) apiInput.value = localStorage.getItem(KEY_API) || PRESETS.relay.backend;
if (shellUrlInput) shellUrlInput.value = localStorage.getItem(KEY_SHELL) || PRESETS.local_pc.shell;
if (presetSelect) presetSelect.value = localStorage.getItem(KEY_PRESET) || "relay";
setMode(localStorage.getItem(KEY_MODE) || "driving");

newChat();
refreshStatus();

if (q("#refreshStatusBtn")) q("#refreshStatusBtn").onclick = refreshStatus;
if (q("#applyPresetBtn")) q("#applyPresetBtn").onclick = applyPreset;
if (q("#saveApiBtn")) q("#saveApiBtn").onclick = () => {
  saveUrls();
  refreshStatus();
};

if (q("#drivingModeBtn")) q("#drivingModeBtn").onclick = () => setMode("driving");
if (q("#assistedModeBtn")) q("#assistedModeBtn").onclick = () => setMode("assisted");

if (q("#mobileCockpitBtn")) q("#mobileCockpitBtn").onclick = () => sendTask("run_cockpit", buildPayload());
if (q("#executionBtn")) q("#executionBtn").onclick = () => sendTask("run_task", buildPayload());

if (q("#setupEnvBtn")) q("#setupEnvBtn").onclick = setupEnv;

let unreadCount = 0;
function updateUnreadBadge() {
  if (unreadBadge) {
    if (unreadCount > 0) {
      unreadBadge.style.display = "inline-flex";
      unreadBadge.textContent = unreadCount;
    } else {
      unreadBadge.style.display = "none";
    }
  }
}

if (chatSendBtn) chatSendBtn.onclick = () => sendMessage(chatInput.value.trim());
if (chatInput) chatInput.onkeypress = (e) => {
  if (e.key === "Enter") sendMessage(chatInput.value.trim());
};

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    unreadCount = 0;
    updateUnreadBadge();
  }
});

// Global Exposure
window.goBack = goBack;
window.setupEnv = setupEnv;
window.sendMessage = sendMessage;
window.newChat = newChat;

// Phase 227: Production Approval Popups
function showPopup({ title, message, actions }) {
  console.log(`🔔 Popup: ${title} - ${message}`);

  // Create modal elements
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.style.cssText = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); display:flex; align-items:center; justify-content:center; z-index:10000; padding:20px;";

  const modal = document.createElement("div");
  modal.className = "modal-content";
  modal.style.cssText = "background:#1e1e2e; border:1px solid #313244; border-radius:12px; width:100%; max-width:400px; padding:24px; box-shadow:0 10px 30px rgba(0,0,0,0.5);";

  modal.innerHTML = `
    <h3 style="margin-top:0; color:#f38ba8;">${title}</h3>
    <p style="color:#cdd6f4; line-height:1.5;">${message}</p>
    <div class="modal-actions" style="display:flex; gap:12px; margin-top:24px;">
    </div>
  `;

  const actionContainer = modal.querySelector(".modal-actions");

  return new Promise((resolve) => {
    actions.forEach(label => {
      const btn = document.createElement("button");
      btn.textContent = label;
      btn.className = "btn";
      btn.style.flex = "1";
      if (label === "Aprovar") btn.style.background = "#a6e3a1";
      if (label === "Cancelar") btn.style.background = "#f38ba8";

      btn.onclick = () => {
        document.body.removeChild(overlay);
        resolve(label);
      };
      actionContainer.appendChild(btn);
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  });
}

// Intercept critical messages for popup display
const originalSync = sync;
window.sync = async function() {
  const responses = await fetchResponses();

  if (responses.length > 0) {
    for (const r of responses) {
      // Check for approval-like responses that might need a popup
      const result = r.result || {};
      if (result.action === "deploy_vercel" || (typeof result === "string" && result.includes("Confirmar deploy"))) {
         const decision = await showPopup({
           title: "Deploy produção",
           message: "Confirmar deploy para Vercel?",
           actions: ["Aprovar", "Cancelar"]
         });

         if (decision === "Aprovar") {
           await sendTask("approve", { plan_id: result.plan_id || r.id });
         }
      }
    }
  }
  return originalSync();
};

window.showPopup = showPopup;

// Start polling for responses (using the augmented sync if redefined)
setInterval(() => window.sync ? window.sync() : sync(), 2000);
