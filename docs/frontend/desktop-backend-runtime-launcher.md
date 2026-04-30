# Desktop Backend Runtime Launcher

## Problema encontrado no teste real

O APK conseguia apontar para o IP correto do PC (`192.168.1.81:8000`), mas a página continuava offline. No PC também aparecia erro/impossível apresentar.

A causa era crítica: o `GodModeDesktop.exe` antigo não arrancava o backend FastAPI. O launcher apenas escrevia alguns ficheiros JSON e abria uma URL local antiga (`127.0.0.1:4173`), enquanto o APK esperava o backend em `:8000`.

## Correção

O launcher desktop passa a:

1. carregar o backend empacotado;
2. arrancar `uvicorn main:app`;
3. servir em `0.0.0.0:8000`;
4. aguardar `/health`;
5. abrir `http://127.0.0.1:8000/app/home` no PC;
6. gerar pairing payload com URL LAN;
7. gerar diagnóstico HTML se o backend falhar.

## URLs

- PC local: `http://127.0.0.1:8000/app/home`
- Telemóvel na mesma rede: `http://IP_DO_PC:8000/app/home`
- Health: `http://127.0.0.1:8000/health`

## Ficheiros alterados

- `desktop/godmode_desktop_launcher.py`
- `desktop/GodModeDesktop.spec`

## Diagnóstico

Se falhar, o launcher escreve em `%APPDATA%/GodModeDesktop/`:

- `desktop_runtime.log`
- `desktop_runtime_state.json`
- `desktop_backend_diagnostic.html`
- `godmode-mobile-pairing.json`

## Segurança

- Não guarda credenciais.
- Não abre portas externas para a internet.
- Expõe apenas o backend local/LAN na porta 8000.
- Continua dependente da firewall/router local.

## Resultado esperado

Depois de instalar a nova versão do EXE:

1. abrir `GodModeDesktop.exe`;
2. backend deve responder em `/health`;
3. PC deve abrir `/app/home`;
4. APK deve abrir `http://192.168.1.81:8000/app/home`.
