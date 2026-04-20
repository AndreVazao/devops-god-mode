# Android Real Pipeline Readiness Plan

## Branch
- `feature/android-real-pipeline-readiness`

## Objetivo
Começar a substituir o placeholder Android por uma camada ativa de readiness para pipeline real, alinhada com a arquitetura atual: PC como cérebro principal e telemóvel como cockpit remoto principal.

## Meta funcional
- definir readiness do pipeline Android real
- expor blockers explícitos para sair do placeholder atual
- expor sequência de substituição do workflow foundation
- consolidar topologia PC + phone como alvo oficial
- preparar a fase seguinte de pipeline Android real

## Blocos desta fase
### 1. Android readiness contract
Representar:
- readiness_id
- target_topology
- current_pipeline_mode
- replacement_status
- real_build_readiness
- blockers
- next_step

### 2. Android replacement step contract
Representar:
- step_id
- phase
- step_summary
- required_artifacts
- step_status

### 3. Services and routes
Criar backend para:
- devolver summary de readiness Android real
- devolver blockers
- devolver steps de substituição do placeholder
- devolver próximo passo prioritário

### 4. Scope
Nesta fase ainda não fecha o APK Android final.
Fecha a camada ativa de readiness que prepara a troca do foundation placeholder por pipeline Android real.
