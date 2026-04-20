# Android Mobile Build Plan

> Legacy foundation note:
> este documento continua na repo como referência histórica de uma fase inicial de Android placeholder.
> não representa o fluxo principal atual do `main`.
> ver também `docs/archive/legacy-foundations-index.md`.

## Branch
- `feature/android-apk-build-workflow`

## Objetivo
Preparar a base do workflow de build Android para o cockpit mobile do God Mode, mantendo o PC como runtime principal e o telemóvel como cliente remoto.

## Meta funcional
- definir perfil de build Android
- definir artefacto APK esperado
- preparar workflow GitHub Actions base
- manter experiência mobile simples e automática
- preparar pairing fácil com o PC

## Blocos desta fase
### 1. Build contract
Representar:
- build_id
- target_platform
- artifact_type
- app_mode
- entrypoint
- packaging_tool
- output_name
- build_status

### 2. Workflow foundation
Criar workflow para:
- checkout
- setup Node
- preparar artefacto APK foundation
- publicar artefacto do build em modo best-effort

### 3. Mobile usability direction
Documentar direção futura para:
- pairing simples com o PC
- defaults automáticos
- cockpit remoto intuitivo
- zero-touch sempre que possível

### 4. Scope
Esta fase foca só a base do APK.
A fase seguinte endurece o build Android real.
