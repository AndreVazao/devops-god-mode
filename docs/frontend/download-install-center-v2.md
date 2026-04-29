# Download Install Center v2

## Objetivo

A Phase 140 cria o centro de download/instalação do God Mode.

O PC é tratado como cérebro principal e cache principal de artifacts. O telemóvel tenta baixar do PC quando houver ligação segura/LAN/túnel. Se não houver ligação direta, o sistema usa fallback por link remoto seguro ou Drive/manual.

## Endpoints

- `GET/POST /api/download-install-center-v2/status`
- `GET/POST /api/download-install-center-v2/panel`
- `GET/POST /api/download-install-center-v2/policy`
- `POST /api/download-install-center-v2/package`
- `POST /api/download-install-center-v2/share`
- `POST /api/download-install-center-v2/transfer-plan`
- `POST /api/download-install-center-v2/intake-request`
- `GET/POST /api/download-install-center-v2/latest`
- `GET/POST /api/download-install-center-v2/full-package`

## Artifacts principais

### Windows EXE

- `GodModeDesktop.exe`
- artifact: `godmode-windows-exe`
- workflow: `.github/workflows/windows-exe-real-build.yml`

### Android APK

- `GodModeMobile-debug.apk`
- artifact: `godmode-android-webview-apk`
- workflow: `.github/workflows/android-real-build-progressive.yml`

## Canais de transferência

### 1. PC local / LAN / túnel

Preferido para:

- APK;
- screenshots;
- logs;
- ficheiros médios;
- envio telefone ↔ PC quando ambos estão ligados.

### 2. Link remoto seguro

Preferido para:

- quando o PC está online mas o telemóvel está fora da rede local;
- acesso pelo túnel seguro.

### 3. Drive/manual fallback

Preferido para:

- ficheiros grandes;
- quando túnel falha;
- quando estás fora de casa;
- quando queres partilhar algo entre PC/telemóvel usando a tua conta Google.

## Transferência de ficheiros gerais

O endpoint `/transfer-plan` decide o melhor caminho para ficheiros como:

- imagens;
- screenshots;
- logs;
- PDFs;
- artifacts;
- ficheiros para usar em projetos.

Exemplo real:

> Tenho uma foto no telemóvel e quero que o God Mode a use como fundo do site.

O God Mode pode escolher:

- enviar pelo túnel/LAN para o PC;
- pedir upload/seleção por Drive;
- criar pedido de intake associado ao projeto.

## Intake request

`/intake-request` cria um pedido para o operador enviar ficheiro.

O pedido fica associado a um projeto e indica:

- tipo esperado;
- objetivo;
- canal preferido;
- mensagem simples para o operador.

## Segurança

- Links temporários expiram.
- Tokens de share não ficam guardados em claro.
- Não guardar tokens Drive/túnel em memória.
- Para ficheiros grandes, preferir Drive/manual fallback.
- Associar ficheiros ao projeto correto.

## Estratégia final

- PC baixa artifacts depois do build.
- Telemóvel baixa do PC quando possível.
- Fora da rede, usa link seguro/Drive.
- O operador não precisa saber o caminho técnico; só envia/recebe o ficheiro.
