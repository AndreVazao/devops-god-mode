# Offline Buffer Orchestrator Bridge

## Cockpit

- `/app/offline-command-buffering`
- `/app/offline-buffer`

## API adicionada/atualizada

- `GET /api/offline-command-buffering/status`
- `GET /api/offline-command-buffering/connectivity`
- `POST /api/offline-command-buffering/connectivity`
- `GET /api/offline-command-buffering/buffers`
- `GET /api/offline-command-buffering/commands`
- `POST /api/offline-command-buffering/commands`
- `POST /api/offline-command-buffering/sync`
- `POST /api/offline-command-buffering/replay`
- `POST /api/offline-command-buffering/sync-and-replay`
- `GET /api/offline-command-buffering/replays`
- `POST /api/offline-command-buffering/commands/{command_id}/execution`
- `GET /api/offline-command-buffering/actions`
- `GET /api/offline-command-buffering/package`
- `GET /api/offline-command-buffering/next-buffer-action`

## Objetivo

Fechar a lacuna crítica entre telefone offline e backend autónomo.

O operador pode dar uma ordem no telemóvel quando o PC está offline. Essa ordem fica guardada. Quando o PC volta, o buffer sincroniza e cria um job durável no Request Orchestrator. Depois o Request Worker Loop continua o job até concluir ou bloquear.

## Fluxo validado

1. Telefone envia comando enquanto PC está offline.
2. O comando fica com `sync_status = buffered_on_phone_until_pc_returns`.
3. PC volta online.
4. `/sync` transforma o comando em `ready_for_pc_execution`.
5. `/replay` envia o comando para o Request Orchestrator.
6. O comando passa a ter `orchestrator_job_id`.
7. O job continua com o Request Worker Loop.
8. Se precisar de OK, login manual ou input, fica bloqueado e o operador recebe cartão/aprovação.

## Mudança importante

O serviço `offline_command_buffering_service.py` deixa de escrever JSON manualmente e passa a usar `AtomicJsonStore`.

Isto reduz risco de corrupção em escrita concorrente/local e alinha o serviço com os requisitos de execução local-first.

## Segurança

O buffer bloqueia comandos que pareçam conter valores sensíveis. O operador não deve colocar passwords, tokens, cookies ou keys no chat/buffer.

## Integrações

- Request Orchestrator
- Request Worker Loop
- AtomicJsonStore
- Mobile/APK offline queue

## Porque esta fase era prioritária

As issues e docs definem que:

- PC é executor principal;
- telefone é cockpit;
- telefone pode ficar offline;
- PC deve continuar até terminar ou bloquear;
- ordens devem sobreviver a desconexões;
- escrita local deve ser robusta.

Esta fase liga essas peças num fluxo operacional real.
