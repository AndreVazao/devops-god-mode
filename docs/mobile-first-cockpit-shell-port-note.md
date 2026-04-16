# Port note — feature/mobile-first-cockpit-shell

## Motivo
A branch `feature/mobile-first-cockpit-shell` estava `ahead_by: 1` relativamente ao `main`.

Esse commit extra mexe apenas em:
- `frontend/mobile-shell/index.html`

## Objetivo desta nota
Preservar o conteúdo dessa versão dentro da nova branch limpa `feature/mobile-hybrid-shell-next`, para que a branch antiga possa ser apagada sem perda de trabalho.

## Conteúdo a reaproveitar
Abaixo segue a versão do `index.html` existente na branch antiga, pronta para ser portada/adaptada nesta nova fase.

```html
<!doctype html>
<html lang="pt-PT">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
    <title>God Mode Mobile Shell</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div class="app-shell">
      <header class="topbar">
        <div>
          <div class="eyebrow">DevOps God Mode</div>
          <h1>Mobile Cockpit</h1>
          <p class="subtitle">Comando rápido, aprovação curta, backend a fazer o trabalho pesado.</p>
        </div>
        <button id="refreshStatusBtn" class="ghost-btn">Atualizar</button>
      </header>

      <section class="panel status-panel">
        <div class="panel-title-row">
          <h2>Ligação</h2>
          <span id="connectionBadge" class="badge badge-neutral">Por validar</span>
        </div>
        <label class="field">
          <span>API base</span>
          <input id="apiBaseInput" type="url" placeholder="https://devops-god-mode-backend.onrender.com" />
        </label>
        <div class="action-row compact-row">
          <button id="saveApiBtn" class="primary-btn">Guardar API</button>
          <button id="statusBtn" class="secondary-btn">Testar /ops/status</button>
        </div>
        <pre id="statusOutput" class="output-box small-output"></pre>
      </section>

      <section class="panel command-panel">
        <div class="panel-title-row">
          <h2>Pedido</h2>
          <span class="badge badge-info">mobile-first</span>
        </div>

        <label class="field">
          <span>Comando / pedido</span>
          <textarea id="textInput" rows="8" placeholder="Ex.: Repo AndreVazao/baribudos-studio. Substitui o ficheiro app/main.py por isto: ..."></textarea>
        </label>

        <div class="grid two-col">
          <label class="field">
            <span>Repo alvo</span>
            <input id="repoInput" type="text" placeholder="AndreVazao/baribudos-studio" />
          </label>
          <label class="field">
            <span>Ficheiro alvo</span>
            <input id="pathInput" type="text" placeholder="app/main.py" />
          </label>
          <label class="field">
            <span>Branch sugerida</span>
            <input id="branchInput" type="text" placeholder="feature/mobile-shell-test" />
          </label>
          <label class="field">
            <span>Base branch</span>
            <input id="baseBranchInput" type="text" value="main" />
          </label>
          <label class="field">
            <span>Visibilidade desejada</span>
            <select id="visibilityInput">
              <option value="private" selected>private</option>
              <option value="public">public</option>
            </select>
          </label>
          <label class="field">
            <span>Ciclo de visibilidade</span>
            <select id="lifecycleInput">
              <option value="public_until_product_ready" selected>public_until_product_ready</option>
              <option value="private_only">private_only</option>
              <option value="public_only">public_only</option>
            </select>
          </label>
          <label class="field">
            <span>Estratégia de build</span>
            <select id="buildStrategyInput">
              <option value="github_actions_free_public" selected>github_actions_free_public</option>
              <option value="standard">standard</option>
            </select>
          </label>
          <label class="field checkbox-field">
            <span>Produto pronto</span>
            <input id="productReadyInput" type="checkbox" />
          </label>
        </div>

        <label class="field">
          <span>Contexto de repos relacionadas</span>
          <textarea id="relatedReposInput" rows="4" placeholder="AndreVazao/baribudos-studio&#10;AndreVazao/baribudos-studio-website"></textarea>
        </label>

        <div class="action-row">
          <button id="executionBtn" class="primary-btn">Gerar execution pipeline</button>
          <button id="mobileCockpitBtn" class="secondary-btn">Gerar mobile cockpit</button>
        </div>
      </section>

      <section class="panel cockpit-panel">
        <div class="panel-title-row">
          <h2>Cockpit</h2>
          <span id="decisionBadge" class="badge badge-neutral">Sem decisão</span>
        </div>

        <div id="headlineCard" class="headline-card">
          <div class="headline-label">Próximo passo</div>
          <div id="headlineText" class="headline-text">Ainda sem resposta.</div>
        </div>

        <div id="compactCards" class="compact-cards"></div>

        <div class="action-buttons">
          <button class="decision-btn decision-ok">OK</button>
          <button class="decision-btn decision-change">ALTERA</button>
          <button class="decision-btn decision-reject">REJEITA</button>
        </div>
      </section>

      <section class="panel outputs-panel">
        <div class="panel-title-row">
          <h2>JSON</h2>
          <span class="badge badge-info">debug</span>
        </div>
        <div class="stacked-outputs">
          <div>
            <h3>Execution pipeline</h3>
            <pre id="executionOutput" class="output-box"></pre>
          </div>
          <div>
            <h3>Mobile cockpit</h3>
            <pre id="cockpitOutput" class="output-box"></pre>
          </div>
        </div>
      </section>
    </div>

    <script src="./app.js"></script>
  </body>
</html>
```

## Próxima ação nesta nova branch
- adaptar o `frontend/mobile-shell/index.html` atual para incorporar este layout e os modos `driving` e `assisted`
- manter branch curta e PR limpa
