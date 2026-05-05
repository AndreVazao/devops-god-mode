# Provider Browser Proof Execution Link + Login Attention Cards

## Objetivo

A Phase 192 liga o cockpit de broadcast a links seguros para abrir providers no browser local e cria cartões de atenção quando algum provider precisa de login.

Esta fase acelera o uso real do God Mode sem fingir automação que ainda não existe.

## Endpoint principal

```txt
/api/provider-browser-proof-link/package
```

## Endpoints

- `/api/provider-browser-proof-link/status`
- `/api/provider-browser-proof-link/policy`
- `/api/provider-browser-proof-link/build-links`
- `/api/provider-browser-proof-link/create-login-cards`
- `/api/provider-browser-proof-link/create-automation-gate`
- `/api/provider-browser-proof-link/dashboard`
- `/api/provider-browser-proof-link/package`

## O que esta fase faz

- Cria links seguros para providers do broadcast plan.
- Mostra instrução manual para abrir provider no PC/browser local.
- Cria cards `provider_login_request` no Mobile Approval Cockpit.
- Cria gate futuro para browser automation, mas não executa automação nesta fase.
- Liga a página `/app/provider-broadcast-cockpit` a links/login cards.

## O que esta fase não faz

- Não automatiza login.
- Não envia prompts automaticamente.
- Não lê passwords.
- Não guarda credenciais.
- Não guarda cookies/tokens.
- Não faz scrape de chats privados.

## Segurança

- Browser automation fica `false`.
- Manual open fica `true`.
- Qualquer automação real futura exige gate explícito.
- O Oner continua a fazer login manualmente.

## Providers conhecidos

- ChatGPT: `https://chatgpt.com/`
- Claude: `https://claude.ai/`
- Gemini: `https://gemini.google.com/`
- Perplexity: `https://www.perplexity.ai/`
- Copilot: `https://copilot.microsoft.com/`
- OpenRouter: `https://openrouter.ai/`
- Ollama local: `http://localhost:11434/`
- Local WebUI: `http://localhost:7860/`

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 191 deve ser apagado. Fica só:

- `.github/workflows/phase192-browser-proof-login-cards-smoke.yml`

Além dos workflows globais/builds.
