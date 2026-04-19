# Runtime Supervisor And Guidance Plan

## Branch
- `feature/runtime-supervisor-and-guidance`

## Objetivo
Adicionar uma camada mais inteligente ao God Mode para supervisionar o runtime local, resumir o estado atual, recomendar a próxima ação e expor guidance claro no PC e no telemóvel.

## Meta funcional
- consolidar runtime health
- consolidar readiness do handoff desktop/mobile
- recomendar próxima ação operacional
- expor guidance simples para o utilizador
- aproximar o sistema de um assistente operacional local

## Blocos desta fase
### 1. Supervisor contract
Representar:
- supervisor_id
- runtime_mode
- runtime_health
- bundle_readiness
- pairing_readiness
- recommended_next_action
- guidance_status

### 2. Supervisor service
Criar serviço para:
- devolver summary do runtime
- devolver readiness summary
- devolver recommended next action

### 3. Supervisor routes
Endpoints para:
- status
- summary
- readiness
- recommended-next-action
