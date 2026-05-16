const BASE = "https://devops-god-mode.vercel.app";

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
    agents: []
};
let currentFile = null;
let editor;

async function api(path, method="GET", body){
  const r = await fetch(BASE+path,{
    method,
    headers:{
        "Content-Type":"application/json",
        "Authorization": `Bearer ${RELAY_TOKEN}`
    },
    body: body?JSON.stringify(body):undefined
  });
  return r.json();
}

async function load(){
  try {
    state = await api("/api/state");
    render();
  } catch (e) {
    console.error("Load state failed", e);
  }
}

function render(){
  const chat = state.chats && state.activeChat && state.chats[state.activeChat] ? state.chats[state.activeChat] : null;

  document.getElementById("app").innerHTML = `
    <div class="ide">

      <!-- Sidebar -->
      <div class="sidebar-icons">
        <div class="icon" onclick="load()">💬</div>
        <div class="icon" onclick="loadFiles()">📁</div>
        <div class="icon" onclick="loadLogs()">📊</div>
      </div>

      <!-- Explorer -->
      <div class="explorer" id="explorer">
        <h3>Ficheiros</h3>
      </div>

      <!-- Editor -->
      <div class="editor" id="editor"></div>

      <!-- Chat -->
      <div class="chat">
        <div class="messages" id="chatMessages">
          ${chat ? chat.messages.map(m=>`
            <div style="margin-bottom: 8px; border-bottom: 1px solid #222; padding-bottom: 4px;">
                <small style="color: #64748b;">${m.role}</small>
                <div>${m.content || m.text || ""}</div>
            </div>
          `).join("") : "Nenhum chat ativo"}
        </div>

        <div class="input">
          <input id="msg" placeholder="Escreve..."/>
          <button onclick="send()">➤</button>
        </div>

        <div class="agent-grid">
            ${(state.agents || []).map(a => `
                <div class="agent-card">
                    <div>
                        <span class="agent-status status-${a.status}"></span>
                        <strong>${a.name}</strong>
                    </div>
                    <div class="agent-output">${a.output || a.status}</div>
                </div>
            `).join("")}
        </div>

        <div class="terminal" id="terminal"></div>
      </div>

    </div>
  `;

  initEditor();
  const msgs = document.getElementById("chatMessages");
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
}

function initEditor(){
  if (typeof require === 'undefined') {
      setTimeout(initEditor, 100);
      return;
  }
  if (editor) return;

  require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@latest/min/vs' }});

  require(['vs/editor/editor.main'], function () {
    editor = monaco.editor.create(document.getElementById('editor'), {
      value: "// God Mode IDE",
      language: "javascript",
      theme: "vs-dark",
      automaticLayout: true
    });
  });
}

async function loadFiles(){
  try {
    const files = await api("/api/files");
    document.getElementById("explorer").innerHTML = `<h3>Ficheiros</h3>` + files.map(f=>`
      <div class="chat-item" style="padding: 5px; cursor: pointer;" onclick="openFile('${f}')">${f}</div>
    `).join("");
  } catch (e) {
    console.error("Load files failed", e);
  }
}

async function openFile(file){
  currentFile = file;
  try {
    const content = await api("/api/files?name="+file);
    if (editor) editor.setValue(typeof content === 'string' ? content : JSON.stringify(content, null, 2));
  } catch (e) {
    console.error("Open file failed", e);
  }
}

async function saveFile(){
  if (!currentFile || !editor) return;
  await api("/api/files","POST",{
    name: currentFile,
    content: editor.getValue()
  });

  log("✔ Guardado "+currentFile);
}

async function send(){
  const input = document.getElementById("msg");
  const text = input.value;
  if (!text) return;

  await api("/api/relay","POST",{
    chatId: state.activeChat,
    content: text,
    action: "chat"
  });

  input.value = "";
  await load();
}

function log(text){
  const t = document.getElementById("terminal");
  if (t) {
    t.innerHTML += text+"<br/>";
    t.scrollTop = t.scrollHeight;
  }
}

async function loadLogs(){
  try {
    const logs = await api("/api/logs");
    const t = document.getElementById("terminal");
    if (t && Array.isArray(logs)) {
        t.innerHTML = logs.join("<br/>");
        t.scrollTop = t.scrollHeight;
    }
  } catch (e) {}
}

setInterval(load, 2000);
load();
