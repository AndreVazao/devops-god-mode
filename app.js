const RELAY_BASE = "https://devops-god-mode.vercel.app";
const LOCAL_BASE = "http://127.0.0.1:8000";

const getRelayToken = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token') || localStorage.getItem("god_mode_relay_token") || "GODMODE_SECURE_TOKEN";
    if (urlParams.get('token')) localStorage.setItem("god_mode_relay_token", token);
    return token;
};

const RELAY_TOKEN = getRelayToken();

let state = {
    chats: {},
    activeChat: null,
    agents: [],
    providers: [],
    backendOnline: false
};

async function api(base, path, method="GET", body){
  try {
      const r = await fetch(base + path, {
        method,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${RELAY_TOKEN}`
        },
        body: body ? JSON.stringify(body) : undefined
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
  } catch (e) {
      console.error(`API Error (${path}):`, e);
      throw e;
  }
}

async function checkBackend() {
    try {
        const health = await api(LOCAL_BASE, "/health");
        state.backendOnline = (health.status === "ok");
    } catch (e) {
        state.backendOnline = false;
    }

    const banner = document.getElementById("backend-error");
    if (banner) {
        banner.style.display = state.backendOnline ? "none" : "block";
    }
}

async function loadData() {
    await checkBackend();

    // Load state from relay
    try {
        const relayState = await api(RELAY_BASE, "/api/state");
        state.agents = relayState.agents || [];
        state.chats = relayState.chats || {};
        state.activeChat = relayState.activeChat;
    } catch (e) {}

    // Load agents/providers from local if online, or use mock/relay data
    if (state.backendOnline) {
        try {
            const adapters = await api(LOCAL_BASE, "/api/chat-inventory/adapters");
            state.providers = adapters.adapters || [];
        } catch (e) {}
    }

    render();
}

function render() {
    const agentGrid = document.getElementById("agent-grid");
    if (agentGrid) {
        agentGrid.innerHTML = state.agents.length ? state.agents.map(a => `
            <div class="monitor-card">
                <span class="monitor-name">${a.name}</span>
                <span class="monitor-status">
                    <span class="dot dot-${a.status}"></span> ${a.status}
                </span>
                <div style="font-size: 10px; color: #64748b; margin-top: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${a.output || ''}
                </div>
            </div>
        `).join("") : '<div class="monitor-status">Nenhum agente ativo</div>';
    }

    const providerGrid = document.getElementById("provider-grid");
    if (providerGrid) {
        providerGrid.innerHTML = state.providers.length ? state.providers.map(p => `
            <div class="monitor-card">
                <span class="monitor-name">${p.platform || p.adapter_id}</span>
                <span class="monitor-status">
                    <span class="dot dot-online"></span> ${p.adapter_status || 'ready'}
                </span>
            </div>
        `).join("") : '<div class="monitor-status">Nenhum provider configurado</div>';
    }
}

async function sendChat() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    try {
        await api(RELAY_BASE, "/api/relay", "POST", {
            chatId: state.activeChat,
            content: text,
            action: "chat"
        });
        input.value = "";
        await loadData();
    } catch (e) {
        alert("Erro ao enviar mensagem.");
    }
}

function executeCommand(cmd) {
    const input = document.getElementById("chat-input");
    input.value = cmd;
    sendChat();
}

function createNewChat() {
    alert("Funcionalidade Novo Chat em desenvolvimento.");
}

// Initial load
loadData();
setInterval(loadData, 5000);

// Handle Enter in chat input
document.getElementById("chat-input")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
});
