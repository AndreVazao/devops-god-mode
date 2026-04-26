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
- o APK Android passa a ser um APK debug real WebView shell;
- o operador deve instalar o APK apenas em teste controlado e configurar o URL do PC.

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

- `godmode-android-webview-apk`

Ficheiro principal:

- `GodModeMobile-debug.apk`

Estado:

- APK debug real;
- WebView shell;
- abre `/app/apk-start`;
- por defeito usa `http://127.0.0.1:8000`;
- num telemóvel físico, o operador deve trocar o URL base para o IP do PC, por exemplo `http://192.168.1.50:8000`.

## Passos de download

1. Abrir GitHub Actions.
2. Abrir último run verde de Windows EXE Build.
3. Baixar artifact `godmode-windows-exe`.
4. Abrir último run verde de Android APK Build.
5. Baixar artifact `godmode-android-webview-apk`.
6. Instalar `GodModeMobile-debug.apk` em teste controlado.
7. No APK, configurar o URL do PC.
8. Validar no God Mode com `/app/first-use`, `/app/install-readiness` e `/app/e2e-operational-drill`.

## Próximo blocker técnico

Depois do APK debug real, o próximo passo será endurecer a distribuição:

- assinatura release;
- configuração automática do URL/pareamento com o PC;
- QR/pairing flow;
- permissões e diagnóstico de rede;
- versão release fora de debug.
