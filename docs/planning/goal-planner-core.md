# Goal Planner Core

## Objetivo

Criar o primeiro planeador nativo do God Mode para converter pedidos do André em planos executáveis.

Esta fase é inspirada nas ideias de goal planning / orchestration estudadas no Ruflo Research Lab, mas não depende do Ruflo em runtime.

## O que o Goal Planner faz

Recebe um objetivo e devolve:

- `goal_id`
- projeto inferido;
- repo inferido;
- classificação;
- plano de memória;
- pesquisa obrigatória de código reutilizável quando aplicável;
- tarefas estruturadas;
- riscos;
- blockers;
- plano de validação;
- próximo passo seguro;
- resumo para operador.

## Endpoints

- `GET/POST /api/goal-planner/status`
- `GET/POST /api/goal-planner/panel`
- `GET/POST /api/goal-planner/rules`
- `GET /api/goal-planner/template`
- `GET /api/goal-planner/policy`
- `POST /api/goal-planner/plan`
- `GET/POST /api/goal-planner/package`

## Home

Novo botão:

- `Goal Planner`

Novo comando rápido:

- `open_goal_planner`

## Exemplo de payload

```json
{
  "goal": "Corrigir o build do EXE e validar no Windows",
  "project": "GOD_MODE",
  "repo": "AndreVazao/devops-god-mode",
  "context": "O EXE compila mas precisa passar /health no runner.",
  "priority": "critical",
  "execution_mode": "safe_autopilot",
  "constraints": ["não apagar dados", "validar smoke test"]
}
```

## Regras

- Todo objetivo longo deve virar plano antes de execução.
- Antes de pedir código novo a IA, pesquisar Reusable Code Registry.
- Antes de mexer em repo, confirmar branch/PR alvo.
- Antes de enviar contexto a IA externa, filtrar segredos e usar AI Handoff Trace.
- Ações destrutivas exigem confirmação explícita do Oner.

## Próximas evoluções

- Persistir histórico de planos.
- Ligar planos diretamente ao PC Autopilot Loop.
- Criar agent role assignment.
- Criar Goal Planner UI com estado e botões de execução.
- Ligar ao AI Handoff Security Guard.
