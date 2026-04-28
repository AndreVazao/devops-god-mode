# Artifact Download Shortcuts

## Objetivo

A Phase 96 reduz a fricção para obter os ficheiros finais do God Mode pelo telemóvel.

O Artifacts Center passa a devolver atalhos diretos para:

- últimos builds em `main`;
- workflow Android APK;
- workflow Windows EXE.

## API

`/api/artifacts-center/dashboard` inclui:

- `download_shortcuts`
- `mobile_download_steps`
- `workflow_runs_url` em cada artifact.

## Artifacts esperados

### APK Android

- workflow: `.github/workflows/android-real-build-progressive.yml`
- artifact: `godmode-android-webview-apk`
- ficheiro esperado: `GodModeMobile-debug.apk`

### EXE Windows

- workflow: `.github/workflows/windows-exe-real-build.yml`
- artifact: `godmode-windows-exe`
- ficheiro esperado: `GodModeDesktop.exe`

## Fluxo móvel

1. Abrir `Instalar agora`.
2. Abrir `APK/EXE`.
3. Abrir `Últimos builds em main`.
4. Escolher o último run verde.
5. Obter os dois artifacts finais.

## Critério de aceitação

A validação confirma:

- atalhos existem;
- URLs apontam para workflows canónicos;
- nomes de artifact estão corretos;
- `Project Tree Autorefresh` vê a documentação nova.
