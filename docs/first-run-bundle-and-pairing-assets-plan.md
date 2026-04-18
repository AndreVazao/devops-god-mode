# First Run Bundle And Pairing Assets Plan

## Branch
- `feature/first-run-bundle-and-pairing-assets`

## Objetivo
Juntar numa camada mais prática tudo o que o utilizador precisa no primeiro arranque: bundle desktop, payloads de pairing PC ↔ telemóvel e assets de bootstrap para o cockpit mobile e o launcher desktop.

## Meta funcional
- gerar bundle de first run consolidado
- juntar payloads desktop e mobile num só ponto
- gerar pairing asset pronto para QR/manual code
- alinhar outputs do launcher desktop e do build Android
- aproximar o produto do modo "abrir e trabalhar"

## Blocos desta fase
### 1. First run bundle contract
Representar:
- bundle_id
- runtime_mode
- desktop_payloads
- mobile_payloads
- pairing_payload
- recommended_sequence
- final_status

### 2. First run bundle service
Criar serviço para:
- consolidar bootstrap desktop
- consolidar bootstrap PC-phone
- gerar asset de pairing
- devolver sequência recomendada de first run

### 3. First run bundle routes
Endpoints para:
- status
- bundle completo
- pairing asset

### 4. Packaging alignment
Atualizar launcher desktop e output Android para incluir asset de pairing partilhado.
