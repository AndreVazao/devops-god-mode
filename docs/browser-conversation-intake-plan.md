# Browser Conversation Intake Plan

## Branch
- `feature/browser-conversation-intake`

## Objetivo
Preparar a camada de intake no browser local para ler conversas antigas de IA, fazer scroll incremental e produzir material estruturado para a reconstrução de repo.

## Meta funcional
- representar uma sessão de intake no browser
- guardar origem, url, título e estado da conversa alvo
- guardar blocos capturados e trechos relevantes
- suportar scroll incremental por passos
- deixar tudo pronto para futura automação local no PC

## Blocos desta fase
### 1. Browser intake contract
Criar contrato para:
- session_id
- source_type
- source_url
- conversation_title
- capture_status
- scroll_steps
- snippets
- code_blocks
- warnings

### 2. Backend intake service
Guardar sessões de intake localmente com persistência simples.

### 3. Backend intake routes
Endpoints para:
- criar sessão
- listar sessões
- consultar sessão
- adicionar captura incremental

### 4. Mobile/cockpit visibility later
Esta fase prepara a base backend. A visibilidade no cockpit pode vir logo a seguir.

## Critérios de saída
- contrato de intake criado
- service backend criado
- routes backend criadas
- smoke verde da fase
