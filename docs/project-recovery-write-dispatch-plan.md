# Project Recovery Write Dispatch Plan

## Branch
- `feature/recovery-dispatch`

## Objetivo
Levar a recovery write create para uma camada de dispatch preparada para `real_local_write`, para o God Mode saber que payloads já podem virar pedidos de despacho concretos para escrita local real.

## Meta funcional
- representar dispatches de recovery write
- representar targets preparados para dispatch
- expor pacote de dispatch preparado
- expor próxima ação desta fase
- preparar a fase seguinte de integração mais direta com `real_local_write`

## Blocos desta fase
### 1. Recovery write dispatch contract
Representar:
- recovery_write_dispatch_id
- recovery_project_id
- recovery_write_create_id
- dispatch_target_count
- dispatch_status

### 2. Recovery write dispatch target contract
Representar:
- recovery_write_dispatch_target_id
- recovery_project_id
- recovery_write_create_target_id
- dispatch_target_path
- dispatch_mode
- dispatch_target_status

### 3. Services and routes
Criar backend para:
- devolver dispatches preparados
- devolver targets de dispatch
- devolver pacote de dispatch
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
