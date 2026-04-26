# First Usable Release

## Cockpit

- `/app/first-usable-release`
- `/app/first-use`

## API

- `GET /api/first-usable-release/status`
- `GET /api/first-usable-release/package`
- `GET /api/first-usable-release/plan`
- `GET /api/first-usable-release/guide`
- `GET /api/first-usable-release/dashboard`

## Objetivo

Transformar o God Mode num produto utilizável pela primeira vez:

- instalar/abrir no PC;
- abrir o APK/mobile cockpit;
- validar readiness;
- correr drill operacional;
- dar a primeira ordem no chat;
- deixar o backend continuar até terminar ou bloquear.

## Uso no PC

1. Gerar/baixar EXE Windows pelo workflow `windows-exe-real-build.yml` ou usar `desktop/godmode_desktop_launcher.py`.
2. Confirmar backend com `/health` e `/api/system/config`.
3. Abrir `/app/install-readiness`.
4. Correr `/app/e2e-operational-drill`.

## Uso no telemóvel/APK

1. Entrada única: `/app/apk-start`.
2. Validar `/app/mobile-first-run`.
3. Usar `/app/operator-chat-sync-cards`.
4. Dar ordens em linguagem normal.
5. Aprovar quando necessário em `/app/mobile-approval-cockpit-v2`.

## Primeiras ordens recomendadas

- “quero começar a ganhar dinheiro com o projeto mais rápido; faz o processo até precisares do meu OK”
- “audita o God Mode e diz o próximo blocker para ficar pronto a instalar e usar”
- “guarda esta ordem e continua no PC quando ele voltar online”
- “prepara uso de Gemini/ChatGPT provider e pára quando precisares do meu login manual”

## Quando bloquear

- Se pedir OK: abrir `/app/mobile-approval-cockpit-v2`.
- Se pedir login/provider: fazer login manual no provider e não escrever credenciais no chat.
- Se APK desligar: o job fica no backend; abrir `/app/request-worker` ou `/app/request-orchestrator`.
- Se PC/telemóvel desconectar: usar `/app/offline-buffer`.

## Decisão de release

O cockpit combina:

- Install Run Readiness;
- End-to-End Operational Drill;
- Mobile First Run Wizard;
- Request Worker Loop;
- workflows de EXE/APK/testes.

O estado pode ser:

- `green`: pronto para primeira instalação controlada;
- `yellow`: usável para teste controlado, mas com blockers/avisos;
- `red`: não usar ainda como operação real.
