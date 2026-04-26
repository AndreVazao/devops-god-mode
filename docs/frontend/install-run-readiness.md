# Install / Run Readiness

## Cockpit

- `/app/install-run-readiness`
- `/app/install-readiness`

## API

- `GET /api/install-run-readiness/status`
- `GET /api/install-run-readiness/package`
- `GET /api/install-run-readiness/report`
- `GET /api/install-run-readiness/checklist`
- `GET /api/install-run-readiness/dashboard`

## Objetivo

Responder de forma direta:

> O God Mode está pronto para instalar no PC e usar pelo APK?

## O que verifica

### PC local

- backend FastAPI;
- requirements;
- desktop launcher;
- PyInstaller spec;
- health/config.

### APK/mobile

- APK launch config;
- `/app/apk-start`;
- first run wizard;
- chat com cartões inline;
- fallback chat/home.

### Backend operacional

- AndreOS Memory Core;
- Mobile Start Config;
- Mobile First Run Wizard;
- Chat Inline Card Renderer;
- Mobile Approval Cockpit;
- Request Orchestrator;
- Request Worker Loop;
- Offline Command Buffer.

### GitHub Actions/builds

- Windows EXE build;
- Android APK build;
- Universal Total Test;
- prune/project tree validation.

## Estados

- `green`: pronto para instalação local controlada e uso mobile;
- `yellow`: usável com avisos;
- `red`: não instalar antes de corrigir blockers.

## Caminho end-to-end esperado

1. Abrir `/app/apk-start`.
2. Validar `/app/mobile-first-run`.
3. Entrar em `/app/operator-chat-sync-cards`.
4. Enviar ordem por `/api/chat-inline-card-renderer/send-orchestrated`.
5. Criar job durável em `/api/request-orchestrator/submit`.
6. Continuar com `/api/request-worker/tick`.
7. Se bloquear, aprovar em `/app/mobile-approval-cockpit-v2`.
8. Retomar com `/api/request-orchestrator/resume`.
9. Se houver offline, usar `/app/offline-buffer`.

## Segurança

Este cockpit não executa alterações destrutivas. Ele só lê estado, calcula readiness e mostra blockers/checklist.
