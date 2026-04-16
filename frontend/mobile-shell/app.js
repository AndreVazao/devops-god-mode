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

  if (preset.backend) {
    apiInput.value = preset.backend;
  }

  if (preset.shell) {
    shellUrlInput.value = preset.shell;
  }

  presetValue.textContent = presetSelect.value;
  saveUrls();
  refreshStatus();
}

function buildPayload() {
  return {
    text: q("#textInput").value,
    repo_full_name: q("#repoInput").value,
    preferred_path: q("#pathInput").value,
    proposed_branch: q("#branchInput").value,
    registry_context: {
      ecosystem_key: "baribudos-ecosystem",
      related_repos: getRelatedRepos(),
    },
    desired_visibility: q("#visibilityInput").value,
    lifecycle_mode: q("#lifecycleInput").value,
    build_strategy: "github_actions_free_public",
    product_ready: false,
    base_branch: q("#baseBranchInput").value,
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

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

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

  if (decision === "ok") {
    decisionBadge.classList.add("badge-success");
  } else if (decision === "altera") {
    decisionBadge.classList.add("badge-warning");
  } else if (decision === "rejeita") {
    decisionBadge.classList.add("badge-danger");
  } else {
    decisionBadge.classList.add("badge-neutral");
  }
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

async function refreshApprovals() {
  try {
    const data = await fetchJson(`${getBaseUrl()}/api/approval-broker/requests?status=pending`);
    renderApprovalCards(data.requests || []);
    if ((data.requests || []).length === 0) {
      setQuickSummary("Sem approvals pendentes.");
    }
  } catch (error) {
    approvalCards.innerHTML = "";
    approvalEmptyState.style.display = "block";
    approvalEmptyState.textContent = "Erro ao carregar approvals.";
    setApprovalCount(0);
    setQuickSummary("Erro ao carregar approvals pendentes.");
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
  } catch (error) {
    setQuickSummary("Erro ao responder ao approval.");
  }
}

async function refreshStatus() {
  connectionBadge.textContent = "a validar";
  connectionBadge.className = "badge badge-warning";
  presetValue.textContent = presetSelect.value;

  try {
    const root = await fetchJson(`${getBaseUrl()}/`);
    const ops = await fetchJson(`${getBaseUrl()}/ops/status`);

    backendStatusValue.textContent = root.status || "ok";
    backendProfileValue.textContent = ops.profile || root.profile || "desconhecido";
    profileBadge.textContent = ops.profile || "backend";

    connectionBadge.textContent = "online";
    connectionBadge.className = "badge badge-success";

    setQuickSummary(`Ligação OK em ${getBaseUrl()}`);
  } catch (error) {
    backendStatusValue.textContent = "erro";
    backendProfileValue.textContent = String(error.message).slice(0, 80);

    connectionBadge.textContent = "offline";
    connectionBadge.className = "badge badge-danger";

    setQuickSummary(`Falha na ligação a ${getBaseUrl()}`);
  }
}

async function runCockpit() {
  const data = await fetchJson(`${getBaseUrl()}/ops/mobile-cockpit`, {
    method: "POST",
    body: JSON.stringify(buildPayload()),
  });

  cockpitOutput.textContent = JSON.stringify(data, null, 2);
  headlineBox.textContent = data.headline || data.next_step || "Ainda sem resposta.";
  renderDecision(data.decision);
  renderCards(data.compact_cards || []);

  setQuickSummary(`${data.headline || "Cockpit gerado"} | preset: ${presetSelect.value}`);
}

async function runExecutionPipeline() {
  const data = await fetchJson(`${getBaseUrl()}/ops/execution-pipeline`, {
    method: "POST",
    body: JSON.stringify(buildPayload()),
  });

  executionOutput.textContent = JSON.stringify(data, null, 2);
  headlineBox.textContent =
    data.next_step || (data.approval_shell || {}).headline || "Pipeline gerado.";

  renderDecision((data.approval_shell || {}).decision);

  const summary = (data.approval_shell || {}).compact_summary || {};
  renderCards([
    { title: "Repo alvo", value: summary.repo },
    { title: "Ficheiro alvo", value: summary.path },
    { title: "Branch", value: summary.branch },
    { title: "Operação", value: summary.operation },
  ]);

  setQuickSummary(`Pipeline gerado para ${summary.repo || "repo desconhecida"}`);
}

function copySummary() {
  const text = [
    headlineBox.textContent,
    quickSummaryOutput.textContent,
    `Backend: ${getBaseUrl()}`,
    `Shell: ${shellUrlInput.value || localStorage.getItem(KEY_SHELL) || "—"}`,
    `Preset: ${presetSelect.value}`,
  ].join("\n");

  navigator.clipboard
    ?.writeText(text)
    .then(() => setQuickSummary("Resumo copiado."))
    .catch(() => setQuickSummary("Não foi possível copiar o resumo."));
}

apiInput.value = localStorage.getItem(KEY_API) || PRESETS.render.backend;
shellUrlInput.value = localStorage.getItem(KEY_SHELL) || PRESETS.local_pc.shell;
presetSelect.value = localStorage.getItem(KEY_PRESET) || "render";

setMode(localStorage.getItem(KEY_MODE) || "driving");
refreshStatus();
refreshApprovals();

q("#refreshStatusBtn").onclick = () => {
  refreshStatus();
  refreshApprovals();
};
q("#applyPresetBtn").onclick = applyPreset;
q("#saveApiBtn").onclick = () => {
  saveUrls();
  refreshStatus();
  refreshApprovals();
};
q("#statusBtn").onclick = refreshStatus;
q("#refreshApprovalsBtn").onclick = refreshApprovals;

q("#drivingModeBtn").onclick = () => setMode("driving");
q("#assistedModeBtn").onclick = () => setMode("assisted");

q("#mobileCockpitBtn").onclick = () =>
  runCockpit().catch((error) => {
    cockpitOutput.textContent = error.message;
    headlineBox.textContent = error.message;
    renderDecision("rejeita");
    renderCards([]);
    setQuickSummary("Erro ao gerar cockpit.");
  });

q("#executionBtn").onclick = () =>
  runExecutionPipeline().catch((error) => {
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
