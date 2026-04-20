# Project Recovery Write Runs Plan

## Branch
- `feature/recovery-runs`

## Objetivo
Transformar candidatos de escrita real em runs preparados para a camada `real_local_write`, para o God Mode saber que operações já estão prontas para entrar na fila de escrita local real.

## Meta funcional
- representar runs de recovery write
- representar targets preparados para run
- expor pacote de runs preparados
- expor próxima ação desta fase
- preparar a fase seguinte de integração ainda mais direta com a escrita local real

## Blocos desta fase
### 1. Recovery write run contract
Representar:
- recovery_write_run_id
- recovery_project_id
- write_candidate_id
- run_target_count
- run_status

### 2. Recovery write run target contract
Representar:
- recovery_write_run_target_id
- recovery_project_id
- write_candidate_target_id
- run_target_path
- run_mode
- run_target_status

### 3. Services and routes
Criar backend para:
- devolver runs preparados
- devolver targets preparados
- devolver pacote de runs
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
