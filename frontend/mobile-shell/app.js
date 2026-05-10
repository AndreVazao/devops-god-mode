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
  const loader = q("#globalLoader");
  if (loader) loader.style.display = loading ? "block" : "none";
}

function goBack() {
  window.history.back();
}

function isRelayMode() {
  return presetSelect.value === "relay";
}

async function pushTask(action, payload) {
  setLoading(true);
  try {
    const res = await fetch(getBaseUrl() + "/push", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RELAY_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ action, payload })
    });
    const data = await res.json();
    setQuickSummary(`Tarefa enviada via Relay: ${action}`);
    return data;
  } catch (e) {
    setQuickSummary(`Erro ao enviar tarefa via Relay: ${e.message}`);
  } finally {
    setLoading(false);
  }
}

function getBaseUrl() {
  return (apiInput.value || localStorage.getItem(KEY_API) || PRESETS.relay.backend)
    .trim()
    .replace(/\/$/, "");
}

function getRelatedRepos() {
  return q("#relatedReposInput")
    .value.split(/\n+/)
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
    goal: q("#textInput").value,
    repo: q("#repoInput").value,
    context: `Preferred path: ${q("#pathInput").value} | Branch: ${q("#branchInput").value} | Base: ${q("#baseBranchInput").value}`,
    priority: "normal",
    visibility: q("#visibilityInput").value,
    lifecycle: q("#lifecycleInput").value,
    related_repos: getRelatedRepos()
  };
}

const CLOUD_URL = "https://devops-god-mode.vercel.app/api";

const RELAY_TOKEN = "GODMODE_SECURE_TOKEN"; // Should be synced with RELAY_TOKEN env

