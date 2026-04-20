# Project Recovery Write Candidates Plan

## Branch
- `feature/recovery-next`

## Objetivo
Preparar candidatos de escrita real a partir dos handoffs de recovery, para o God Mode saber que projetos e targets já podem seguir para runs compatíveis com a camada `real_local_write`.

## Meta funcional
- representar candidatos de escrita por projeto
- representar targets candidatos por ficheiro
- expor pacote de candidatos de escrita real
- expor próxima ação desta fase
- preparar a fase seguinte de ligação ainda mais direta à execução local real

## Blocos desta fase
### 1. Recovery write candidate contract
Representar:
- write_candidate_id
- recovery_project_id
- handoff_id
- candidate_target_count
- candidate_status

### 2. Recovery write candidate target contract
Representar:
- write_candidate_target_id
- recovery_project_id
- handoff_target_id
- target_path
- candidate_mode
- candidate_target_status

### 3. Services and routes
Criar backend para:
- devolver candidatos de escrita real
- devolver targets candidatos
- devolver pacote de candidatos
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
