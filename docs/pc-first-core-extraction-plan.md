# PC-First Core Extraction Phase Plan

## Branch
- `feature/pc-first-core-extraction`

## Objetivo
Adicionar uma camada de extração do núcleo para o God Mode conseguir separar o core operacional do arranque cloud-first original, deixando Vercel, Render e Supabase como apoio opcional e reforçando o PC como cérebro principal e o APK como thin client.

## Meta funcional
- representar superfícies do core PC-first
- representar ações de extração e isolamento do núcleo
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de migração
- preparar a fase seguinte de runtime local dominante

## Blocos desta fase
### 1. PC-first core extraction contract
Representar:
- pc_first_core_id
- core_runtime
- cloud_support_mode
- extraction_scope
- extraction_status

### 2. PC-first extraction action contract
Representar:
- pc_first_extraction_action_id
- extraction_area
- action_type
- action_label
- migration_target
- action_status

### 3. Services and routes
Criar backend para:
- devolver surfaces do core PC-first
- devolver ações de extração
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O APK continua fino. O PC assume o cérebro e o runtime principal. A cloud deixa de ser centro e passa a apoio opcional.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
