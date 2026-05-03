# Real Orchestration Pipeline v1

## Objetivo

Ligar de forma real os módulos inteligentes do God Mode para criar uma fila de execução segura.

Esta é a primeira camada que deixa de ser apenas mapa/painel e começa a orquestrar módulos em cadeia.

## Pipeline

```txt
Pedido do André
→ Goal Planner
→ Agent Roles Registry
→ AI Handoff Security Guard
→ AI Provider Router
→ MCP Compatibility Map
→ Execution Gates
→ Safe Action Queue
```

## O que faz

Recebe um pedido e devolve:

- `pipeline_id`
- plano do objetivo;
- papéis internos atribuídos;
- pacote sanitizado de segurança;
- provider IA recomendado;
- fallback chain;
- validação das tools MCP;
- gates de execução;
- fila de ações seguras;
- passos prontos;
- passos bloqueados;
- resumo para operador.

## Endpoints

- `GET/POST /api/real-orchestration/status`
- `GET/POST /api/real-orchestration/panel`
- `GET/POST /api/real-orchestration/rules`
- `GET /api/real-orchestration/policy`
- `POST /api/real-orchestration/run`
- `POST /api/real-orchestration/simulate`
- `GET/POST /api/real-orchestration/package`

## Política de execução

Esta versão cria uma fila de execução segura, mas ainda não executa ações destrutivas.

### Auto-safe

Pode preparar:

- plano;
- classificação;
- atribuição de roles;
- security package;
- provider route;
- validação MCP;
- fila de execução;
- health/readiness checks.

### Requer confirmação

- commits reais;
- PRs com alterações persistentes;
- merge;
- release;
- sync técnico persistente;
- update de memória estável.

### Requer Oner explicitamente

- apagar ficheiros/repos;
- alterar credenciais;
- mexer em licenças/pagamentos;
- ações destrutivas;
- publicar artifacts finais automaticamente.

## Exemplo payload

```json
{
  "goal": "Corrigir o erro do EXE, validar /health e preparar PR",
  "project": "GOD_MODE",
  "repo": "AndreVazao/devops-god-mode",
  "context": "O build falhou no Windows runner.",
  "priority": "critical",
  "sensitive": false,
  "needs_code": true,
  "preferred_provider": "chatgpt",
  "execution_mode": "safe_queue",
  "operator_approved": false
}
```

## Resultado esperado

O God Mode passa a responder com uma fila como:

```txt
Q1 plano pronto
Q2 roles prontos
Q3 security package pronto/bloqueado
Q4 provider escolhido
Q5 reusable code search pronto
Q6 branch/PR requer aprovação
```

## Próxima evolução

- Persistir pipelines em SQLite/local DB.
- Criar executor de fila para tarefas low-risk.
- Ligar ao PC Autopilot Loop.
- Criar botão direto na Home/App para executar pipeline.
- Registar cada pipeline na memória AndreOS/GitHub.
- Transformar approved steps em ações reais de GitHub quando o Oner aprovar.
