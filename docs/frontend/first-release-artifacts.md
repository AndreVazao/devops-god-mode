# First Release Artifact Center

## Cockpit

- `/app/first-release-artifacts`
- `/app/release-artifacts`

## API

- `GET /api/first-release-artifacts/status`
- `GET /api/first-release-artifacts/package`
- `GET /api/first-release-artifacts/report`
- `GET /api/first-release-artifacts/dashboard`

## Objetivo

Mostrar a verdade dos artifacts da primeira release utilizável:

- o EXE Windows é caminho real de instalação PC;
- o APK Android ainda é placeholder no workflow atual;
- o operador não deve confundir placeholder com APK instalável real.

## Estado atual dos builds

### Windows EXE

Workflow:

- `.github/workflows/windows-exe-real-build.yml`

Artifact esperado:

- `godmode-windows-exe`

Estado:

- build real via PyInstaller;
- pode ser usado como caminho PC-first controlado.

### Android APK

Workflow:

- `.github/workflows/android-real-build-progressive.yml`

Artifact esperado:

- `godmode-android-apk-placeholder`

Estado:

- ainda placeholder;
- não deve ser tratado como APK real instalável de produto;
- próxima fase técnica deve substituir por APK real/WebView shell.

## Passos de download

1. Abrir GitHub Actions.
2. Abrir último run verde de Windows EXE Build.
3. Baixar artifact `godmode-windows-exe`.
4. Validar no God Mode com `/app/first-use`, `/app/install-readiness` e `/app/e2e-operational-drill`.
5. Para Android, não tratar o artifact placeholder como release real.

## Próximo blocker técnico

Criar o APK real/WebView shell, ou pelo menos atualizar o pipeline Android para produzir um APK instalável verdadeiro que abra `/app/apk-start`.
