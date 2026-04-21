# Remote Session Persistence Phase Plan

## Branch
- `feature/remote-session-persistence`

## Objetivo
Adicionar uma camada de persistência de sessão remota para o God Mode conseguir manter contexto curto entre APK e PC, retomar rapidamente o estado da operação e continuar comandos sem obrigar o utilizador a recomeçar quando há interrupções.

## Meta funcional
- representar sessões remotas persistentes
- representar ações de retoma e continuação
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de persistência
- preparar a fase seguinte de execução remota contínua

## Blocos desta fase
### 1. Remote session persistence contract
Representar:
- remote_session_id
- session_scope
- continuity_mode
- state_profile
- session_status

### 2. Remote session action contract
Representar:
- remote_session_action_id
- session_area
- action_type
- action_label
- resume_mode
- action_status

### 3. Services and routes
Criar backend para:
- devolver sessões persistentes
- devolver ações de persistência
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve poder voltar ao APK e continuar quase de imediato. O PC preserva o estado útil e devolve ao APK apenas o essencial.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
