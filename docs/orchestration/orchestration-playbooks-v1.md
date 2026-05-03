# Orchestration Playbooks v1

## Objetivo

Trazer o melhor de Praison e Ruflo para o God Mode sem dependência runtime externa.

Praison inspira os playbooks YAML/JSON, workflows e modos agentic.
Ruflo inspira goal planning, routing, swarms e tools.

## Pipeline

```txt
Playbook
→ validação
→ pipeline request
→ Real Orchestration Pipeline
→ safe action queue
```

## Endpoints

- `GET/POST /api/orchestration-playbooks/status`
- `GET/POST /api/orchestration-playbooks/panel`
- `GET/POST /api/orchestration-playbooks/rules`
- `GET /api/orchestration-playbooks/template`
- `POST /api/orchestration-playbooks/validate`
- `POST /api/orchestration-playbooks/to-pipeline`
- `POST /api/orchestration-playbooks/run`
- `GET/POST /api/orchestration-playbooks/package`

## Modos v1

- `sequential`
- `hierarchical`
- `workflow`
- `prompt_chain`
- `evaluator_optimizer`
- `parallel_safe`

Nesta fase, todos os modos produzem safe queue. Execução paralela real, manager/worker real e evaluator loop persistente ficam para fases futuras.

## Schema base

```json
{
  "version": "godmode.playbook.v1",
  "name": "godmode-safe-feature-flow",
  "description": "Playbook base para transformar um pedido em pipeline real segura.",
  "project": "GOD_MODE",
  "repo": "AndreVazao/devops-god-mode",
  "mode": "sequential",
  "priority": "normal",
  "sensitive": false,
  "needs_code": true,
  "needs_large_context": false,
  "needs_multimodal": false,
  "preferred_provider": "chatgpt",
  "operator_approved": false,
  "goals": [
    {
      "id": "goal_main",
      "goal": "Descrever aqui o objetivo principal.",
      "context": "Contexto técnico e operacional.",
      "constraints": ["não executar destrutivo sem aprovação", "validar build/testes"]
    }
  ],
  "gates": [
    "goal_planner",
    "agent_roles",
    "security_guard",
    "provider_router",
    "mcp_validation",
    "operator_approval_for_high_risk"
  ]
}
```

## Valor real

O God Mode passa a poder guardar workflows reutilizáveis para:

- bugfix e release;
- investigação de repos externos;
- criação de novas features;
- validação de APK/EXE;
- sync de memória;
- uso de providers IA;
- pipelines por projeto.

## Próximo passo

- Persistir playbooks em disco/DB.
- Criar templates por projeto.
- Ligar playbooks à Home/App.
- Criar executor low-risk para steps prontos.
