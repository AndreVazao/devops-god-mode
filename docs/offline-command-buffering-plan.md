# Offline Command Buffering Phase Plan

## Branch
- `feature/offline-command-buffering`

## Objetivo
Adicionar uma camada de buffering offline para o God Mode conseguir aceitar ordens no APK mesmo quando o PC está offline, e permitir ao PC continuar a trabalhar mesmo quando o telefone desaparece temporariamente.

## Meta funcional
- representar buffers offline por lado do sistema
- representar ações de enqueue, replay e continuação
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de buffering resiliente
- preparar a fase seguinte de inventário inicial e grafo de projeto

## Blocos desta fase
### 1. Offline command buffer contract
Representar:
- offline_command_buffer_id
- buffer_side
- buffer_scope
- replay_mode
- buffer_status

### 2. Offline buffer action contract
Representar:
- offline_buffer_action_id
- buffer_area
- action_type
- action_label
- recovery_mode
- action_status

### 3. Services and routes
Criar backend para:
- devolver buffers offline
- devolver ações de buffering e replay
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve poder falar agora e deixar processar depois. O PC deve continuar o trabalho atual mesmo sem novas ordens do telefone.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
