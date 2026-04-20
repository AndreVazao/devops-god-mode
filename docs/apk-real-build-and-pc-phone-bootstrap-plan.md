# APK Real Build And PC Phone Bootstrap Plan

> Legacy foundation note:
> este documento continua na repo como referência histórica de uma fase intermédia de Android mais realista.
> não representa ainda o fluxo final principal do `main`.
> ver também `docs/archive/legacy-foundations-index.md`.

## Branch
- `feature/apk-real-build-and-pc-phone-bootstrap`

## Objetivo
Dar um salto maior no God Mode: aproximar o build Android de algo mais real e, ao mesmo tempo, preparar a configuração automática entre PC e telemóvel para o modo final `pc_and_phone_primary`.

## Resultado esperado
- cockpit mobile preparado para empacotamento Android mais real
- perfil de pairing entre PC e telemóvel
- bootstrap local com autodetect e autoconfig
- QR/manual pairing payload pronto
- workflow Android mais realista que o placeholder inicial
- direção forte para merge grande e útil

## Blocos desta fase
### 1. Android real build profile
Representar:
- build_id
- target_platform
- artifact_type
- app_mode
- entrypoint
- packaging_tool
- output_name
- runtime_topology
- build_status

### 2. PC phone bootstrap topology
Representar:
- bootstrap_id
- primary_runtime
- remote_client
- autodetect
- autoconfig
- local_backend_url
- local_shell_url
- pairing_mode
- tunnel_mode
- final_status

### 3. Backend bootstrap service
Criar serviço para:
- devolver defaults zero-touch
- gerar pairing payload
- listar bootstrap profiles
- promover `render_test` para `pc_and_phone_primary`

### 4. Android build workflow upgrade
Preparar workflow Android com:
- setup Node
- geração de artefacto mobile mais real
- estrutura de output Android dedicada
- upload best-effort

### 5. Scope
Ainda não fecha o app Android final de produção.
Fecha a fundação séria para:
- APK mais real
- pairing simples PC ↔ telemóvel
- bootstrap automático
