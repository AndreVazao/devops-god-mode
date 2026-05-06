# Provider Browser Proof Local Launcher + Capture Contract

## Objetivo

A Phase 197 prepara um contrato real para o PC abrir providers no browser local e capturar/importar respostas de forma segura.

Esta fase ainda não automatiza login, envio de prompts ou scraping. Ela cria o trilho operacional real: abrir provider, login manual se necessário, copiar resposta e importar para o Conversation Source Import Feed.

## Endpoint principal

```txt
/api/provider-browser-local-launcher/package
```

## Página visual

```txt
/app/provider-browser-local-launcher
/app/provider-launcher
```

## Endpoints

- `/api/provider-browser-local-launcher/status`
- `/api/provider-browser-local-launcher/policy`
- `/api/provider-browser-local-launcher/create-launch-contract`
- `/api/provider-browser-local-launcher/create-capture-contract`
- `/api/provider-browser-local-launcher/import-capture`
- `/api/provider-browser-local-launcher/create-attention-card`
- `/api/provider-browser-local-launcher/package-provider`
- `/api/provider-browser-local-launcher/dashboard`
- `/api/provider-browser-local-launcher/package`

## O que esta fase faz

- Cria contrato de abertura local de provider.
- Cria contrato de captura manual.
- Cria card de atenção para abrir provider/login manual/captura.
- Liga captura ao `/api/conversation-source-import-feed/import-text`.
- Usa URLs seguras conhecidas por provider.
- Mantém flag explícita `executes_browser_automation=false`.

## O que esta fase não faz

- Não guarda passwords.
- Não guarda tokens.
- Não guarda cookies.
- Não automatiza login.
- Não envia prompts automaticamente.
- Não faz scrape de chats privados.

## Regra de realidade

O contrato é real para operação local: o PC sabe que provider abrir, com que perfil/label, e para onde importar a captura. Automação real futura exige gates próprios.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 196 deve ser apagado. Fica só:

- `.github/workflows/phase197-provider-browser-local-launcher-smoke.yml`

Além dos workflows globais/builds.
