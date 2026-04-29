# External AI Chat Reader + Scroll Plan

## Objetivo

A Phase 108 prepara a leitura segura de mensagens visíveis e o scroll do histórico em chats externos de IAs.

Esta fase não envia prompts automaticamente. Ela define o contrato para o PC runner ler e fazer scroll com checkpoints.

## Endpoints

- `GET/POST /api/external-ai-chat-reader/status`
- `GET/POST /api/external-ai-chat-reader/capability`
- `GET/POST /api/external-ai-chat-reader/panel`
- `GET/POST /api/external-ai-chat-reader/reader-plan`
- `GET/POST /api/external-ai-chat-reader/scroll-plan`
- `GET/POST /api/external-ai-chat-reader/runtime-instructions`
- `POST /api/external-ai-chat-reader/normalize-snapshot`
- `GET/POST /api/external-ai-chat-reader/package`

## Ligação à Home

A Home passa a expor:

- `Ler chat IA`
- `/api/external-ai-chat-reader/panel`

## O que a fase cobre

- selectors/hints por provedor;
- plano de leitura de mensagens visíveis;
- plano de scroll de histórico;
- instruções para PC runner;
- normalização de snapshot;
- deduplicação de mensagens;
- checkpoints seguros;
- retoma após falha de internet/browser/backend.

## Provedores com hints iniciais

- ChatGPT
- Claude
- Gemini
- Perplexity

## Ações permitidas ao PC runner

- consultar texto visível;
- consultar candidatos a mensagem;
- fazer scroll do container;
- aguardar mensagens visíveis;
- devolver snapshot.

## Ações bloqueadas nesta fase

- preencher input de prompt;
- pressionar Enter para enviar;
- ler campos de password;
- exportar cookies;
- exportar tokens;
- contornar login.

## Retoma

O plano de scroll define regras:

- antes do scroll: voltar ao último snapshot visível;
- durante o scroll: reabrir conversa e reler antes de repetir;
- depois do scroll: comparar snapshots antes de continuar.

## Próximo passo

A próxima fase deve implementar o `External AI Prompt Safety Gate`, para analisar o que pode ou não ser enviado para uma IA externa antes de permitir prompt automático.
