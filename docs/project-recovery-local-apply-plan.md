# Project Recovery Local Apply Plan

## Branch
- `feature/project-recovery-local-apply`

## Objetivo
Ligar a execução assistida da recuperação à camada local, para o God Mode preparar bundles prontos a aplicar localmente e aproximar a recuperação de uma repo materializada de verdade.

## Meta funcional
- representar bundle local aplicável
- representar targets locais por projeto
- expor pacote de aplicação local
- expor próxima ação local pronta a executar
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

### 2. Recovery local target contract
Representar:
- local_target_id
- recovery_project_id
- local_target_path
- source_target_file_id
- local_role
- local_status

### 3. Services and routes
Criar backend para:
- devolver bundles locais aplicáveis
- devolver targets locais por projeto
- devolver pacote de aplicação local
- devolver próxima ação local

### 4. Scope
Nesta fase ainda não faz escrita automática no disco.
Fecha a ponte entre execução assistida de recovery e aplicação local preparada.