async function api(path, options = {}) {
  const localBase = getBaseUrl();
  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${RELAY_TOKEN}`,
    ...options.headers
  };

  // Normalize path: ensure it starts with /
  let normalizedPath = path.startsWith("/") ? path : "/" + path;

  try {
    // Vercel routes are in /api/* but CLOUD_URL already ends in /api
    // So if path is /push-task, it becomes .../api/push-task
    // If path is /api/system/config, we should NOT send it to Vercel as /api/api/...
    // BUT the prompt says "Vercel passa a ter API real (relay)" and lists routes like /api/push-task.ts
    // Wait, if I create api/push-task.ts, the URL is /api/push-task

    // Let's check how the Vercel routes are intended to be accessed.
    // The user said: "Vercel passa a ter API real (relay) Cria pasta: /api"
    // So the endpoints are indeed under /api/

    let cloudPath = normalizedPath;

    // If CLOUD_URL is ".../api", then cloudPath should just be the part after /api
    const cloudBase = CLOUD_URL.endsWith("/api") ? CLOUD_URL.slice(0, -4) : CLOUD_URL;

    const res = await fetch(cloudBase + normalizedPath, { ...options, headers });
    if (res.ok) return res;
  } catch (e) {
    console.warn("Cloud API failed, falling back to local", e);
  }

  return fetch(localBase + normalizedPath, { ...options, headers });
}

async function fetchJson(path, options = {}) {
  // If path starts with http, it's an absolute URL, use fetch directly
  // Otherwise, use our smart routing api()
  let response;
  if (path.startsWith("http")) {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } else {
    response = await api(path, options);
  }

  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }

  if (!response.ok) throw new Error(JSON.stringify(data));
  return data;
}

function renderCards(cards) {
  compactCards.innerHTML = "";
  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "compact-card";
    article.innerHTML = `<p class="label">${card.title}</p><p class="value">${card.value || "—"}</p>`;
    compactCards.appendChild(article);
  });
}

function renderDecision(decision) {
  decisionBadge.textContent = decision || "sem decisão";
  decisionBadge.className = "badge";

  if (decision === "ok") decisionBadge.classList.add("badge-success");
  else if (decision === "altera") decisionBadge.classList.add("badge-warning");
  else if (decision === "rejeita") decisionBadge.classList.add("badge-danger");
  else decisionBadge.classList.add("badge-neutral");
}

function setQuickSummary(text) {
  quickSummaryOutput.textContent = text;
}

function setMode(mode) {
  localStorage.setItem(KEY_MODE, mode);
  q("#drivingModeBtn").classList.toggle("mode-btn-active", mode === "driving");
  q("#assistedModeBtn").classList.toggle("mode-btn-active", mode === "assisted");
  assistedFields.style.display = mode === "assisted" ? "block" : "none";
  modeSummary.textContent =
    mode === "driving"
      ? "Driving: menos distração, headline curta e decisão rápida."
      : "Assisted: mais campos, mais contexto e mais controlo manual.";
}

function setApprovalCount(count) {
  approvalCountBadge.textContent = `${count} pendentes`;
  approvalCountBadge.className = count > 0 ? "badge badge-warning" : "badge badge-success";
}

function setExecutionCount(count) {
  executionCountBadge.textContent = `${count} monitorizadas`;
  executionCountBadge.className = count > 0 ? "badge badge-info" : "badge badge-success";
}

function setReconstructionCount(count) {
  reconstructionCountBadge.textContent = `${count} propostas`;
  reconstructionCountBadge.className = count > 0 ? "badge badge-info" : "badge badge-success";
}

function renderApprovalCards(requests) {
  approvalCards.innerHTML = "";
  approvalEmptyState.style.display = requests.length > 0 ? "none" : "block";
  setApprovalCount(requests.length);
  requests.forEach((request) => {
    const card = document.createElement("article");
    card.className = "approval-card";
    const source = request.source || "origem desconhecida";
    const risk = request.risk_level || "n/a";
    const summary = request.summary || "Sem resumo";
    const details = request.details ? JSON.stringify(request.details, null, 2) : "{}";
    card.innerHTML = `
      <div class="approval-card-top">
        <div>
          <p class="label">${source}</p>
          <p class="value">${summary}</p>
        </div>
        <span class="badge ${risk === "high" ? "badge-danger" : risk === "medium" ? "badge-warning" : "badge-info"}">${risk}</span>
      </div>
      <pre class="approval-details">${details}</pre>
      <div class="action-buttons approval-action-buttons">
        <button class="decision-btn" data-approval="${request.request_id}" data-response="OK">OK</button>
        <button class="decision-btn" data-approval="${request.request_id}" data-response="ALTERA">ALTERA</button>
        <button class="decision-btn" data-approval="${request.request_id}" data-response="REJEITA">REJEITA</button>
      </div>
    `;
    approvalCards.appendChild(card);
  });
  approvalCards.querySelectorAll("button[data-approval]").forEach((button) => {
    button.onclick = () => respondApproval(button.dataset.approval, button.dataset.response);
  });
}

function renderExecutionCards(executions) {
  executionCards.innerHTML = "";
  executionEmptyState.style.display = executions.length > 0 ? "none" : "block";
  setExecutionCount(executions.length);

  executions.forEach((execution) => {
    const card = document.createElement("article");
    card.className = "execution-card";
    const status = execution.status || "unknown";
    const summary = execution.summary || "Sem resumo";
    const repo = execution.repo_full_name || "repo desconhecida";
    const path = execution.target_path || "sem ficheiro";
    const approvalId = execution.approval_request_id || "sem approval";

    card.innerHTML = `
      <div class="execution-card-top">
        <div>
          <p class="label">${repo}</p>
          <p class="value">${summary}</p>
          <p class="helper-text">${path}</p>
        </div>
        <span class="badge ${status === "waiting_for_approval" ? "badge-warning" : status === "approved_to_continue" ? "badge-success" : status === "rejected" ? "badge-danger" : "badge-info"}">${status}</span>
      </div>
      <p class="helper-text">Approval: ${approvalId}</p>
      <div class="action-row wrap-row compact-row">
        <button class="secondary-btn" data-sync-execution="${execution.execution_id}">Sync estado</button>
      </div>
    `;

    executionCards.appendChild(card);
  });
  executionCards.querySelectorAll("button[data-sync-execution]").forEach((button) => {
    button.onclick = () => syncExecution(button.dataset.syncExecution);
  });
}

function renderReconstructionCards(items) {
  reconstructionCards.innerHTML = "";
  reconstructionEmptyState.style.display = items.length > 0 ? "none" : "block";
  setReconstructionCount(items.length);

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "reconstruction-card";
    const repoName = (item.proposed_repo || {}).name || "repo-sem-nome";
    const status = item.status || "unknown";
    const source = item.source_label || "conversa sem label";
    const count = item.code_blocks_found ?? 0;
    const risks = (item.risks || []).join(", ") || "sem riscos";

    card.innerHTML = `
      <div class="reconstruction-card-top">
        <div>
          <p class="label">${source}</p>
          <p class="value">${repoName}</p>
          <p class="helper-text">${count} blocos de código</p>
        </div>
        <span class="badge ${status === "approved_to_build_repo" ? "badge-success" : status === "needs_changes" ? "badge-warning" : status === "rejected" ? "badge-danger" : "badge-info"}">${status}</span>
      </div>
      <p class="helper-text">Riscos: ${risks}</p>
      <div class="action-row wrap-row compact-row">
        <button class="secondary-btn" data-sync-reconstruction="${item.reconstruction_id}">Sync proposta</button>
      </div>
    `;

    reconstructionCards.appendChild(card);
  });

  reconstructionCards.querySelectorAll("button[data-sync-reconstruction]").forEach((button) => {
    button.onclick = () => syncReconstruction(button.dataset.syncReconstruction);
  });
}

async function refreshApprovals() {
  if (isRelayMode()) return;
  try {
    const data = await fetchJson(`/api/approval-broker/requests?status=pending`);
    renderApprovalCards(data.requests || []);
    if ((data.requests || []).length === 0) setQuickSummary("Sem approvals pendentes.");
  } catch {
    approvalCards.innerHTML = "";
    approvalEmptyState.style.display = "block";
    approvalEmptyState.textContent = "Erro ao carregar approvals.";
    setApprovalCount(0);
    setQuickSummary("Erro ao carregar approvals pendentes.");
  }
}

async function refreshExecutions() {
  if (isRelayMode()) return;
  try {
    const data = await fetchJson(`/api/execution-gate/executions`);
    renderExecutionCards(data.executions || []);
    if ((data.executions || []).length === 0) setQuickSummary("Sem execuções monitorizadas.");
  } catch {
    executionCards.innerHTML = "";
    executionEmptyState.style.display = "block";
    executionEmptyState.textContent = "Erro ao carregar execuções.";
    setExecutionCount(0);
    setQuickSummary("Erro ao carregar execuções monitorizadas.");
  }
}

async function refreshReconstructions() {
  if (isRelayMode()) return;
  try {
    const data = await fetchJson(`/api/conversation-reconstruction/proposals`);
    renderReconstructionCards(data.reconstructions || []);
    if ((data.reconstructions || []).length === 0) setQuickSummary("Sem reconstruções propostas.");
  } catch {
    reconstructionCards.innerHTML = "";
    reconstructionEmptyState.style.display = "block";
    reconstructionEmptyState.textContent = "Erro ao carregar reconstruções.";
    setReconstructionCount(0);
    setQuickSummary("Erro ao carregar reconstruções.");
  }
}

async function respondApproval(requestId, response) {
  try {
    const data = await fetchJson(`/api/approval-broker/requests/${requestId}/respond`, {
      method: "POST",
      body: JSON.stringify({ response, note: "respondido via mobile cockpit" }),
    });

    setQuickSummary(`Approval ${data.request.request_id} atualizado para ${data.request.status}.`);
    await refreshApprovals();
    await refreshExecutions();
    await refreshReconstructions();
  } catch {
    setQuickSummary("Erro ao responder ao approval.");
  }
}

async function syncExecution(executionId) {
  try {
    const data = await fetchJson(`/api/execution-gate/executions/${executionId}/sync`, {
      method: "POST",
    });

    setQuickSummary(`Execução ${data.execution.execution_id} agora está em ${data.execution.status}.`);
    await refreshExecutions();
  } catch {
    setQuickSummary("Erro ao sincronizar execução.");
  }
}

async function syncReconstruction(reconstructionId) {
  try {
    const data = await fetchJson(`/api/conversation-reconstruction/proposals/${reconstructionId}/sync`, {
      method: "POST",
    });

    setQuickSummary(`Reconstrução ${data.reconstruction.reconstruction_id} agora está em ${data.reconstruction.status}.`);
    await refreshReconstructions();
  } catch {
    setQuickSummary("Erro ao sincronizar reconstrução.");
  }
}

async function autoUpdateConnection() {
  if (isRelayMode()) return;
  try {
    const data = await fetchJson(`/api/mobile-pc-pairing/connection-manifest`);
    if (!data.ok) return;

    const currentUrl = getBaseUrl();
    const tryList = data.mobile_should_try_in_order || [];

    for (const item of tryList) {
       try {
         const health = await fetch(`${item.url.replace(/\/$/, "")}/health`, { signal: AbortSignal.timeout(2000) });
         if (health.ok) {
           if (item.url.replace(/\/$/, "") !== currentUrl) {
              apiInput.value = item.url;
              saveUrls();
              refreshStatus();
              setQuickSummary(`Ligação auto-sincronizada: ${item.mode}`);
           }
           break;
         }
       } catch (e) {
         continue;
       }
    }
  } catch (e) {
    console.error("Auto-sync failed", e);
  }
}

async function refreshStatus() {
  connectionBadge.textContent = "a validar";
  connectionBadge.className = "badge badge-warning";
  presetValue.textContent = presetSelect.value;
  try {
    if (isRelayMode()) {
       const health = await fetchJson(`${getBaseUrl()}/health`);
       backendStatusValue.textContent = health.status || "ok";
       backendProfileValue.textContent = "relay";
       profileBadge.textContent = "cloud relay";
       connectionBadge.textContent = "online";
       connectionBadge.className = "badge badge-success";
       setQuickSummary(`Ligação Relay OK em ${getBaseUrl()}`);
       return;
    }

    const root = await fetchJson(`${getBaseUrl()}/`);
    const ops = await fetchJson(`${getBaseUrl()}/api/system/config`);
    const root = await fetchJson(`/`);
    const ops = await fetchJson(`/api/system/config`);
    backendStatusValue.textContent = root.status || "ok";
    backendProfileValue.textContent = ops.runtime_mode || root.profile || "desconhecido";
    profileBadge.textContent = ops.local_brain || "backend";
    connectionBadge.textContent = "online";
    connectionBadge.className = "badge badge-success";
    setQuickSummary(`Ligação OK em ${getBaseUrl()}`);
    refreshCriticalAction();
    if (presetSelect.value !== "manual") {
       autoUpdateConnection();
    }
  } catch (error) {
    backendStatusValue.textContent = "erro";
    backendProfileValue.textContent = String(error.message).slice(0, 80);
    connectionBadge.textContent = "offline";
    connectionBadge.className = "badge badge-danger";
    setQuickSummary(`Falha na ligação a ${getBaseUrl()}`);
  }
}

async function runCockpit() {
  if (isRelayMode()) {
    return pushTask("run_cockpit", buildPayload());
  }
  const data = await fetchJson(`${getBaseUrl()}/api/real-orchestration/simulate`, {
  const data = await fetchJson(`/api/real-orchestration/simulate`, {
    method: "POST",
    body: JSON.stringify(buildPayload()),
  });
  cockpitOutput.textContent = JSON.stringify(data, null, 2);
  const summary = data.operator_summary || "Simulação concluída.";
  headlineBox.textContent = summary;
  renderDecision(data.ok ? "ok" : "rejeita");
  renderCards([
    { title: "ID Pipeline", value: data.pipeline_id },
    { title: "Steps Ready", value: (data.ready_to_execute_safe_steps || []).length },
    { title: "Gates", value: (data.execution_gates || {}).gate_count },
  ]);
  setQuickSummary(`Cockpit simulado | Pipeline: ${data.pipeline_id}`);
}

async function runExecutionPipeline() {
  if (isRelayMode()) {
    return pushTask("run_task", buildPayload());
  }
  const data = await fetchJson(`${getBaseUrl()}/api/real-orchestration/run`, {
  const data = await fetchJson(`/api/real-orchestration/run`, {
    method: "POST",
    body: JSON.stringify(buildPayload()),
  });
  executionOutput.textContent = JSON.stringify(data, null, 2);
  const summary = data.operator_summary || "Pipeline gerado.";
  headlineBox.textContent = summary;
  renderDecision(data.ok ? "ok" : "rejeita");
  renderCards([
    { title: "Repo alvo", value: data.repo || "n/a" },
    { title: "ID Pipeline", value: data.pipeline_id },
    { title: "Provider", value: (data.provider_route || {}).selected_provider?.provider_id || "none" },
  ]);
  setQuickSummary(`Pipeline real gerado para ${data.repo || "repo desconhecida"}`);
}

async function runSetupValidation() {
  if (isRelayMode()) {
    setQuickSummary("Setup validation não disponível em modo Relay.");
    return;
  }
  const statusDiv = q("#setupEnvStatus");
  const list = q("#setupEnvList");
  statusDiv.style.display = "block";
  list.innerHTML = "<li>A validar...</li>";

  try {
    const data = await fetchJson(`/api/system/setup-validation`);
    list.innerHTML = "";

    const items = [
      { label: "Paths", ...data.paths },
      { label: "Relay", ...data.relay },
      { label: "GitHub", ...data.github },
    ];

    items.forEach((item) => {
      const li = document.createElement("li");
      li.style.marginBottom = "4px";
      const icon = item.status === "ok" ? "✔" : item.status === "missing" ? "⚠" : "❌";
      const color = item.status === "ok" ? "var(--accent)" : item.status === "missing" ? "var(--warning)" : "var(--danger)";
      li.innerHTML = `<span style="color: ${color}">${icon} ${item.label}:</span> ${item.details}`;
      list.appendChild(li);
    });

    setQuickSummary("Validação de ambiente concluída.");
  } catch (e) {
    list.innerHTML = `<li style="color: var(--danger)">Erro ao validar: ${e.message}</li>`;
    setQuickSummary("Erro na validação de ambiente.");
  }
}

async function refreshCriticalAction() {
  if (isRelayMode()) return;
  const section = q("#criticalActionSection");
  const label = q("#criticalActionLabel");
  const btn = q("#criticalActionBtn");

  try {
    const data = await fetchJson(`/api/mobile-cockpit/next-critical-action`);
    const action = data.next_critical_action;

    if (action) {
      section.style.display = "block";
      label.textContent = action.label;
      btn.onclick = () => {
         fetchJson(`/api/mobile-cockpit/quick-actions/advance`, {
           method: "POST",
           body: JSON.stringify({ action_id: action.action_id })
         }).then(() => {
            setQuickSummary(`Ação ${action.action_id} executada.`);
            refreshCriticalAction();
            refreshStatus();
         }).catch(err => setQuickSummary("Erro ao executar ação crítica: " + err.message));
      };
    } else {
      section.style.display = "none";
    }
  } catch (e) {
    section.style.display = "none";
  }
}

function copySummary() {
  const text = [
    headlineBox.textContent,
    quickSummaryOutput.textContent,
    `Backend: ${getBaseUrl()}`,
    `Shell: ${shellUrlInput.value || localStorage.getItem(KEY_SHELL) || "—"}`,
    `Preset: ${presetSelect.value}`,
  ].join("\n");
  navigator.clipboard?.writeText(text).then(() => setQuickSummary("Resumo copiado.")).catch(() => setQuickSummary("Não foi possível copiar o resumo."));
}

function renderSidebar(chats) {
  if (!sidebarChats) return;
  sidebarChats.innerHTML = "";
  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "chat-sidebar-item";
    if (chat.has_unread) item.classList.add("unread");
    item.innerHTML = `
      <span>${chat.name}</span>
      ${chat.has_unread ? '<span class="unread-dot"></span>' : ''}
    `;
    sidebarChats.appendChild(item);
  });
}

// Initializing UI
apiInput.value = localStorage.getItem(KEY_API) || PRESETS.relay.backend;
shellUrlInput.value = localStorage.getItem(KEY_SHELL) || PRESETS.local_pc.shell;
presetSelect.value = localStorage.getItem(KEY_PRESET) || "relay";
setMode(localStorage.getItem(KEY_MODE) || "driving");

const mockChats = [
  {
    "id": "1",
    "name": "Deploy Vercel",
    "messages": [],
    "has_unread": true
  }
];
renderSidebar(mockChats);

refreshStatus();
refreshApprovals();
refreshExecutions();
refreshReconstructions();

q("#refreshStatusBtn").onclick = () => {
  refreshStatus();
  refreshApprovals();
  refreshExecutions();
  refreshReconstructions();
};

q("#applyPresetBtn").onclick = applyPreset;
q("#saveApiBtn").onclick = () => {
  saveUrls();
  refreshStatus();
  refreshApprovals();
  refreshExecutions();
  refreshReconstructions();
};

q("#statusBtn").onclick = refreshStatus;
q("#refreshApprovalsBtn").onclick = refreshApprovals;
q("#refreshExecutionsBtn").onclick = refreshExecutions;
q("#refreshReconstructionsBtn").onclick = refreshReconstructions;

q("#drivingModeBtn").onclick = () => setMode("driving");
q("#assistedModeBtn").onclick = () => setMode("assisted");

q("#mobileCockpitBtn").onclick = () => runCockpit().catch((error) => {
  cockpitOutput.textContent = error.message;
  headlineBox.textContent = error.message;
  renderDecision("rejeita");
  renderCards([]);
  setQuickSummary("Erro ao gerar cockpit.");
});

q("#executionBtn").onclick = () => runExecutionPipeline().catch((error) => {
  executionOutput.textContent = error.message;
  headlineBox.textContent = error.message;
  renderDecision("rejeita");
  renderCards([]);
  setQuickSummary("Erro ao gerar pipeline.");
});

q("#setupEnvBtn").onclick = runSetupValidation;
q("#copySummaryBtn").onclick = copySummary;
q("#approveOkBtn").onclick = () => setQuickSummary("Aprovação rápida: OK");
q("#approveChangeBtn").onclick = () => setQuickSummary("Aprovação rápida: ALTERA");
q("#approveRejectBtn").onclick = () => setQuickSummary("Aprovação rápida: REJEITA");

window.goBack = goBack;
let unreadCount = 0;

function renderMessage(msg) {
  const div = document.createElement("div");
  let msgType = msg.type || "bot";
  if (msgType === "chat_response") msgType = "bot";
  div.className = `msg ${msgType}`;

  if (msg.type === "approval") {
    div.innerHTML = `
      ${msg.text}
      <div class="actions">
        <button class="primary-btn" onclick="sendChatMessage('OK')">OK</button>
        <button class="secondary-btn" onclick="sendChatMessage('Cancelar')">Cancelar</button>
      </div>
    `;
  } else {
    div.textContent = msg.message || msg.text || JSON.stringify(msg);
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChatMessage(text) {
  const input = text || chatInput.value.trim();
  if (!input) return;

  renderMessage({ type: "user", message: input });
  if (!text) chatInput.value = "";

  try {
    await fetchJson("/api/push-task", {
      method: "POST",
      body: JSON.stringify({
        action: "chat",
        message: input
      })
    });
  } catch (e) {
    renderMessage({ type: "system", message: "Erro ao enviar: " + e.message });
  }
}

async function pullChatResults() {
  try {
    const data = await fetchJson("/api/pull-results");
    if (data.results && data.results.length > 0) {
      chatStatus.textContent = "online";
      chatStatus.className = "badge badge-success";

      data.results.forEach(res => {
        renderMessage(res);
        if (document.visibilityState !== "visible") {
           unreadCount++;
           updateUnreadBadge();
        }
      });
    }
  } catch (e) {
    chatStatus.textContent = "offline";
    chatStatus.className = "badge badge-neutral";
  }
}

function updateUnreadBadge() {
  if (unreadCount > 0) {
    unreadBadge.style.display = "inline-flex";
    unreadBadge.textContent = unreadCount;
  } else {
    unreadBadge.style.display = "none";
  }
}

chatSendBtn.onclick = () => sendChatMessage();
chatInput.onkeypress = (e) => {
  if (e.key === "Enter") sendChatMessage();
};

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    unreadCount = 0;
    updateUnreadBadge();
  }
});

// Start polling
setInterval(pullChatResults, 2000);

// Expose sendChatMessage globally for inline buttons
window.sendChatMessage = sendChatMessage;
