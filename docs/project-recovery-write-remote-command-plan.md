# Project Recovery Write Remote Command Bridge Plan

## Branch
- `feature/recovery-remote-command-bridge`

## Objetivo
Adicionar uma camada de comando remoto acima do approval cockpit, para o God Mode conseguir transformar itens mobile-ready em comandos simples de avançar, aprovar, adiar e priorizar diretamente a partir do telemóvel.

## Meta funcional
- representar sessões de comando remoto por projeto
- representar comandos acionáveis por target
- expor pacote de controlo remoto pronto para mobile cockpit
- expor próxima decisão remota prioritária
- preparar a fase seguinte de operação assistida ponta a ponta

## Blocos desta fase
### 1. Recovery write remote command contract
Representar:
- recovery_write_remote_command_id
- recovery_project_id
- commandable_item_count
- pending_command_count
- remote_status

### 2. Recovery write remote action contract
Representar:
- recovery_write_remote_action_id
- recovery_project_id
- recovery_write_approval_item_id
- command_type
- command_label
- command_status

### 3. Services and routes
Criar backend para:
- devolver sessões de comando remoto
- devolver ações remotas por projeto
- devolver pacote pronto para mobile cockpit
- devolver próxima ação remota prioritária

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
