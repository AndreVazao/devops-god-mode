# Windows EXE Build Workflow Plan

## Branch
- `feature/windows-exe-build-workflow`

## Objetivo
Preparar o primeiro workflow real de packaging para gerar um `.exe` do God Mode para Windows, com foco no PC como runtime principal e no telemóvel como cockpit remoto.

## Meta funcional
- definir entrada de build para Windows
- definir artefacto `.exe` esperado
- preparar workflow GitHub Actions para packaging desktop
- manter o empacotamento simples, automático e orientado ao uso no PC
- deixar a experiência futura de instalação o mais zero-touch possível

## Blocos desta fase
### 1. Build contract
Representar:
- build_id
- target_platform
- artifact_type
- entry_script
- packaging_tool
- output_name
- build_status

### 2. Workflow foundation
Criar workflow para:
- checkout
- setup Python
- instalar dependências de build
- gerar artefacto Windows `.exe`
- publicar artefacto do build

### 3. Desktop install direction
Documentar direção futura para:
- shortcut na área de trabalho
- autoconfig local
- runtime principal invisível no PC
- dashboard intuitivo para controlo direto

### 4. Scope
Esta fase foca só o `.exe` do Windows.
A fase do APK vem logo a seguir.

## Critérios de saída
- plano criado
- contrato de build criado
- workflow base de `.exe` criado
- smoke/validação da fase criado
