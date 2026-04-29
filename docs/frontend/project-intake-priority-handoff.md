# Project Intake Priority Handoff

## Objetivo

A Phase 111 liga o `Unified Project Intake Orchestrator` ao sistema real de prioridades do operador.

Depois do intake seguro, o God Mode deve pedir confirmação antes de avançar para execução profunda.

## Endpoints

- `GET/POST /api/project-intake-priority-handoff/status`
- `GET/POST /api/project-intake-priority-handoff/review`
- `GET/POST /api/project-intake-priority-handoff/current`
- `POST /api/project-intake-priority-handoff/confirm-suggested`
- `POST /api/project-intake-priority-handoff/confirm`
- `POST /api/project-intake-priority-handoff/defer`
- `GET/POST /api/project-intake-priority-handoff/package`

## Ligação à Home

A Home passa a expor:

- `Confirmar prioridades`
- `/api/project-intake-priority-handoff/review`

## O que faz

- Executa/reusa o intake seguro da Phase 110.
- Mostra uma ordem sugerida de projetos.
- Mostra grupos de repos relacionados.
- Pede confirmação do operador.
- Aplica a ordem usando `operator_priority_service.set_order`.
- Mantém estado em `data/project_intake_priority_handoff.json`.

## Segurança

Esta fase não faz ações destrutivas.

Não faz:

- renomear conversas;
- criar repos;
- escrever ficheiros de projeto;
- enviar prompts para IAs externas;
- guardar credenciais;
- apagar módulos duplicados.

## Decisões possíveis

### Confirmar ordem sugerida

Endpoint:

`POST /api/project-intake-priority-handoff/confirm-suggested`

Aplica a ordem sugerida pelo intake.

### Confirmar ordem personalizada

Endpoint:

`POST /api/project-intake-priority-handoff/confirm`

Payload principal:

```json
{
  "ordered_project_ids": ["GOD_MODE", "BARIBUDOS_STUDIO", "BARIBUDOS_STUDIO_WEBSITE"],
  "active_project": "GOD_MODE",
  "external_ai_scan_permission": "manual_login_only_no_prompt_send"
}
```

### Adiar

Endpoint:

`POST /api/project-intake-priority-handoff/defer`

Mantém execução profunda bloqueada.

## Regra principal

A prioridade vem do operador.

Receita/dinheiro não decide a ordem de trabalho.

## Próximo passo recomendado

Phase 112 deve criar o plano de execução profunda aprovado, usando as prioridades confirmadas, mas ainda com gates para:

- prompts externos;
- criação de repos;
- escrita de ficheiros;
- renomeação de conversas.
