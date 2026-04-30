# Release Candidate Handoff

## Objetivo

A Phase 143 cria o pacote final de handoff para a primeira instalação real controlada.

Isto evita o operador ter de interpretar vários painéis antes de instalar.

## Endpoints

- `GET/POST /api/release-candidate-handoff/status`
- `GET/POST /api/release-candidate-handoff/panel`
- `POST /api/release-candidate-handoff/build`
- `GET/POST /api/release-candidate-handoff/latest`
- `GET/POST /api/release-candidate-handoff/package`

## O que inclui

- versão candidata (`RC1` por defeito);
- commit SHA;
- artifacts esperados;
- workflows associados;
- estado do gate final;
- download center;
- home launch;
- first real run checklist;
- smoke test;
- blockers;
- passos do operador;
- política de rollback.

## Artifacts esperados

### PC

- artifact: `godmode-windows-exe`
- ficheiro: `GodModeDesktop.exe`
- workflow: `windows-exe-real-build.yml`

### Android

- artifact: `godmode-android-webview-apk`
- ficheiro: `GodModeMobile-debug.apk`
- workflow: `android-real-build-progressive.yml`

## Passos finais

1. Abrir GitHub Actions e baixar artifacts.
2. Extrair/abrir bundle do EXE no PC.
3. Executar `GodModeDesktop.exe`.
4. Instalar `GodModeMobile-debug.apk`.
5. Emparelhar APK ao PC.
6. Abrir Modo Fácil.
7. Executar checklist `first-real-run`.
8. Dar primeiro comando real curto.

## Regra

Se houver blockers, não instalar como versão de trabalho. Corrigir primeiro o gate final.
