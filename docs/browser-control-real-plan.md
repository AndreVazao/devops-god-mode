# Browser Control Real Plan

## Branch
- `feature/browser-control-real`

## Objetivo
Dar o próximo salto ao God Mode: sair de planeamento de intake e passar para controlo operacional do browser, com ações assistidas de abrir chat, focar thread, scroll guiado e captura orientada por sessão.

## Meta funcional
- definir sessão de controlo do browser ligada ao intake
- representar ações de controlo reais e seguras
- expor próxima ação recomendada no browser
- refletir o estado de execução do controlo sobre a sessão de intake
- preparar a fase seguinte de cockpit mobile forte para comandar estas ações

## Blocos desta fase
### 1. Browser control session contract
Representar:
- control_id
- session_id
- control_mode
- target_url
- target_conversation_id
- control_status
- active_step_id
- pending_actions_count
- last_action_summary

### 2. Browser control action contract
Representar:
- action_id
- control_id
- action_type
- target_hint
- requires_confirmation
- action_status
- completion_note

### 3. Services and routes
Criar backend para:
- devolver sessões de controlo do browser
- devolver plano de ações por sessão
- devolver próxima ação recomendada
- marcar avanço assistido de uma ação
- sincronizar estado do controlo com a sessão de intake

### 4. Scope
Nesta fase ainda não injeta controlo em browser real nem faz automação invisível.
Fecha a camada lógica e operacional para o browser ser comandado de forma assistida nas próximas fases.
