# Android Real Runtime Shell Plan

## Branch
- `feature/android-real-runtime-shell`

## Objetivo
Dar a próxima camada real ao lado Android: preparar um runtime shell mobile mais credível para o cockpit remoto, com config local, bootstrap importável e defaults simples para ligação ao PC principal.

## Meta funcional
- definir shell runtime profile Android
- preparar config mobile local
- importar bootstrap do PC
- expor modo simples/intuitivo para cockpit remoto
- alinhar build Android com output menos placeholder

## Blocos desta fase
### 1. Android runtime shell contract
Representar:
- runtime_id
- app_mode
- config_source
- bootstrap_import
- pairing_mode
- ui_profile
- local_status

### 2. Mobile config service
Criar serviço para:
- devolver config mobile default
- aceitar bootstrap import do PC
- devolver shell profile simples

### 3. Mobile shell routes
Endpoints para:
- status
- config default
- import bootstrap
- shell profile

### 4. Android build alignment
Preparar a próxima evolução do build Android para usar estes outputs.
