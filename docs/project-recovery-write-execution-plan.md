# Project Recovery Write Execution Bridge Plan

## Branch
- `feature/recovery-execution-bridge`

## Objetivo
Instanciar a ponte entre o pacote de materialização e o executor local, para o God Mode conseguir criar patches, previews, apply runs e pedidos de real write, classificando também bloqueios de aprovação quando existirem.

## Meta funcional
- representar sessões de execução por projeto
- instanciar pedidos compatíveis com a stack local
- registar resultados por target e por camada do executor
- expor bloqueios de aprovação e passos pendentes
- preparar a fase seguinte de cockpit remoto e operação ponta a ponta

## Blocos desta fase
### 1. Recovery write execution session contract
Representar:
- recovery_write_execution_id
- recovery_project_id
- recovery_write_materialize_id
- execution_target_count
- execution_status
- blocker_count

### 2. Recovery write execution result contract
Representar:
- recovery_write_execution_result_id
- recovery_project_id
- recovery_write_materialize_target_id
- patch_status
- preview_status
- apply_run_status
- real_write_status
- blocker_reason

### 3. Services and routes
Criar backend para:
- devolver sessões de execução
- devolver resultados por projeto
- instanciar uma sessão de recovery write bridge
- devolver próxima ação desta fase

### 4. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
