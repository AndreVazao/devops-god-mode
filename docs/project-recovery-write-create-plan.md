# Project Recovery Write Create Plan

## Branch
- `feature/recovery-create`

## Objetivo
Levar a recovery write submit para uma camada de criação preparada para `real_local_write`, para o God Mode saber que payloads já podem virar pedidos concretos de criação de escrita local real.

## Meta funcional
- representar pedidos de create de recovery write
- representar targets preparados para create
- expor pacote de create preparado
- expor próxima ação desta fase
- preparar a fase seguinte de integração mais direta com `real_local_write`

## Blocos desta fase
### 1. Recovery write create contract
Representar:
- recovery_write_create_id
- recovery_project_id
- recovery_write_submit_id
- create_target_count
- create_status

### 2. Recovery write create target contract
Representar:
- recovery_write_create_target_id
- recovery_project_id
- recovery_write_submit_target_id
- create_target_path
- create_mode
- create_target_status

### 3. Services and routes
Criar backend para:
- devolver pedidos de create preparados
- devolver targets de create
- devolver pacote de create
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
