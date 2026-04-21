# Autonomous Project Continuation Plan

## Branch
- `feature/autonomous-project-continuation`

## Objetivo
Adicionar uma camada de continuação autónoma de projeto para o God Mode conseguir pegar num projeto já escolhido, continuar o trabalho com pouca intervenção do utilizador e decidir a próxima ação útil até ao ponto de bloqueio real.

## Meta funcional
- representar sessões de continuação autónoma por projeto
- representar ações seguintes para continuar o projeto
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de continuação
- preparar a fase seguinte de rollover automático de conversa e handoff operacional entre providers

## Blocos desta fase
### 1. Autonomous continuation contract
Representar:
- autonomous_continuation_id
- target_project
- continuation_mode
- current_focus
- continuation_status

### 2. Continuation action contract
Representar:
- continuation_action_id
- target_project
- action_type
- action_reason
- requires_short_confirmation
- action_status

### 3. Services and routes
Criar backend para:
- devolver sessões de continuação autónoma
- devolver ações seguintes por projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve poder dizer para continuar um projeto e depois ver só o essencial: o foco atual, a próxima ação e se existe algum bloqueio real.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
