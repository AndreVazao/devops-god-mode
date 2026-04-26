# Mobile Start Config

## Config file

- `frontend/mobile-shell/apk-launch-config.json`

## Cockpit

- `/app/mobile-start-config`

## API

- `GET /api/mobile-start-config/status`
- `GET /api/mobile-start-config/package`
- `GET /api/mobile-start-config/config`
- `GET /api/mobile-start-config/validate`
- `GET /api/mobile-start-config/launch-plan`
- `GET /api/mobile-start-config/dashboard`

## Objetivo

Definir uma configuração versionada para o APK/mobile shell.

O APK deve abrir sempre:

- `/app/apk-start`

Depois o backend resolve a rota certa através do manifest/router.

## Regras principais

- Não hardcodar `/app/operator-chat-sync-cards` diretamente no APK.
- Usar `/app/apk-start` como entrada única.
- Preferir chat com cartões inline.
- Manter chat antigo como fallback.
- Mostrar botões de fallback quando houver erro.
- Não guardar valores sensíveis na configuração.

## WebView

A configuração declara:

- JavaScript ativo;
- DOM storage ativo;
- pull-to-refresh ativo;
- links externos fora do WebView;
- comportamento do botão voltar.

## Plano de arranque

`/api/mobile-start-config/launch-plan` combina:

- config versionada;
- APK manifest router;
- rota resolvida;
- fallback;
- home segura;
- botões seguros.

## Uso recomendado

No APK:

1. ler `frontend/mobile-shell/apk-launch-config.json` embutido no build;
2. abrir `default_entry_route`, atualmente `/app/apk-start`;
3. deixar o backend resolver a rota final;
4. se o backend falhar, usar última rota local ou `safe_home_route`.
