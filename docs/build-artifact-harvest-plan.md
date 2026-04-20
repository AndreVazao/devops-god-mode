# Build Artifact Harvest Bridge Plan

## Branch
- `feature/build-artifact-harvest-bridge`

## Objetivo
Adicionar uma camada para recolher artefactos finais dos workflows, descarregar o produto certo e normalizar o nome final do ficheiro, para o God Mode conseguir fechar o ciclo depois do build e deixar APK, EXE ou outros outputs prontos a usar.

## Meta funcional
- representar sessões de recolha de artefactos por projeto
- representar artefactos finais elegíveis para download
- expor pacote pronto para download e rename
- expor próxima recolha prioritária
- preparar a fase seguinte de entrega final e catálogo de builds

## Blocos desta fase
### 1. Build artifact harvest contract
Representar:
- build_artifact_harvest_id
- recovery_project_id
- artifact_candidate_count
- preferred_output_type
- harvest_status

### 2. Build artifact item contract
Representar:
- build_artifact_item_id
- recovery_project_id
- source_workflow
- artifact_name
- normalized_output_name
- artifact_status

### 3. Services and routes
Criar backend para:
- devolver sessões de recolha de artefactos
- devolver artefactos elegíveis por projeto
- devolver pacote pronto para download e rename
- devolver próxima recolha prioritária

### 4. UX note
O cockpit mobile deve continuar leve, intuitivo e com o mínimo de campos de preenchimento possível. Esta fase prepara outputs finais para o cockpit sem o tornar confuso.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
