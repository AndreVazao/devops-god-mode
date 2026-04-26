# Chat Boot Briefing

## Cockpit

- `/app/chat-boot-briefing`

## API

- `GET /api/chat-boot-briefing/status`
- `GET /api/chat-boot-briefing/package`
- `GET /api/chat-boot-briefing/briefing`
- `POST /api/chat-boot-briefing/boot`
- `GET /api/chat-boot-briefing/dashboard`

## Objetivo

Fazer o chat do APK/mobile arrancar com uma mensagem útil em vez de começar vazio.

O briefing inicial mostra:

- estado mobile;
- rota recomendada;
- fallback;
- aprovações pendentes;
- melhor próximo projeto para dinheiro;
- cartões clicáveis para ações seguras.

## Cartões criados

Ao executar `/api/chat-boot-briefing/boot`, o serviço cria uma thread se necessário, escreve a mensagem inicial e cria cartões para:

- Entrar no God Mode;
- Criar próximo passo para dinheiro;
- Abrir aprovações.

## Segurança

Esta fase não executa ações destrutivas. Ela cria mensagem de briefing e cartões seguros já suportados pelo Chat Action Cards.

## Uso recomendado

No arranque do APK:

1. abrir `/app/apk-start`;
2. entrar no chat com cartões;
3. chamar `/api/chat-boot-briefing/boot` se a thread ainda não tiver briefing;
4. mostrar os cartões inline na conversa.

## Fallback

Se o briefing falhar, o APK continua a poder abrir:

- `/app/operator-chat-sync-cards`;
- `/app/operator-chat-sync`;
- `/app/home`.
