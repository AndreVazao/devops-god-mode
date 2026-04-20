# Android Progressive Runtime Binding Plan

## Branch
- `feature/android-progressive-runtime-binding`

## Objetivo
Endurecer a camada progressiva do Android, ligando explicitamente runtime shell e pairing ao output progressivo, para aproximar o pipeline novo de um fluxo mais real.

## Meta funcional
- definir binding de runtime progressivo
- definir binding de pairing progressivo
- expor summary do binding por API
- expor artefactos de runtime/pairing progressivos
- preparar a fase seguinte de Android ainda mais real

## Blocos desta fase
### 1. Progressive runtime binding contract
Representar:
- binding_id
- runtime_mode
- shell_status
- pairing_mode
- binding_status
- output_target

### 2. Progressive pairing asset contract
Representar:
- asset_id
- asset_name
- pairing_mode
- topology_binding
- asset_status

### 3. Services and routes
Criar backend para:
- devolver summary do runtime binding progressivo
- devolver assets de runtime e pairing
- devolver próximo passo do binding

### 4. Workflow alignment
Atualizar o workflow progressivo para incluir outputs explícitos de runtime binding e pairing binding.

### 5. Scope
Nesta fase ainda não fecha o APK Android final.
Fecha a ligação explícita entre pipeline progressivo, runtime shell e pairing.
