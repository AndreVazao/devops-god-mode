# APK Launch Manifest

## Cockpit

- `/app/apk-launch`

## API

- `GET /api/apk-launch/status`
- `GET /api/apk-launch/package`
- `GET /api/apk-launch/manifest`
- `GET /api/apk-launch/health`
- `GET /api/apk-launch/dashboard`
- `POST /api/apk-launch/launch`

## Objetivo

Dar ao APK/mobile shell um ponto único de arranque.

Em vez do APK ter rotas hardcoded, ele pergunta ao backend:

> Qual é a superfície principal que devo abrir agora?

## Rota principal

A rota principal passa a ser:

- `/app/operator-chat-sync-cards`

Esta é a conversa corrida com cartões visuais clicáveis inline.

## Fallbacks

O manifest devolve também:

- fallback legacy: `/app/operator-chat-sync`;
- home: `/app/god-mode-home`;
- money: `/app/money-command-center`;
- approvals: `/app/mobile-approval-cockpit-v2`;
- offline safe: `/app/home`.

## Capacidades declaradas

O manifest informa o APK se o backend suporta:

- conversa contínua;
- cartões de ação inline;
- one-tap actions;
- mobile approvals;
- cache offline no sync chat;
- bloqueio de mensagens com aparência de segredo;
- approval obrigatório para ações destrutivas.

## Botões seguros

O manifest devolve botões seguros para o APK:

- Chat;
- Ganhar dinheiro;
- Aprovações;
- Home;
- Chat antigo.

## Health

`GET /api/apk-launch/health` verifica se os componentes principais respondem:

- God Mode Home;
- Chat Inline Card Renderer;
- Chat Action Cards;
- Mobile Approval Cockpit;
- Operator Chat Runtime Snapshot.

Se algum falhar, o health fica `yellow` e o APK pode abrir fallback.

## Segurança

Esta fase não executa comandos destrutivos e não guarda secrets.

O manifest só declara rotas, capacidades, snapshots e botões seguros.

## Uso recomendado no APK

No arranque:

1. chamar `/api/apk-launch/manifest`;
2. abrir `manifest.launch_policy.default_route`;
3. se falhar, abrir `manifest.launch_policy.fallback_route`;
4. se o backend estiver indisponível, abrir a última rota local em cache ou `/app/home`.
