# Artifacts Center

## Objetivo

Mostrar na Home o caminho para obter os pacotes principais do God Mode:

- APK Android;
- EXE Windows.

Os links finais dependem do run do GitHub Actions. O Artifacts Center dá ao operador um mapa estável com workflows, nomes esperados e passos de instalação.

## API

- `GET /api/artifacts-center/status`
- `GET /api/artifacts-center/package`
- `GET /api/artifacts-center/dashboard`

## Integração com Home

A Home inclui:

- bloco `artifacts_center` no dashboard/status;
- botão `APK/EXE`;
- card `APK/EXE` no resumo;
- modo condução com número de pacotes previstos.

## Pacotes esperados

### APK

- workflow: `Android APK Build`;
- artifact esperado: `godmode-android-webview-apk`;
- ficheiro esperado: `GodModeMobile-debug.apk`;
- destino: telemóvel Android.

### EXE

- workflow: `Windows EXE Build`;
- artifact esperado: `godmode-windows-exe`;
- ficheiro esperado: `GodMode.exe`;
- destino: PC Windows.

## Ordem operacional

1. Abrir GitHub Actions.
2. Abrir último run verde em `main`.
3. Obter o APK.
4. Obter o EXE.
5. Abrir EXE no PC e depois APK no telemóvel.

## Limite conhecido

Esta fase não usa API autenticada do GitHub para obter pacotes diretamente. Ela mostra o caminho canónico e nomes esperados dos pacotes.
