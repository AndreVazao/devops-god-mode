# Continuous Remote Execution Phase Plan

## Branch
- `feature/continuous-remote-execution`

## Objetivo
Adicionar uma camada de execução remota contínua para o God Mode conseguir manter um ciclo operacional entre APK e PC com pedidos curtos, confirmações rápidas e progressão contínua da tarefa sem quebrar o fluxo de trabalho.

## Meta funcional
- representar loops de execução remota contínua
- representar ações de avanço operacional por loop
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de execução contínua
- preparar a fase seguinte de operação remota assistida ponta a ponta

## Blocos desta fase
### 1. Continuous remote execution contract
Representar:
- continuous_remote_execution_id
- execution_loop_mode
- control_surface
- continuity_profile
- execution_status

### 2. Continuous execution action contract
Representar:
- continuous_execution_action_id
- execution_area
- action_type
- action_label
- loop_mode
- action_status

### 3. Services and routes
Criar backend para:
- devolver loops de execução contínua
- devolver ações de avanço operacional
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve conseguir continuar a dar ordens curtas e receber estado compacto sem sentir que cada passo recomeça do zero.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
