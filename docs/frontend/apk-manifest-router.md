# APK Manifest Router

## Cockpit

- `/app/apk-start`
- `/app/start`

## API

- `GET /api/apk-router/status`
- `GET /api/apk-router/package`
- `GET /api/apk-router/resolve`
- `POST /api/apk-router/resolve`
- `GET /api/apk-router/dashboard`

## Objetivo

Transformar o APK Launch Manifest num arranque real.

O APK/mobile shell pode abrir sempre:

- `/app/apk-start`

Essa página pergunta ao backend qual rota deve abrir e redireciona automaticamente.

## Rota recomendada

Quando o backend está saudável e há suporte para cartões inline:

- `/app/operator-chat-sync-cards`

## Fallbacks

- legacy chat: `/app/operator-chat-sync`
- home segura: `/app/home`

## Preferências

O router aceita `prefer`:

- `auto`: escolhe a rota principal se disponível;
- `legacy`: força `/app/operator-chat-sync`;
- `home`: força `/app/god-mode-home` ou `/app/home`.

## Cache local

A página `/app/apk-start` guarda em `localStorage`:

- `godmode.apk.lastRoute`
- `godmode.apk.lastFallback`

Se o backend falhar, mostra a última rota conhecida e botões de fallback.

## Segurança

Esta fase não executa operações de sistema, não cria repositórios e não altera ficheiros fora do fluxo validado.

Ela apenas resolve rotas, mantém histórico local de resoluções e ajuda o APK a abrir a superfície certa.

## Uso recomendado no APK

No WebView/arranque do APK:

1. abrir `/app/apk-start`;
2. deixar o router chamar `/api/apk-router/resolve`;
3. se a resposta estiver ok, abrir a rota recomendada;
4. se falhar, usar última rota em cache ou `/app/home`.
