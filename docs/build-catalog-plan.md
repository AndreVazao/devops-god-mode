# Build Catalog Phase Plan

## Branch
- `feature/build-catalog`

## Objetivo
Adicionar uma camada de catálogo final de builds, para o God Mode conseguir listar outputs concluídos de forma leve no cockpit, destacar o ficheiro principal e expor ações simples de download e entrega sem confundir a interface mobile.

## Meta funcional
- representar catálogos de build por projeto
- representar entradas finais de output por tipo
- expor pacote leve para cockpit mobile
- expor próximo output prioritário
- preparar a fase seguinte de entrega final assistida

## Blocos desta fase
### 1. Build catalog contract
Representar:
- build_catalog_id
- recovery_project_id
- output_count
- primary_output_name
- catalog_status

### 2. Build output entry contract
Representar:
- build_output_entry_id
- recovery_project_id
- output_type
- display_name
- source_artifact_name
- delivery_status

### 3. Services and routes
Criar backend para:
- devolver catálogos de builds
- devolver outputs por projeto
- devolver pacote leve pronto para cockpit
- devolver próximo output prioritário

### 4. UX note
O cockpit mobile deve manter-se leve, direto e com poucas decisões por ecrã. Esta fase deve privilegiar nomes claros, ações simples e zero ruído.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
