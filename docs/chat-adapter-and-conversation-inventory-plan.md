# Chat Adapter And Conversation Inventory Plan

## Branch
- `feature/chat-adapter-and-conversation-inventory`

## Objetivo
Preparar a camada que vai permitir ao God Mode inventariar conversas, classificá-las por projeto, manter aliases internos, extrair blocos de código e começar a reutilizar conhecimento operacional sem depender sempre de abrir chats manualmente.

## Meta funcional
- definir adapter de frontend de chat
- definir inventário de conversas
- classificar conversas por projeto e tags
- manter aliases internos para nomes mais limpos
- preparar extração de scripts e reaproveitamento futuro

## Blocos desta fase
### 1. Chat adapter contract
Representar:
- adapter_id
- platform
- mode
- inventory_capable
- extraction_capable
- rename_mode
- adapter_status

### 2. Conversation inventory contract
Representar:
- conversation_id
- platform
- title
- alias
- project_key
- tags
- contains_code
- inventory_status

### 3. Services and routes
Criar backend para:
- devolver adapters disponíveis
- devolver inventário de conversas
- devolver aliases e classificação
- devolver candidatos a reaproveitamento

### 4. Scope
Nesta fase ainda não fecha automação real do browser.
Fecha a base lógica para inventário, classificação e reaproveitamento futuro.
