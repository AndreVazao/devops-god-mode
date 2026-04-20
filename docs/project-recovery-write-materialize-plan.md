# Project Recovery Write Materialize Bridge Plan

## Branch
- `feature/recovery-materialize-bridge`

## Objetivo
Transformar o pipeline de recovery write num pacote operacional compatível com o executor local, para o God Mode conseguir sair da fase de planeamento e preparar pedidos concretos para `local_file_apply_runtime` e `real_local_write`.

## Meta funcional
- representar bridges de materialização entre recovery e executor local
- representar targets materializáveis por projeto
- expor pacote compatível com patch, preview, apply run e real write
- expor decisão de materialização pronta para execução
- preparar a fase seguinte de execução real controlada pelo cockpit remoto

## Blocos desta fase
### 1. Recovery write materialize bridge contract
Representar:
- recovery_write_materialize_id
- recovery_project_id
- handoff_id
- materialize_target_count
- executor_stack
- bridge_status

### 2. Recovery write materialize target contract
Representar:
- recovery_write_materialize_target_id
- recovery_project_id
- local_repo_path
- local_target_file
- patch_strategy
- risk_level
- target_status

### 3. Services and routes
Criar backend para:
- devolver bridges de materialização
- devolver targets materializáveis por projeto
- devolver pacote executor-ready com payloads compatíveis com `local_code_patch`, `patch_apply_preview`, `local_file_apply_runtime` e `real_local_write`
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
