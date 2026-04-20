# Android Real Build Pipeline Foundation Plan

## Branch
- `feature/android-real-build-pipeline-foundation`

## Objetivo
Dar o passo seguinte depois da readiness Android: criar a fundação concreta do pipeline Android real, separada do workflow placeholder histórico, já alinhada com a topologia `pc_and_phone_primary`.

## Meta funcional
- definir contract do pipeline Android real
- definir contract do output Android real
- expor plano de build Android real por API
- criar workflow foundation novo para o pipeline Android real
- manter o placeholder histórico separado até substituição completa

## Blocos desta fase
### 1. Android real pipeline contract
Representar:
- pipeline_id
- target_platform
- topology
- build_mode
- packaging_strategy
- output_type
- readiness_status

### 2. Android real output contract
Representar:
- artifact_id
- artifact_type
- artifact_name
- runtime_binding
- pairing_support
- output_status

### 3. Services and routes
Criar backend para:
- devolver plano do pipeline Android real
- devolver output esperado
- devolver resumo de substituição do placeholder

### 4. Workflow foundation
Criar workflow novo, separado do placeholder histórico, para:
- preparar estrutura de output Android real
- gerar artifacts foundation do pipeline novo
- publicar artifacts best-effort

### 5. Scope
Nesta fase ainda não fecha o APK Android final de produção.
Fecha a fundação concreta do pipeline novo para substituir o workflow placeholder histórico.
