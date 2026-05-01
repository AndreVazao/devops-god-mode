# Windows EXE Boot Smoke Test

## Motivo

No teste real, o artifact parecia pequeno e o workflow era rápido. O build anterior confirmava que o EXE era gerado, mas não confirmava de forma suficiente que o EXE arrancava o backend real e respondia em `/health`.

## Correção

O workflow `Windows EXE Build` passa a executar um smoke test após compilar o EXE:

1. limpa `%APPDATA%/GodModeDesktop` no runner;
2. arranca `dist/GodModeDesktop.exe`;
3. aguarda até 60 segundos;
4. testa `http://127.0.0.1:8000/health`;
5. copia logs/estado/diagnóstico para `dist/onboarding`;
6. falha o workflow se o endpoint não responder.

## Ficheiro alterado

- `.github/workflows/windows-exe-real-build.yml`

## Artifacts adicionais

Quando disponíveis, o artifact Windows inclui:

- `desktop-boot-smoke-result.json`
- `desktop-runtime-state-ci.json`
- `desktop-runtime-ci.log`
- `desktop-backend-diagnostic-ci.html`

## Resultado esperado

O artifact `godmode-windows-exe` só deve ser considerado pronto quando:

- o EXE compila;
- os ficheiros esperados existem;
- o EXE arranca;
- o backend responde em `/health`.

## Segurança

- O teste corre apenas no runner Windows.
- Não usa credenciais.
- Não toca em dados reais do operador.
- Só valida runtime local em `127.0.0.1:8000`.
