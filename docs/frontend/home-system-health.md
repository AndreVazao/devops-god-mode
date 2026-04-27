# Home System Health Snapshot

## Objetivo

Dar à Home um resumo único de saúde operacional.

Em vez de abrir vários cockpits, o operador vê numa só resposta:

- score de saúde;
- semáforo;
- blockers;
- próxima ação;
- estado dos subsistemas principais.

## API

- `GET /api/home-system-health/status`
- `GET /api/home-system-health/package`
- `GET /api/home-system-health/snapshot`

## Subsistemas avaliados

- Home.
- Ready To Use.
- Install First Run Guide.
- Artifacts Center.
- PC Autopilot.
- Chat ligado ao backend.
- Prioridade do operador.

## Estados

- `healthy`.
- `attention`.
- `blocked`.

## Integração com Home

A Home passa a incluir:

- `home_system_health` no dashboard/status;
- botão `Saúde`;
- modo condução com score de saúde;
- próxima ação baseada em blockers críticos.

## Política

- Não executa alterações por conta própria.
- Não altera prioridades.
- Não inicia autopilot sozinho.
- Só calcula estado, blockers e próxima ação.
