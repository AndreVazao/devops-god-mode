# Chat Inline Card Renderer

## Cockpit

- `/app/operator-chat-sync-cards`
- `/app/chat-inline-cards`

## API

- `GET /api/chat-inline-card-renderer/status`
- `GET /api/chat-inline-card-renderer/package`
- `GET /api/chat-inline-card-renderer/dashboard`
- `GET /api/chat-inline-card-renderer/manifest`
- `POST /api/chat-inline-card-renderer/open-session`
- `POST /api/chat-inline-card-renderer/send`

## Objetivo

Renderizar visualmente os Chat Action Cards dentro da conversa corrida, com botões clicáveis.

A Phase 54 criou os cartões e o marcador `[ACTION_CARD:<card_id>]`. A Phase 55 cria uma superfície dedicada para o APK/mobile onde esses cartões são mostrados como blocos visuais, com botões de executar e ignorar.

## Fluxo

1. O operador escreve uma mensagem normal, como no ChatGPT.
2. `/api/chat-inline-card-renderer/send` envia a mensagem para o God Mode Home chat.
3. As sugestões são convertidas em cartões por `chat_action_cards_service`.
4. O frontend renderiza os cartões inline.
5. O operador carrega no botão do cartão.
6. O cartão executa através de `/api/chat-action-cards/execute`.
7. O cartão pode ser ignorado através de `/api/chat-action-cards/dismiss`.

## Segurança

Esta fase não adiciona shell, scripts livres, escrita arbitrária nem automação destrutiva.

A execução continua limitada às ações permitidas na Phase 54:

- `open_url`
- `one_tap_money`
- `one_tap_continue_god_mode`
- `one_tap_review_memory`
- `create_money_approval_card`
- `decide_mobile_approval`
- `acknowledge`

## Contrato APK

O endpoint `/api/chat-inline-card-renderer/manifest` devolve:

- rota principal: `/app/operator-chat-sync-cards`;
- alias: `/app/chat-inline-cards`;
- rota legacy: `/app/operator-chat-sync`;
- endpoints de executar/ignorar/listar cartões;
- `render_inline = true`;
- `message_mode = continuous_chat_like_chatgpt`.

## Uso recomendado

No APK, usar `/app/operator-chat-sync-cards` como próxima superfície preferida para conversas corridas com ações clicáveis.

A rota antiga `/app/operator-chat-sync` continua intacta como fallback.
