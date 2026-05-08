const PRESETS = {
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

const approvalCards = q("#approvalCards");
const approvalEmptyState = q("#approvalEmptyState");
const approvalCountBadge = q("#approvalCountBadge");

const executionCards = q("#executionCards");
const executionEmptyState = q("#executionEmptyState");
const executionCountBadge = q("#executionCountBadge");

const reconstructionCards = q("#reconstructionCards");
const reconstructionEmptyState = q("#reconstructionEmptyState");
const reconstructionCountBadge = q("#reconstructionCountBadge");

function getBaseUrl() {
  return (apiInput.value || localStorage.getItem(KEY_API) || PRESETS.render.backend)
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
  const preset = PRESETS[presetSelect.value] || PRESETS.render;
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
  };
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
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
  try {
    const data = await fetchJson(`${getBaseUrl()}/api/approval-broker/requests?status=pending`);
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
  try {
    const data = await fetchJson(`${getBaseUrl()}/api/execution-gate/executions`);
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
  try {
    const data = await fetchJson(`${getBaseUrl()}/api/conversation-reconstruction/proposals`);
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
    const data = await fetchJson(`${getBaseUrl()}/api/approval-broker/requests/${requestId}/respond`, {
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
    const data = await fetchJson(`${getBaseUrl()}/api/execution-gate/executions/${executionId}/sync`, {
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
    const data = await fetchJson(`${getBaseUrl()}/api/conversation-reconstruction/proposals/${reconstructionId}/sync`, {
      method: "POST",
    });

    setQuickSummary(`Reconstrução ${data.reconstruction.reconstruction_id} agora está em ${data.reconstruction.status}.`);
    await refreshReconstructions();
  } catch {
    setQuickSummary("Erro ao sincronizar reconstrução.");
  }
}

async function autoUpdateConnection() {
  try {
    const data = await fetchJson(`${getBaseUrl()}/api/mobile-pc-pairing/connection-manifest`);
    if (!data.ok) return;

    const currentUrl = getBaseUrl();
    const tryList = data.mobile_should_try_in_order || [];

    // If current URL is already working and in the list, we might not want to jump unless it's a better mode
    // For now, let's just pick the first one that responds to /health
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
    const root = await fetchJson(`${getBaseUrl()}/`);
    const ops = await fetchJson(`${getBaseUrl()}/api/system/config`);
    backendStatusValue.textContent = root.status || "ok";
    backendProfileValue.textContent = ops.runtime_mode || root.profile || "desconhecido";
    profileBadge.textContent = ops.local_brain || "backend";
    connectionBadge.textContent = "online";
    connectionBadge.className = "badge badge-success";
    setQuickSummary(`Ligação OK em ${getBaseUrl()}`);
    refreshCriticalAction();
    // Only auto-update if we are not manually overriding
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
  const data = await fetchJson(`${getBaseUrl()}/api/real-orchestration/simulate`, {
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
  const data = await fetchJson(`${getBaseUrl()}/api/real-orchestration/run`, {
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

async function refreshCriticalAction() {
  const section = q("#criticalActionSection");
  const label = q("#criticalActionLabel");
  const btn = q("#criticalActionBtn");

  try {
    const data = await fetchJson(`${getBaseUrl()}/api/mobile-cockpit/next-critical-action`);
    const action = data.next_critical_action;

    if (action) {
      section.style.display = "block";
      label.textContent = action.label;
      btn.onclick = () => {
         fetchJson(`${getBaseUrl()}/api/mobile-cockpit/quick-actions/advance`, {
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

apiInput.value = localStorage.getItem(KEY_API) || PRESETS.render.backend;
shellUrlInput.value = localStorage.getItem(KEY_SHELL) || PRESETS.local_pc.shell;
presetSelect.value = localStorage.getItem(KEY_PRESET) || "render";
setMode(localStorage.getItem(KEY_MODE) || "driving");
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
q("#copySummaryBtn").onclick = copySummary;
q("#approveOkBtn").onclick = () => setQuickSummary("Aprovação rápida: OK");
q("#approveChangeBtn").onclick = () => setQuickSummary("Aprovação rápida: ALTERA");
q("#approveRejectBtn").onclick = () => setQuickSummary("Aprovação rápida: REJEITA");
