# Conversation Provider Linkage Phase Plan

## Branch
- `feature/conversation-provider-linkage`

## Objetivo
Adicionar uma camada de ligação a provedores de conversa para o God Mode conseguir preparar o arranque real de novas conversas com a IA pedida pelo utilizador, organizar o contexto de origem e alinhar conversa, projeto e repo sem pesar o APK.

## Meta funcional
- representar providers de conversa suportados
- representar ações de arranque por provider
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de ligação
- preparar a fase seguinte de criação e organização real de conversas

## Blocos desta fase
### 1. Conversation provider linkage contract
Representar:
- conversation_provider_linkage_id
- provider_name
- provider_scope
- linkage_mode
- linkage_status

### 2. Conversation provider action contract
Representar:
- conversation_provider_action_id
- provider_name
- action_type
- action_label
- target_mode
- action_status

### 3. Services and routes
Criar backend para:
- devolver providers de conversa
- devolver ações por provider
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O APK continua a só pedir, mostrar e confirmar. O PC trata da ligação ao provider, do nome do projeto e da organização conversa -> projeto -> repo.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
