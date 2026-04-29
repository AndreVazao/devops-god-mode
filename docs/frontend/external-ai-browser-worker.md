# External AI Browser Worker

## Objetivo

A Phase 107 adiciona a primeira camada do worker de browser para sessões com IAs externas.

Esta fase não envia prompts nem recolhe respostas finais. Ela prepara a sessão de forma segura:

- deteta se Playwright está disponível;
- cria plano de sessão externo;
- pede login manual se necessário;
- cria checkpoints seguros;
- define probe permitido para o PC runner;
- impede armazenamento de credenciais;
- prepara retoma após falhas.

## Endpoints

- `GET/POST /api/external-ai-browser/status`
- `GET/POST /api/external-ai-browser/capability`
- `GET/POST /api/external-ai-browser/panel`
- `POST /api/external-ai-browser/prepare`
- `GET/POST /api/external-ai-browser/probe`
- `POST /api/external-ai-browser/confirm-login`
- `GET/POST /api/external-ai-browser/package`

## Ligação à Home

A Home passa a expor:

- `Browser IA`
- `/api/external-ai-browser/panel`

## Segurança

O worker define ações permitidas:

- abrir contexto browser não persistente;
- navegar para URL da IA;
- aguardar confirmação manual de login;
- detetar presença básica de input de chat;
- guardar checkpoint seguro.

E ações proibidas:

- ler campos de password;
- guardar cookies;
- guardar tokens;
- contornar login;
- enviar prompt sem gate de segurança.

## Login manual

Se o provedor exigir login, o worker chama o contrato da Phase 106:

- `/api/external-ai-session/login-popup`

O operador faz login manualmente e confirma com:

- `/api/external-ai-browser/confirm-login`

## Retoma

O worker grava checkpoints em passos como:

- `browser_worker_prepared`
- `request_manual_login_if_needed`
- `open_browser_or_service`
- `check_login_state`

Se houver falha de internet, browser ou backend, a retoma usa o contrato de sessão externa da Phase 106.

## Playwright opcional

Se Playwright não estiver instalado, o endpoint não rebenta. Ele devolve:

- `playwright_not_installed`
- instrução de preparação para o PC backend.

## Próximo passo

A próxima fase deve implementar a leitura segura de mensagens visíveis e o scroll do histórico, ainda sem envio automático de prompt sensível.
