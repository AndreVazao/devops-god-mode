# Canonical Build And Test Workflows

## Objetivo
Definir o conjunto mínimo de workflows principais para a repo, mantendo o `prune` intocado e evitando proliferação de workflows de fase já ultrapassados.

## Canonical workflows
### 1. Windows EXE build
- `.github/workflows/windows-exe-real-build.yml`
- build canónico do `.exe` desktop para instalar no PC

### 2. Android APK build
- `.github/workflows/android-real-build-progressive.yml`
- build canónico do único APK Android

### 3. Universal total test
- `.github/workflows/universal-total-test.yml`
- workflow canónico de teste transversal da stack

## Regra operacional
- `prune` fica intocado
- workflows antigos de fase podem ser removidos gradualmente
- estes três workflows passam a ser a referência principal de build e teste
