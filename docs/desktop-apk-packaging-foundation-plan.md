# Desktop APK Packaging Foundation Plan

## Branch
- `feature/desktop-apk-packaging-foundation`

## Objetivo
Preparar a base para empacotamento do God Mode em `.exe` para o PC e APK para o telemóvel, mantendo o Render apenas como ambiente temporário de testes e deixando o alvo final como PC + telemóvel.

## Contexto operacional
- Render serve apenas para testes e observação rápida do comportamento
- alvo final: runtime principal no PC de casa
- telemóvel funciona como cockpit remoto e cliente de operação
- depois o fluxo principal deve ser PC local + telemóvel, sem dependência do Render

## Meta funcional
- definir perfis de packaging desktop e mobile
- definir artefactos esperados `.exe` e APK
- preparar contratos de build profile
- preparar workflow unificado de packaging futuro
- separar modo `render_test` de modo `pc_and_phone_primary`

## Blocos desta fase
### 1. Packaging contract
Representar:
- profile_id
- target_platform
- artifact_type
- runtime_mode
- entrypoint
- output_name
- packaging_status
- notes

### 2. Runtime topology contract
Representar:
- topology_id
- primary_runtime
- remote_client
- render_role
- tunnel_mode
- persistence_mode

### 3. Backend routes later
Preparar base para futuras rotas de:
- listar profiles de build
- listar topologias de runtime
- promover de `render_test` para `pc_and_phone_primary`

### 4. Future workflows
Deixar explícito que virão depois:
- workflow `.exe` para Windows PC
- workflow APK para Android
- modo final centrado em PC + telemóvel

## Critérios de saída
- plano criado
- direção de packaging definida
- Render assumido como temporário
- base pronta para fase seguinte de contracts e workflows
