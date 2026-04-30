# AI Handoff Trace Ledger

## Objetivo

Garantir que toda passagem entre God Mode, ChatGPT/outros providers, repos e memória AndreOS mantém contexto e rastreabilidade.

O God Mode deve preparar o pedido para a IA com:

- `trace_id`;
- projeto;
- repo alvo;
- repo de memória AndreOS;
- ficheiros de memória relevantes;
- contexto compacto;
- tarefa concreta;
- regras de segurança;
- formato esperado de resposta.

Depois, quando a IA responder, o God Mode deve registar o resultado no ledger e associar a branch, PR, commit, artifact ou delta de memória.

## Endpoints

- `GET/POST /api/ai-handoff-trace/status`
- `GET/POST /api/ai-handoff-trace/panel`
- `GET/POST /api/ai-handoff-trace/policy`
- `POST /api/ai-handoff-trace/prepare`
- `POST /api/ai-handoff-trace/record-result`
- `GET /api/ai-handoff-trace/ledger`
- `GET /api/ai-handoff-trace/trace/{trace_id}`
- `GET /api/ai-handoff-trace/repo-hints/{project_id}`
- `GET/POST /api/ai-handoff-trace/package`

## Home / Modo Fácil

Foi adicionado o botão:

- `Handoff IA` → `/api/ai-handoff-trace/panel`

Foi adicionado o comando rápido:

- `open_ai_handoff_trace`

## Fluxo

1. Operador pede ajuda ou continuação de projeto.
2. God Mode identifica projeto.
3. God Mode consulta AndreOS Context Orchestrator.
4. God Mode prepara prompt com repo + memória + contexto + tarefa.
5. Prompt é enviado/colado no provider.
6. Resposta volta ao God Mode.
7. God Mode regista resultado no ledger.
8. God Mode valida/aplica via PR/checks.
9. God Mode prepara `MEMORY_DELTA` para memória AndreOS.

## Política

- O provider não é fonte final de verdade.
- O God Mode reconcilia com repo/código real.
- Nenhum dado sensível deve ir para o provider ou memória Markdown.
- Toda alteração deve ficar ligada a `trace_id`.
- Toda alteração real deve ter PR, commit, artifact, validação ou rollback associado.

## Resultado

O God Mode deixa de perder o fio entre chats, repos, memória e ações reais. Cada handoff fica rastreável e pode ser auditado depois.
