# Conversation Rollover And Provider Handoff Plan

## Branch
- `feature/convo-rollover-handoff`

## Objetivo
Adicionar uma camada de rollover automático de conversa e handoff operacional entre providers para o God Mode conseguir continuar projetos longos quando uma conversa degrada, bloqueia ou precisa de outro provider para concluir a próxima parte útil.

## Meta funcional
- representar sessões de rollover por projeto e provider
- representar handoffs operacionais para outro provider
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de rollover ou handoff
- preparar a fase seguinte de execução semi-automática em browser com prompts de continuação

## Blocos desta fase
### 1. Conversation rollover contract
Representar:
- conversation_rollover_id
- target_project
- source_provider
- rollover_reason
- prepared_prompt_mode
- rollover_status

### 2. Provider handoff operation contract
Representar:
- provider_handoff_operation_id
- target_project
- source_provider
- target_provider
- handoff_goal
- handoff_status

### 3. Services and routes
Criar backend para:
- devolver rollovers preparados
- devolver handoffs operacionais
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: conversa atual saturada ou bloqueada, próximo provider ou nova conversa preparada, e a ação curta para seguir em frente.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
