# Pipeline Persistence + Low-Risk Executor v1

## Objetivo

Persistir pipelines/playbooks localmente e executar apenas passos low-risk seguros.

Esta fase transforma a Real Orchestration Pipeline de resposta temporária em histórico local consultável.

## O que entra

- Serviço: `backend/app/services/pipeline_persistence_executor_service.py`
- Rota: `backend/app/routes/pipeline_persistence_executor.py`

## Endpoints

- `GET/POST /api/pipeline-store/status`
- `GET/POST /api/pipeline-store/panel`
- `GET/POST /api/pipeline-store/rules`
- `POST /api/pipeline-store/save`
- `POST /api/pipeline-store/create-from-goal`
- `GET /api/pipeline-store/list`
- `GET /api/pipeline-store/load/{pipeline_id}`
- `POST /api/pipeline-store/execute-low-risk`
- `GET/POST /api/pipeline-store/package`

## Persistência

Por defeito usa:

```txt
~/.godmode/data/pipelines
```

Pode ser alterado com:

```txt
GODMODE_DATA_DIR
```

## Executor low-risk

Executa apenas passos locais/read-only/preparação:

- goal_planner;
- agent_roles;
- ai_provider_router;
- reusable_code_registry;
- mcp_compatibility;
- health_check.

## Bloqueios

Nunca executa nesta fase:

- commit;
- merge;
- release;
- delete;
- alteração de credenciais;
- envio real para IA externa;
- alteração persistente de repo/memória sem gate.

## Fluxo recomendado

```txt
create-from-goal
→ save pipeline
→ list/load
→ execute-low-risk dry_run=true
→ execute-low-risk dry_run=false
→ passos high ficam requires_approval
```

## Próxima evolução

- Ligar à Home/App.
- Persistir também playbooks.
- Ligar ao PC Autopilot Loop.
- Registar pipelines importantes na memória AndreOS/GitHub.
- Criar executor para ações GitHub com aprovação explícita.
