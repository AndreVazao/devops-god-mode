# Approved Work Queue Runner

## Objetivo

A Phase 113 transforma o plano de execução aprovado em fila operacional persistente.

Ela pega nas lanes da Phase 112 e cria itens de trabalho ordenados por prioridade do operador.

## Endpoints

- `GET/POST /api/approved-work-queue/status`
- `GET/POST /api/approved-work-queue/build`
- `GET/POST /api/approved-work-queue/current`
- `GET/POST /api/approved-work-queue/gates`
- `POST /api/approved-work-queue/run-safe`
- `GET/POST /api/approved-work-queue/package`

## Ligação à Home

A Home passa a expor:

- `Fila aprovada`
- `/api/approved-work-queue/build`

## O que faz

- Constrói fila a partir do plano aprovado.
- Persiste a fila em `data/approved_work_queue_runner.json`.
- Separa itens seguros de itens com aprovação obrigatória.
- Submete apenas passos seguros para o pipeline real.
- Chama o worker loop para processar lote seguro.
- Para em gates de aprovação.

## Ações seguras autoexecutáveis

- `read_inventory`
- `read_project_tree`
- `read_repo_metadata`
- `read_visible_chat_snapshot`
- `summarize_findings`
- `prepare_patch_preview`

## Ações bloqueadas até aprovação

- `external_ai_prompt_send`
- `conversation_rename`
- `repo_create`
- `project_file_write`
- `code_materialization`
- `build_trigger`
- `module_merge_or_delete`

## Segurança

`run-safe` só executa comandos com instruções explícitas:

- não escrever ficheiros;
- não criar repos;
- não enviar prompts externos;
- não renomear conversas;
- parar se precisar de aprovação.

## Próximo passo recomendado

Phase 114 deve criar um painel mobile/card visual para a fila aprovada:

- ver fila;
- executar próximos seguros;
- ver gates;
- aprovar/rejeitar ações perigosas;
- retomar após queda de ligação.
