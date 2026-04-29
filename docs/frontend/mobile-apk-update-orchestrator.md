# Mobile APK Update Orchestrator

## Objetivo

A Phase 138 define como o PC/backend pode orquestrar updates do APK no telemóvel.

## Verdade técnica Android

Um APK normal não consegue instalar/desinstalar outro APK, nem atualizar-se em silêncio, sem uma destas condições:

- ADB autorizado pelo utilizador;
- Device Owner / MDM / modo gerido;
- root;
- app privilegiada/sistema;
- interação do utilizador com o Package Installer.

Por isso, o God Mode suporta vários modos em vez de fingir que o Android permite instalação silenciosa normal.

## Modos suportados

### 1. `backend_only`

Quando muda só backend/frontend servido pelo PC.

- Não precisa reinstalar APK.
- APK apenas reconecta ao PC.
- Melhor caminho para updates frequentes.

### 2. `apk_prompt_install`

Quando muda o APK/WebView/permissões.

- O APK recebe/baixa o novo APK.
- Abre o instalador Android.
- O operador toca em Instalar.
- Dados mantidos se o package id e assinatura forem iguais.

### 3. `pc_adb_assisted`

Quando o telefone está ligado/autorizado por ADB.

- PC baixa/envia o artifact.
- PC executa `adb install -r <apk>`.
- Mantém dados da app.
- Requer autorização ADB inicial.

### 4. `device_owner_future`

Modo futuro para dispositivos geridos/kiosk.

- Permite automação mais forte.
- Exige configuração avançada inicial.

## Endpoints

- `GET/POST /api/mobile-apk-update/status`
- `GET/POST /api/mobile-apk-update/panel`
- `GET/POST /api/mobile-apk-update/policy`
- `POST /api/mobile-apk-update/plan`
- `POST /api/mobile-apk-update/handoff`
- `POST /api/mobile-apk-update/adb-script`
- `POST /api/mobile-apk-update/record-result`
- `GET/POST /api/mobile-apk-update/latest`
- `GET/POST /api/mobile-apk-update/package`

## Frases

Preparar update APK:

`UPDATE MOBILE APK`

Gerar script ADB:

`ADB UPDATE APK`

## Preservar dados

Para manter dados no telemóvel:

- usar o mesmo `applicationId` / package id;
- usar a mesma assinatura/certificado;
- instalar por cima;
- não desinstalar primeiro;
- em ADB usar `adb install -r`.

## Estratégia recomendada

- Updates normais: `backend_only`.
- APK só quando mudar shell/permissões/código Android.
- Se telefone estiver ligado ao PC: `pc_adb_assisted`.
- Se estiveres na rua: `apk_prompt_install` com toque manual no instalador.
