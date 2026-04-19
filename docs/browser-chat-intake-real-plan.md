# Browser Chat Intake Real Plan

## Branch
- `feature/browser-chat-intake-real-v2`

## Objetivo
Dar o próximo salto ao God Mode: sair de intake genérico de snippets e passar para intake operacional de chats no browser, com plano de navegação, estado de captura, scroll progressivo e integração com organização de conversas.

## Meta funcional
- definir sessão de intake com foco operacional
- representar plano de navegação no chat
- representar progresso de scroll e captura
- priorizar sessões que alimentam organização, adaptação e reconstrução
- preparar a fase seguinte de browser control real

## Blocos desta fase
### 1. Intake session contract
Representar:
- session_id
- source_type
- source_url
- conversation_title
- project_hint
- intake_goal
- capture_status
- scroll_steps
- snippets_count
- code_blocks_count
- warnings

### 2. Navigation step contract
Representar:
- step_id
- session_id
- action_type
- target_hint
- step_status
- completion_note

### 3. Services and routes
Criar backend para:
- devolver sessões priorizadas de intake
- devolver plano de navegação por sessão
- devolver resumo de progresso de captura
- devolver próxima sessão mais útil para intake

### 4. Scope
Nesta fase ainda não controla browser real.
Fecha a camada operacional que vai orientar navegação e captura assistida nas próximas fases.
