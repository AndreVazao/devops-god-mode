# Project Recovery Local Apply Plan

## Branch
- `feature/recovery-write`

## Objetivo
Ligar a execução assistida da recuperação à camada local e preparar a recuperação para a fase seguinte de escrita real, para o God Mode saber que bundles e targets já estão prontos para seguir para aplicação local.

## Meta funcional
- representar bundle local aplicável
- representar targets locais por projeto
- expor pacote de aplicação local
- expor pacote write-ready
- expor próxima ação local e próxima ação write-ready
- preparar a fase seguinte de escrita/aplicação real

## Blocos desta fase
### 1. Recovery local apply bundle contract
Representar:
- local_apply_bundle_id
- recovery_project_id
- target_root
- local_target_count
- apply_mode
- apply_status
- write_ready_bundle_id
- write_target_count
- write_status

### 2. Recovery local target contract
Representar:
- local_target_id
- recovery_project_id
- local_target_path
- source_target_file_id
- local_role
- local_status
- content_strategy
- write_target_status

### 3. Services and routes
Criar backend para:
- devolver bundles locais aplicáveis
- devolver targets locais por projeto
- devolver pacote de aplicação local
- devolver pacote write-ready
- devolver próxima ação local
- devolver próxima ação write-ready

### 4. Scope
Nesta fase ainda não faz escrita automática no disco.
Fecha a ponte entre execução assistida de recovery e pacote pronto para seguir para a camada de escrita real.
