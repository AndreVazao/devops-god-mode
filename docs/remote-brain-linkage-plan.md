# Remote Brain Linkage Phase Plan

## Branch
- `feature/remote-brain-linkage`

## Objetivo
Adicionar uma camada de ligação entre o APK thin client e o cérebro no PC, para o God Mode conseguir receber voz/comandos no telemóvel, enviar para o backend do PC, interpretar intenção com contexto completo e devolver opções compactas para confirmação e execução.

## Meta funcional
- representar sessões de brain linkage por canal remoto
- representar intents remotas interpretadas pelo backend do PC
- expor pacote compacto para cockpit mobile
- expor próxima ação prioritária de interpretação remota
- preparar a fase seguinte de iniciação de projeto e conversa com IA

## Blocos desta fase
### 1. Remote brain linkage contract
Representar:
- remote_brain_linkage_id
- client_type
- backend_role
- voice_intent_mode
- linkage_status

### 2. Remote brain intent contract
Representar:
- remote_brain_intent_id
- source_channel
- interpreted_action
- probable_target_type
- confirmation_mode
- intent_status

### 3. Services and routes
Criar backend para:
- devolver sessões de brain linkage
- devolver intents interpretadas
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O APK deve continuar fino. Capta voz e mostra opções. O cérebro, o contexto distribuído e a decisão ficam no PC.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
