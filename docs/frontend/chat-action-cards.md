# Chat Action Cards

## Cockpit

- `/app/chat-action-cards`

## API

- `GET /api/chat-action-cards/status`
- `GET /api/chat-action-cards/package`
- `GET /api/chat-action-cards/dashboard`
- `GET /api/chat-action-cards/cards`
- `POST /api/chat-action-cards/create`
- `POST /api/chat-action-cards/from-home-chat`
- `POST /api/chat-action-cards/execute`
- `POST /api/chat-action-cards/dismiss`

## Objetivo

Levar botões e ações para dentro da conversa corrida do APK.

O operador deve conseguir trabalhar como no ChatGPT:

1. escreve uma mensagem;
2. o God Mode responde;
3. a resposta pode trazer cartões clicáveis;
4. o operador toca no cartão;
5. a ação segura é executada ou cria aprovação.

## Formato no chat

Cada cartão também é registado na thread como mensagem do assistant com marcador:

`[ACTION_CARD:<card_id>]`

O APK pode procurar este marcador e renderizar a mensagem como cartão visual.

## Ações permitidas

Apenas ações controladas são permitidas:

- `open_url`
- `one_tap_money`
- `one_tap_continue_god_mode`
- `one_tap_review_memory`
- `create_money_approval_card`
- `decide_mobile_approval`
- `acknowledge`

## Segurança

Esta fase não permite execução arbitrária, scripts livres, comandos shell, escrita de ficheiros fora dos serviços existentes nem criação automática de repos.

Ações sensíveis continuam a passar por Mobile Approval Cockpit ou por serviços já validados.

## Integração com God Mode Home

`POST /api/chat-action-cards/from-home-chat` usa o chat da God Mode Home para interpretar a mensagem e transformar as sugestões em cartões clicáveis.

Exemplos:

- “quero ganhar dinheiro” cria cartão para próximo passo de receita;
- “continua” cria cartão para continuar God Mode;
- “revê memória” cria cartão de revisão de memória;
- “aprovações” cria cartão para abrir aprovações.

## Contrato para APK

O dashboard devolve `apk_contract` com:

- `render_inline = true`
- `card_marker_prefix = [ACTION_CARD:`
- `click_endpoint = /api/chat-action-cards/execute`
- `dismiss_endpoint = /api/chat-action-cards/dismiss`

## Próximo passo futuro

Depois desta fase, o APK pode renderizar estes cartões nativamente em vez de só mostrar texto. Isso deve ser feito numa fase própria, focada no frontend mobile/APK.
