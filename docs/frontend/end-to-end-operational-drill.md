# End-to-End Operational Drill

## Cockpit

- `/app/e2e-operational-drill`
- `/app/operational-drill`

## API

- `GET /api/e2e-operational-drill/status`
- `GET /api/e2e-operational-drill/package`
- `GET /api/e2e-operational-drill/dashboard`
- `GET /api/e2e-operational-drill/latest-report`
- `POST /api/e2e-operational-drill/run`

## Objetivo

Provar o fluxo operacional completo antes de dizer que o God Mode está pronto para uso real.

O drill é não destrutivo. Ele simula uma ordem normal do operador e valida que o backend consegue transformar essa ordem num processo controlado.

## Fluxo validado

1. Criar thread de chat.
2. Escrever ordem do operador na thread.
3. Submeter ordem ao Request Orchestrator.
4. Criar job durável.
5. Correr Request Worker Loop.
6. Validar superfície de aprovações.
7. Se o job bloquear, retomar com resume simulado não destrutivo.
8. Validar offline bridge opcional.
9. Escrever relatório final na thread.
10. Criar card inline com o relatório.
11. Guardar relatório em `data/end_to_end_operational_drill.json`.

## Provas no relatório

O relatório contém flags de prova:

- `chat_thread_created`
- `job_created`
- `worker_tick_ran`
- `approval_surface_checked`
- `resume_checked`
- `offline_bridge_checked`
- `report_written_to_chat`

## Segurança

O drill não executa alterações destrutivas. Ele usa os serviços reais, mas com pedido seguro e resume não destrutivo.

## Uso recomendado

Antes de instalar ou entregar uma build:

1. abrir `/app/install-readiness`;
2. confirmar que não há blockers;
3. abrir `/app/e2e-operational-drill`;
4. correr o drill;
5. confirmar que o relatório fica green ou que os blockers são claros.
