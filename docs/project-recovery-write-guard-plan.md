# Project Recovery Write Guard Plan

## Branch
- `feature/recovery-guard`

## Objetivo
Adicionar uma camada de guard antes da criação real em `real_local_write`, para o God Mode conseguir detetar e classificar erros estruturais como sintaxe, indentação e payloads malformados antes de continuar.

## Meta funcional
- representar guards de recovery write
- representar findings por target
- expor pacote de guard
- expor próxima ação desta fase
- preparar a fase seguinte de criação real com mais segurança

## Blocos desta fase
### 1. Recovery write guard contract
Representar:
- recovery_write_guard_id
- recovery_project_id
- recovery_write_dispatch_id
- finding_count
- guard_status

### 2. Recovery write guard finding contract
Representar:
- recovery_write_guard_finding_id
- recovery_project_id
- recovery_write_dispatch_target_id
- finding_type
- severity
- finding_status

### 3. Services and routes
Criar backend para:
- devolver guards preparados
- devolver findings por target
- devolver pacote de guard
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
