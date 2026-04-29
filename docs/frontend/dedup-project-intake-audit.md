# Dedup Project Intake Audit

## Objetivo

A Phase 109 audita o risco de serviços duplicados entre fundações antigas e as fases recentes 105-108.

A conclusão é clara: já existiam módulos antigos para intake de conversas, browser control, organização de conversas, inventário multi-IA, popup e retoma. As fases recentes adicionaram uma camada mais segura e específica para sessões externas de IA, mas há overlap que precisa unificação.

## Endpoints

- `GET/POST /api/dedup-project-intake-audit/status`
- `GET/POST /api/dedup-project-intake-audit/audit`
- `GET/POST /api/dedup-project-intake-audit/package`

## Ligação à Home

A Home passa a expor:

- `Auditar duplicados`
- `/api/dedup-project-intake-audit/audit`

## Overlap identificado

### Browser/conversa

Antigo:

- `browser_conversation_intake_service.py`
- `browser_control_real_service.py`

Novo:

- `external_ai_browser_worker_service.py`
- `external_ai_chat_reader_service.py`

Decisão: reutilizar os antigos como fundação/compatibilidade e usar os novos como contrato seguro por provider.

### Inventário e organização

Antigo:

- `multi_ai_conversation_inventory_service.py`
- `conversation_organization_service.py`
- `initial_inventory_project_graph_service.py`

Decisão: estes são a base canónica para inventário, agrupamento e mapa de projetos.

### Provider/session/popup/resume

Antigo:

- `conversation_provider_linkage_service.py`
- `operator_popup_delivery_service.py`
- `operator_resumable_action_service.py`

Novo:

- `external_ai_session_plan_service.py`

Decisão: o novo serviço deve chamar/reutilizar os antigos em vez de substituir tudo.

### Reconstrução de repos

Antigo/canónico:

- `conversation_repo_reconstruction_service.py`
- `conversation_repo_materialization_service.py`

Decisão: manter como base para transformar conversas em propostas de repo/materialização.

## Decisão de segurança

- Não apagar nada agora.
- Não fazer limpeza destrutiva sem aprovação explícita.
- Unificar por adapters/orchestrator.
- Criar uma fase seguinte para `Unified Project Intake Orchestrator`.

## Contrato principal do God Mode

No primeiro arranque real no PC, o God Mode deve:

1. Inventariar fontes: conversas AI, GitHub repos, pastas locais.
2. Ler títulos/snippets e preparar leitura/scroll das conversas.
3. Associar conversas a projetos.
4. Detetar repos existentes e repos em falta.
5. Agrupar conversas e repos relacionados.
6. Gerar árvore inicial e auditoria superficial por projeto.
7. Enviar resumo ao operador.
8. Pedir prioridades ao operador.
9. Só depois executar correções, reconstruções, builds e materializações.

## Exemplo importante

`baribudos-studio-website` e `baribudos-studio` são repos separados, mas pertencem ao mesmo ecossistema/projeto:

- Studio/control-panel cria/controla conteúdo.
- Website publica/serve conteúdo.

O God Mode deve tratar isto como um projeto com múltiplos repos e papéis, não como dois projetos sem relação.

## Próximo passo

Criar `Unified Project Intake Orchestrator` que chame os serviços existentes, em vez de criar mais módulos paralelos.
