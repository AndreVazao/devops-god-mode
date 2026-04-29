# Browser Provider Execution Hub

## Objetivo

A Phase 131 consolida execução real browser/providers sem duplicar módulos existentes.

A árvore atual já contém vários módulos de browser, leitura de chats, sessões, guards e continuação. Esta fase cria um hub/orquestrador por cima deles.

## Endpoints

- `GET/POST /api/browser-provider-execution/status`
- `GET/POST /api/browser-provider-execution/panel`
- `GET/POST /api/browser-provider-execution/policy`
- `GET/POST /api/browser-provider-execution/modules`
- `POST /api/browser-provider-execution/plan`
- `POST /api/browser-provider-execution/session`
- `POST /api/browser-provider-execution/handoff`
- `GET/POST /api/browser-provider-execution/latest`
- `GET/POST /api/browser-provider-execution/package`

## Módulos reutilizados

- `external_ai_browser_worker`
- `external_ai_chat_reader`
- `external_ai_session_plan`
- `browser_control_real`
- `browser_conversation_intake`
- `browser_continuation_execution`
- `browser_response_reconciliation`
- `provider_real_execution_guard`
- `provider_session_partition`
- `operator_popup_delivery`
- `operator_resumable_action`

## Política

- Não guardar passwords, tokens, cookies ou API keys.
- Login manual feito pelo operador quando necessário.
- Reutilizar sessão browser depois do login.
- Continuar mesmo se o APK desligar.
- Parar apenas por login, OK, limite, recusa, bloqueio seguro, perda de sessão, net offline ou conclusão.

## Provider sequence

Ordem prevista:

1. ChatGPT
2. DeepSeek
3. Claude
4. Gemini
5. Google/Web
6. Local AI

A ordem pode ser alterada por preferência do operador.

## Resultado

Esta fase torna visível e orquestrado o caminho real:

Browser/session → login manual se necessário → ler/scrollar conversa → enviar prompt → capturar resposta → reconciliar → fallback provider → checkpoint/retoma.
