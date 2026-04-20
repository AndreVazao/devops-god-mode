# Project Recovery Write Mobile Action Execution Bridge Plan

## Branch
- `feature/recovery-mobile-action-execution-bridge`

## Objetivo
Adicionar uma camada de execução de ações mobile acima do remote command, para o God Mode conseguir representar o efeito operacional de comandos remotos no fluxo de recovery write e preparar a operação assistida ponta a ponta a partir do telemóvel.

## Meta funcional
- representar sessões de execução mobile por projeto
- representar efeitos de execução por ação remota
- expor pacote de execução mobile pronto para cockpit
- expor próxima execução mobile prioritária
- preparar a fase seguinte de comando assistido ponta a ponta

## Blocos desta fase
### 1. Recovery write mobile execution contract
Representar:
- recovery_write_mobile_execution_id
- recovery_project_id
- executable_action_count
- executed_action_count
- mobile_execution_status

### 2. Recovery write mobile effect contract
Representar:
- recovery_write_mobile_effect_id
- recovery_project_id
- recovery_write_remote_action_id
- execution_effect
- downstream_status
- effect_status

### 3. Services and routes
Criar backend para:
- devolver sessões de execução mobile
- devolver efeitos por projeto
- devolver pacote pronto para mobile cockpit
- devolver próxima execução mobile prioritária

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
