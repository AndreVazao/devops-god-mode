# Project Recovery Execution Plan

## Branch
- `feature/project-recovery-execution`

## Objetivo
Dar o passo seguinte depois do blueprint de recuperação: preparar a execução assistida da recuperação de projeto, com bundle materializável, ficheiros alvo e próximo passo operacional.

## Meta funcional
- representar bundle de recuperação executável
- representar ficheiros alvo da repo reconstruída
- expor plano de materialização assistida
- expor próxima ação executável de recuperação
- preparar a fase seguinte de escrita real e aplicação local

## Blocos desta fase
### 1. Recovery execution bundle contract
Representar:
- execution_bundle_id
- recovery_project_id
- repo_name
- target_root
- file_count
- execution_status

### 2. Recovery target file contract
Representar:
- target_file_id
- recovery_project_id
- target_path
- file_role
- source_script_id
- target_status

### 3. Services and routes
Criar backend para:
- devolver bundles de execução de recuperação
- devolver ficheiros alvo por projeto
- devolver plano de materialização
- devolver próxima ação executável

### 4. Scope
Nesta fase ainda não escreve ficheiros reais no disco.
Fecha a camada de execução assistida da recuperação para depois ligar à escrita/aplicação local.
