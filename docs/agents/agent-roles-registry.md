# Agent Roles Registry

## Objetivo

Formalizar os papéis internos do God Mode para que tarefas complexas sejam atribuídas ao especialista certo.

Esta fase é inspirada em ideias de swarms/agent roles estudadas no Ruflo Research Lab, mas é implementada nativamente no God Mode.

## Papéis iniciais

- `architect`
- `builder`
- `tester`
- `security`
- `memory`
- `reusable_code`
- `github`
- `obsidian`
- `release`
- `mobile`
- `desktop`
- `ai_research`

## Endpoints

- `GET/POST /api/agent-roles/status`
- `GET/POST /api/agent-roles/panel`
- `GET/POST /api/agent-roles/rules`
- `GET /api/agent-roles/roles`
- `GET /api/agent-roles/roles/{role_id}`
- `POST /api/agent-roles/assign`
- `POST /api/agent-roles/execution-plan`
- `GET/POST /api/agent-roles/package`

## Home

Novo botão:

- `Papéis IA`

Novo comando rápido:

- `open_agent_roles`

## Regras

- O God Mode deve escolher papéis internos antes de executar trabalho complexo.
- Security entra sempre que houver IA externa, tokens, cookies, passwords, prompt injection ou ação destrutiva.
- Reusable Code entra antes de criar código novo.
- Tester entra antes de merge/release/artifact.
- Memory entra quando houver GitHub memory, Obsidian, AndreOS ou contexto persistente.
- Release entra quando houver APK, EXE, artifact, update ou instalador.

## Exemplo

Pedido:

```txt
Corrigir erro do EXE, validar /health no Windows e atualizar memória técnica.
```

Roles esperados:

- `tester`
- `builder`
- `github`
- `desktop`
- `memory`

## Estado

Nesta fase, os papéis ainda não são processos separados. São uma camada de decisão e routing interno para o Goal Planner e futuras automações.
