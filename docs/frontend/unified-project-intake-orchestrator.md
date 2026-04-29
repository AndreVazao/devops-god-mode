# Unified Project Intake Orchestrator

## Objetivo

A Phase 110 cria o orquestrador canónico para o primeiro intake real do God Mode.

Esta fase não cria mais uma camada paralela. Ela reutiliza os serviços antigos e novos já existentes e define uma ordem única para:

1. inventariar conversas, repos e memória;
2. associar conversas a projetos;
3. agrupar projetos/repos relacionados;
4. preparar leitura/scroll de chats externos sem guardar credenciais;
5. detetar repos existentes e repos em falta;
6. gerar primeira auditoria superficial;
7. pedir prioridades ao operador;
8. só depois avançar para execução profunda.

## Endpoints

- `GET/POST /api/unified-project-intake/status`
- `GET/POST /api/unified-project-intake/plan`
- `GET/POST /api/unified-project-intake/run-safe`
- `GET/POST /api/unified-project-intake/package`

## Ligação à Home

A Home passa a expor:

- `Intake unificado`
- `/api/unified-project-intake/plan`

## Serviços reutilizados

A fase chama/reutiliza serviços existentes:

- `dedup_project_intake_audit_service`
- `initial_inventory_project_graph_service`
- `multi_ai_conversation_inventory_service`
- `conversation_organization_service`
- `conversation_provider_linkage_service`
- `conversation_repo_reconstruction_service`
- `conversation_repo_materialization_service`
- `external_ai_session_plan_service`
- `external_ai_browser_worker_service`
- `external_ai_chat_reader_service`
- `repo_relationship_graph_service`
- `project_tree_sync_guard_service`
- `operator_priority_service`

## Segurança

`run-safe` é não destrutivo:

- não renomeia conversas;
- não cria repos;
- não escreve ficheiros de projeto;
- não envia prompts para IAs externas;
- não guarda credenciais;
- não apaga módulos duplicados.

## Gates de aprovação

Exigem aprovação explícita:

- renomear conversas externas;
- criar repos em falta;
- materializar código a partir de conversa;
- enviar prompt para IA externa;
- fazer merge/delete de módulos antigos.

## Grupos conhecidos

### Baribudos Studio Ecosystem

Repos relacionados:

- `baribudos-studio`
- `baribudos-studio-website`

Tratamento:

- um projeto/ecossistema com múltiplos repos;
- `baribudos-studio` = studio/control-panel/content-creator;
- `baribudos-studio-website` = website/publishing-target.

### God Mode Core

Repo:

- `devops-god-mode`

Tratamento:

- sistema principal de orquestração.

## Próxima fase recomendada

Phase 111 deve ligar o resultado do `run-safe` ao fluxo de prioridades do operador, para permitir confirmar projetos principais, secundários, grupos e permissão para leitura/scroll de chats externos.
