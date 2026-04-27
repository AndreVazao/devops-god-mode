# Ready To Use Home Check

## Objetivo

Mostrar na Home se o God Mode está pronto para uso prático.

Cenário alvo:

- abrir APK;
- encontrar PC;
- entrar em `/app/home`;
- enviar ordem pelo chat;
- backend criar trabalho real;
- PC Autopilot continuar com APK fechado;
- operador aprovar quando necessário;
- builds APK/EXE existirem.

## API

- `GET /api/ready-to-use/status`
- `GET /api/ready-to-use/package`
- `GET /api/ready-to-use/checklist`

## Integração com Home

A Home inclui `ready_to_use` no dashboard e status.

A Home também ganha ação rápida:

- `Pronto para usar` → `/api/ready-to-use/checklist`

## Checks

- APK cai na Home principal.
- Backend tem Home principal.
- Chat está ligado ao trabalho real.
- Prioridade do operador está ativa.
- PC Autopilot está instalado e seguro para APK desconectado.
- Aprovações estão acessíveis.
- Projeto Android existe.
- Workflow canónico de APK existe.
- Workflow canónico de EXE existe.

## Estados

- `ready`
- `almost_ready`
- `not_ready`

## Política

- `money_priority_enabled=false` continua a ser respeitado.
- O check não faz alterações por conta própria.
- O check não inicia autopilot sozinho.
- O check só mostra blockers e próxima ação.

## Valor para o operador

Em vez de procurar em vários cockpits, o operador vê na Home uma resposta simples:

- pronto;
- quase pronto;
- não pronto;
- próximo botão a carregar.
