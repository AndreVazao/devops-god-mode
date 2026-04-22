# Canonical Build And Test Workflows

## Objetivo
Definir o conjunto mínimo de workflows principais para a repo, mantendo o `prune` intocado e evitando proliferação de workflows de fase já ultrapassados.

## Canonical workflows
### 1. Windows EXE build
- `.github/workflows/windows-exe-real-build.yml`
- build canónico do `.exe` desktop para instalar no PC
- alinhado com o rumo local-first PC + telefone
- trigger generalizado para acompanhar fases futuras sem workflow temporário por fase

### 2. Android APK build
- `.github/workflows/android-real-build-progressive.yml`
- pipeline canónico **placeholder** do Android nesta fase
- ainda não representa uma build APK real
- serve para manter contratos, artefactos e ligação ao runtime enquanto a build Android real não entra
- trigger generalizado para acompanhar fases futuras sem workflow temporário por fase

### 3. Universal total test
- `.github/workflows/universal-total-test.yml`
- workflow canónico de teste transversal da stack
- usado para validar as fases evolutivas do backend sem criar smoke workflows descartáveis por etapa

## Estratégia operacional
- `prune` fica intocado
- workflows antigos de fase podem ser removidos gradualmente
- o workflow Windows é a referência real de build local-first
- o workflow Android continua temporariamente como placeholder explícito até haver pipeline real
- o workflow universal é a referência para validar evolução incremental do runtime
- estes três workflows passam a ser a referência principal de build e teste

## Regra de evolução
Quando uma nova fase mexer no runtime, cockpit, sessões, buffering, supervisor ou documentação operacional:
- primeiro tentar reutilizar estes workflows gerais
- só criar workflow novo se existir necessidade estrutural real
- quando possível, absorver o teste dessa nova fase no workflow universal
