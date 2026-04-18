# Android Real Runtime Shell V2 Plan

## Branch
- `feature/android-real-runtime-shell-v2`

## Objetivo
Levar o cockpit Android para uma camada mais próxima do uso real: shell mobile com bootstrap consumível, estado de pairing visível e arranque simples para trabalhar com o PC principal sem configuração chata.

## Meta funcional
- definir shell mobile runtime profile
- representar estado de pairing no mobile
- gerar payload de runtime shell Android
- alinhar assets do first run bundle com o cockpit mobile
- preparar output Android mais útil para o utilizador final

## Blocos desta fase
### 1. Android runtime shell contract
Representar:
- shell_id
- runtime_mode
- mobile_profile
- bootstrap_asset
- pairing_asset
- backend_hint
- shell_status

### 2. Android runtime shell service
Criar serviço para:
- devolver shell bundle Android
- consolidar bootstrap e pairing assets
- expor hints simples para arranque mobile

### 3. Android runtime shell routes
Endpoints para:
- status
- shell bundle
- pairing hint

### 4. Build alignment
Atualizar o build Android para incluir:
- runtime shell asset
- pairing asset
- bootstrap asset
- sequência recomendada de primeiro uso
