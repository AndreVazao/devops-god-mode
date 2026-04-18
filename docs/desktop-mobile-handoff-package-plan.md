# Desktop Mobile Handoff Package Plan

## Branch
- `feature/desktop-mobile-handoff-package`

## Objetivo
Criar uma camada unificada de handoff entre o bundle desktop e o cockpit mobile, para o utilizador abrir o pacote no PC, emparelhar o telemóvel e começar a trabalhar com o mínimo de passos manuais.

## Meta funcional
- definir contrato do pacote de handoff
- consolidar assets desktop e mobile num bundle único
- expor sequência de instalação e pairing
- alinhar builds Windows e Android com o mesmo pacote lógico
- aproximar ainda mais o produto do modo `abrir e trabalhar`

## Blocos desta fase
### 1. Handoff contract
Representar:
- handoff_id
- runtime_mode
- desktop_bundle_assets
- mobile_bundle_assets
- pairing_asset
- install_sequence
- handoff_status

### 2. Handoff service
Criar serviço para:
- devolver pacote consolidado desktop + mobile
- devolver sequência de handoff
- devolver resumo do pairing

### 3. Handoff routes
Endpoints para:
- status
- package
- install-sequence
- pairing-summary

### 4. Build alignment
Atualizar builds para incluir:
- `desktop-mobile-handoff.json`
- sequência de instalação
- resumo de pairing
