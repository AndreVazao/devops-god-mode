# Mobile First Run Wizard

## Cockpit

- `/app/mobile-first-run`
- `/app/first-run`

## API

- `GET /api/mobile-first-run/status`
- `GET /api/mobile-first-run/package`
- `GET /api/mobile-first-run/check`
- `GET /api/mobile-first-run/start`
- `GET /api/mobile-first-run/dashboard`

## Objetivo

Criar um primeiro ecrã simples para o APK/mobile validar se o God Mode está pronto.

O operador vê um semáforo e botões grandes:

- Entrar no God Mode;
- Testar de novo;
- Fallback;
- Home.

## Componentes testados

O wizard valida:

- mobile start config;
- launch plan;
- APK launch manifest;
- APK manifest router;
- chat inline renderer;
- operator chat runtime snapshot.

## Semáforo

- `green`: tudo pronto, abrir rota recomendada;
- `yellow`: pode abrir, mas manter fallback;
- `red`: usar fallback ou home segura.

## Rota recomendada

Quando tudo está pronto:

- `/app/operator-chat-sync-cards`

## Fallback

- `/app/operator-chat-sync`

## Home segura

- `/app/home`

## Uso recomendado

No APK, durante primeira configuração ou diagnóstico:

1. abrir `/app/mobile-first-run`;
2. carregar em “Testar de novo”;
3. se estiver green ou yellow, carregar em “Entrar no God Mode”;
4. se estiver red, usar fallback ou home.

## Segurança

Esta fase apenas executa leituras, validações e escolhas de rota. Não aplica alterações destrutivas.
