# Daily Command Router

## Objetivo

Transformar botões e comandos rápidos da Home em ações seguras por `command_id`.

O operador não precisa decorar comandos técnicos. O APK/Home pode chamar um ID estável e o backend encaminha para o fluxo certo.

## API

- `GET /api/daily-command-router/status`
- `GET /api/daily-command-router/package`
- `GET /api/daily-command-router/commands`
- `POST /api/daily-command-router/route`

## Payload

```json
{
  "command_id": "continue_active_project",
  "tenant_id": "owner-andre",
  "requested_project": "GOD_MODE"
}
```

## Comandos suportados

- `continue_active_project`
- `fix_blockers`
- `prepare_install`
- `summarize_next`
- `show_health`
- `show_artifacts`

## Integração com Modo Fácil

O painel `/api/home-operator-ux/panel` passa a expor:

- `daily_command_route_endpoint=/api/daily-command-router/route`;
- comandos rápidos com `route_endpoint`;
- ação principal baseada no router diário.

## Segurança

- Não contorna aprovações.
- Não altera prioridades.
- Usa o projeto ativo do operador quando nenhum projeto é enviado.
- Não pede tokens, passwords, cookies ou API keys.

## Uso esperado

1. Abrir `/app/home`.
2. Carregar em `Modo fácil`.
3. Escolher comando rápido.
4. Home chama `/api/daily-command-router/route` com `command_id`.
5. Backend encaminha para chat real, guia de instalação, saúde ou artifacts.
