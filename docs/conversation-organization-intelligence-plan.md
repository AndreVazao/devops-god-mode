# Conversation Organization Intelligence Plan

## Branch
- `feature/conversation-organization-intelligence`

## Objetivo
Dar o próximo salto ao God Mode: passar de inventário simples de conversas para organização inteligente, agrupamento por projeto, relação entre chats, deteção de continuação e priorização do que precisa de ação.

## Meta funcional
- definir grupos de conversas por projeto e tema
- representar relações entre conversas antigas, continuação e duplicados
- sinalizar quando uma conversa pede continuação, fusão ou só arquivo
- expor foco operacional seguinte para intake, adaptação e reconstrução
- preparar a fase seguinte de browser/chat intake real

## Blocos desta fase
### 1. Conversation group contract
Representar:
- group_id
- project_key
- primary_conversation_id
- conversation_ids
- group_summary
- code_density
- organization_status

### 2. Conversation relation contract
Representar:
- relation_id
- source_conversation_id
- target_conversation_id
- relation_type
- confidence_score
- relation_reason

### 3. Services and routes
Criar backend para:
- devolver grupos organizados de conversas
- devolver relações entre conversas
- devolver sinais de continuação, fusão e arquivo
- devolver foco operacional seguinte para o God Mode

### 4. Scope
Nesta fase ainda não controla browser nem faz scroll real.
Fecha a base lógica que vai orientar intake, reconstrução e adaptação assistida nas próximas fases.
