# Project Recovery Write Queue Plan

## Branch
- `feature/recovery-queue`

## Objetivo
Levar os recovery write runs para uma fila preparada para a camada `real_local_write`, para o God Mode saber que operações já estão prontas para virar entradas de execução local.

## Meta funcional
- representar entradas de recovery write queue
- representar targets de queue por ficheiro
- expor pacote de queue preparado
- expor próxima ação desta fase
- preparar a fase seguinte de integração mais direta com a execução real local

## Blocos desta fase
### 1. Recovery write queue entry contract
Representar:
- recovery_write_queue_id
- recovery_project_id
- recovery_write_run_id
- queue_target_count
- queue_status

### 2. Recovery write queue target contract
Representar:
- recovery_write_queue_target_id
- recovery_project_id
- recovery_write_run_target_id
- queue_target_path
- queue_mode
- queue_target_status

### 3. Services and routes
Criar backend para:
- devolver entradas de queue
- devolver targets da queue
- devolver pacote de queue
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
