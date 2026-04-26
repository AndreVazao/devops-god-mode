# Request Worker Loop

## Cockpit

- `/app/request-worker`

## API

- `GET /api/request-worker/status`
- `GET /api/request-worker/package`
- `GET /api/request-worker/dashboard`
- `POST /api/request-worker/configure`
- `POST /api/request-worker/tick`
- `POST /api/request-worker/run`

## Objetivo

Dar ao backend um ciclo explícito para processar jobs pendentes do Request Orchestrator, mesmo quando o APK está desligado.

A Phase 61 criou jobs duráveis. A Phase 62 cria um worker controlado por ticks.

## Como funciona

- `tick`: procura jobs `queued` ou `running` e chama o orquestrador até cada job concluir ou bloquear.
- `run`: executa vários ticks seguidos, com limite por tick.
- `configure`: ativa/desativa o worker e ajusta `max_jobs_per_tick`.

## Estados processados

O worker processa:

- `queued`
- `running`

O worker não força jobs bloqueados. Jobs em estado `blocked_approval`, `blocked_credentials` ou `blocked_manual_input` aguardam ação do operador.

## Segurança

Esta fase não cria execução livre. O worker apenas chama `request_orchestrator_service.run_until_blocked`, que respeita aprovações e bloqueios manuais.

## Uso recomendado

No backend local/PC:

1. O chat cria jobs com `/api/request-orchestrator/submit` ou `/api/chat-inline-card-renderer/send-orchestrated`.
2. O worker processa com `/api/request-worker/tick` ou `/api/request-worker/run`.
3. Se o job bloquear, o operador recebe cartão no chat e no Mobile Approval Cockpit.
4. Depois do OK/input manual, o job é retomado e o worker pode continuar.

## Próximo passo futuro

Numa fase futura, este worker pode ser chamado automaticamente por um startup hook, watchdog local ou agendador simples. Esta fase mantém o ciclo explícito para ser seguro e validável.
