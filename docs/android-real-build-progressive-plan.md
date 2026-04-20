# Android Real Build Progressive Plan

## Branch
- `feature/android-real-build-progressive`

## Objetivo
Levar a fundação do pipeline Android real para uma camada progressiva de build, mais próxima de um fluxo real, mantendo a arquitetura `pc_and_phone_primary` e sem prometer ainda o APK final de produção.

## Meta funcional
- definir fases progressivas do build Android real
- expor estado progressivo do pipeline por API
- expor artifacts progressivos esperados
- criar workflow progressivo separado do foundation inicial
- preparar a fase seguinte de build Android ainda mais real

## Blocos desta fase
### 1. Android progressive stage contract
Representar:
- stage_id
- stage_name
- stage_order
- stage_summary
- expected_outputs
- stage_status

### 2. Android progressive artifact contract
Representar:
- artifact_id
- artifact_name
- artifact_role
- topology_binding
- artifact_status

### 3. Services and routes
Criar backend para:
- devolver summary do build Android progressivo
- devolver stages do pipeline
- devolver artifacts progressivos esperados
- devolver próximo stage prioritário

### 4. Workflow progressive
Criar workflow novo para:
- preparar estrutura progressiva de output Android
- gerar manifest/config/artifact placeholders do pipeline novo
- publicar artifacts best-effort

### 5. Scope
Nesta fase ainda não fecha o APK Android final de produção.
Fecha a camada progressiva do pipeline novo para aproximar o build Android real.
