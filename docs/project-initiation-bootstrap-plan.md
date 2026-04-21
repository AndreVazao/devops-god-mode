# Project Initiation Bootstrap Phase Plan

## Branch
- `feature/project-initiation-bootstrap`

## Objetivo
Adicionar uma camada de arranque de projeto para o God Mode conseguir iniciar novas conversas, organizar automaticamente o contexto, definir um nome de projeto consistente, renomear a conversa e preparar ou criar repo nova logo no arranque.

## Meta funcional
- representar sessões de iniciação de projeto
- representar passos de bootstrap conversa -> projeto -> repo
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de arranque
- preparar a fase seguinte de integração real com provedores de conversa

## Blocos desta fase
### 1. Project initiation bootstrap contract
Representar:
- project_initiation_id
- source_assistant
- proposed_project_name
- bootstrap_mode
- initiation_status

### 2. Project bootstrap step contract
Representar:
- project_bootstrap_step_id
- source_assistant
- step_type
- target_entity
- step_label
- step_status

### 3. Services and routes
Criar backend para:
- devolver sessões de iniciação
- devolver passos de bootstrap
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
No APK o fluxo deve continuar curto: pedir nova conversa/projeto, ver nome sugerido, confirmar, e deixar o PC organizar conversa, projeto e repo.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
