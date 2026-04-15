const BACKEND_BASE_URL = "https://devops-god-mode-backend.onrender.com";

const backendBadge = document.getElementById("backendBadge");
const backendStatusValue = document.getElementById("backendStatusValue");
const backendProfileValue = document.getElementById("backendProfileValue");
const decisionBadge = document.getElementById("decisionBadge");
const responseOutput = document.getElementById("responseOutput");
const cardsContainer = document.getElementById("cardsContainer");

const repoInput = document.getElementById("repoInput");
const pathInput = document.getElementById("pathInput");
const branchInput = document.getElementById("branchInput");
const requestInput = document.getElementById("requestInput");

const refreshStatusButton = document.getElementById("refreshStatusButton");
const runMobileCockpitButton = document.getElementById("runMobileCockpitButton");
const runExecutionButton = document.getElementById("runExecutionButton");

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
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

function buildPayload() {
  return {
    text: requestInput.value,
    repo_full_name: repoInput.value,
    preferred_path: pathInput.value,
    proposed_branch: branchInput.value,
    registry_context: {
      ecosystem_key: "baribudos-ecosystem",
      related_repos: [
        "AndreVazao/baribudos-studio",
        "AndreVazao/baribudos-studio-website",
      ],
    },
    desired_visibility: "private",
    lifecycle_mode: "public_until_product_ready",
    build_strategy: "github_actions_free_public",
    product_ready: false,
    base_branch: "main",
  };
}

function renderCompactCards(cards = []) {
  cardsContainer.innerHTML = "";
  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "compact-card";
    article.innerHTML = `
      <p class="label">${card.title}</p>
      <p class="value">${card.value || "—"}</p>
    `;
    cardsContainer.appendChild(article);
  });
}

function renderResponse(data) {
  responseOutput.textContent = JSON.stringify(data, null, 2);

  const decision = data?.decision || data?.approval_shell?.decision || "sem decisão";
  decisionBadge.textContent = decision;
  decisionBadge.className = "badge";
  if (decision === "ok") decisionBadge.classList.add("badge-success");
  else if (decision === "altera") decisionBadge.classList.add("badge-warning");
  else if (decision === "rejeita") decisionBadge.classList.add("badge-muted");
  else decisionBadge.classList.add("badge-muted");

  if (data?.compact_cards) {
    renderCompactCards(data.compact_cards);
    return;
  }

  if (data?.approval_shell?.compact_summary) {
    renderCompactCards([
      { title: "Repo alvo", value: data.approval_shell.compact_summary.repo },
      { title: "Ficheiro alvo", value: data.approval_shell.compact_summary.path },
      { title: "Branch sugerida", value: data.approval_shell.compact_summary.branch },
      { title: "Operação", value: data.approval_shell.compact_summary.operation },
    ]);
    return;
  }

  cardsContainer.innerHTML = "";
}

async function refreshBackendStatus() {
  backendBadge.textContent = "a validar";
  backendBadge.className = "badge badge-warning";
  try {
    const root = await fetchJson(`${BACKEND_BASE_URL}/`);
    const ops = await fetchJson(`${BACKEND_BASE_URL}/ops/status`);
    backendStatusValue.textContent = root.status || "ok";
    backendProfileValue.textContent = ops.profile || root.profile || "desconhecido";
    backendBadge.textContent = "online";
    backendBadge.className = "badge badge-success";
  } catch (error) {
    backendStatusValue.textContent = "erro";
    backendProfileValue.textContent = String(error.message).slice(0, 80);
    backendBadge.textContent = "offline";
    backendBadge.className = "badge badge-danger";
  }
}

async function runMobileCockpit() {
  const payload = buildPayload();
  const data = await fetchJson(`${BACKEND_BASE_URL}/ops/mobile-cockpit`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderResponse(data);
}

async function runExecutionPipeline() {
  const payload = buildPayload();
  const data = await fetchJson(`${BACKEND_BASE_URL}/ops/execution-pipeline`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderResponse(data);
}

refreshStatusButton.addEventListener("click", refreshBackendStatus);
runMobileCockpitButton.addEventListener("click", () => runMobileCockpit().catch((error) => renderResponse({ error: error.message })));
runExecutionButton.addEventListener("click", () => runExecutionPipeline().catch((error) => renderResponse({ error: error.message })));

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./service-worker.js").catch(() => {});
  });
}

refreshBackendStatus();
