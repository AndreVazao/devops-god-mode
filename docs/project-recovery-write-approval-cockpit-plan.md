# Project Recovery Write Approval Cockpit Plan

## Branch
- `feature/recovery-approval-cockpit-bridge`

## Objetivo
Adicionar uma camada de cockpit de aprovação para a recovery write execution, para o God Mode conseguir expor no telemóvel o que está bloqueado, o que está pronto e qual a próxima decisão operacional.

## Meta funcional
- representar itens de cockpit por projeto
- representar approvals pendentes por target
- expor pacote mobile-ready para destravar a execução
- expor próxima ação prioritária
- preparar a fase seguinte de comando remoto assistido

## Blocos desta fase
### 1. Recovery write approval cockpit contract
Representar:
- recovery_write_approval_cockpit_id
- recovery_project_id
- pending_approval_count
- ready_target_count
- cockpit_status

### 2. Recovery write approval item contract
Representar:
- recovery_write_approval_item_id
- recovery_project_id
- recovery_write_execution_result_id
- required_response
- approval_status
- mobile_action_label

### 3. Services and routes
Criar backend para:
- devolver cockpits de aprovação
- devolver itens pendentes por projeto
- devolver pacote mobile-ready desta fase
- devolver próxima ação prioritária

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
