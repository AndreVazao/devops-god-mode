# Asset And Workspace Sync Plan

## Branch
- `feature/assetsync`

## Objetivo
Adicionar uma camada de sync de assets e workspaces para o God Mode conseguir receber uploads, fazer downloads para análise, expor previews para aprovação e preparar ligação operacional a fontes como Drive, Dropbox, Figma e equivalentes a partir do PC local.

## Meta funcional
- representar assets recebidos para análise ou build
- representar operações de download e upload locais
- representar workspaces externos ligados ao PC local
- representar previews compactos prontos para cockpit mobile
- expor próxima ação prioritária de asset/workspace sync
- preparar a fase seguinte de aprovação visual e utilização dos assets no fluxo de build local

## Blocos desta fase
### 1. Asset sync contract
Representar:
- asset_sync_id
- target_project
- asset_kind
- transfer_direction
- sync_status

### 2. Workspace bridge contract
Representar:
- workspace_bridge_id
- workspace_kind
- access_mode
- intended_use
- bridge_status

### 3. Asset preview contract
Representar:
- asset_preview_id
- target_project
- preview_kind
- approval_mode
- preview_status

### 4. Services and routes
Criar backend para:
- devolver assets recebidos e transferências preparadas
- devolver workspaces externos ligados ao PC local
- devolver previews compactos para o cockpit
- devolver próxima ação prioritária

### 5. UX note
O utilizador deve ver só o essencial: que ficheiro entrou ou saiu, para que projeto serve, se já há preview pronto no telemóvel e se já pode dar OK visual.

### 6. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
