# Project Recovery Write Submit Plan

## Branch
- `feature/recovery-submit`

## Objetivo
Levar a recovery write queue para uma camada de submissão preparada para `real_local_write`, para o God Mode saber que operações já podem virar submissões locais reais.

## Meta funcional
- representar submissões de recovery write
- representar targets de submissão por ficheiro
- expor pacote de submissão
- expor próxima ação desta fase
- preparar a fase seguinte de integração mais direta com `real_local_write`

## Blocos desta fase
### 1. Recovery write submit contract
Representar:
- recovery_write_submit_id
- recovery_project_id
- recovery_write_queue_id
- submit_target_count
- submit_status

### 2. Recovery write submit target contract
Representar:
- recovery_write_submit_target_id
- recovery_project_id
- recovery_write_queue_target_id
- submit_target_path
- submit_mode
- submit_target_status

### 3. Services and routes
Criar backend para:
- devolver submissões preparadas
- devolver targets de submissão
- devolver pacote de submissão
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
