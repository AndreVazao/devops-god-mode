# Patch Apply And Diff Plan

## Branch
- `feature/patch-apply-and-diff`

## Objetivo
Dar o próximo passo ao patch engine local: simular aplicação, gerar diff resumido, validar risco e preparar aplicação controlada no PC local.

## Meta funcional
- criar proposta de aplicação de patch
- gerar preview de before/after
- guardar diff resumido
- separar simulação de aplicação real
- bloquear aplicação real quando exigir approval
- deixar low-risk pronto para execução local futura

## Blocos desta fase
### 1. Patch preview contract
Representar:
- patch_id
- apply_mode
- before_preview
- after_preview
- diff_summary
- validation_status
- apply_status

### 2. Patch apply service
Adicionar ao patch engine:
- simulação de aplicação
- diff resumido
- estado `preview_ready`
- estado `applied_locally_pending_validation`
- estado `applied_and_validated`

### 3. Patch apply routes
Endpoints para:
- gerar preview
- consultar preview
- marcar aplicação simulada
- sincronizar com approval antes de aplicar

### 4. Approval and risk
- low risk pode avançar para preview/aplicação simulada
- medium/high continua bloqueado até approval

## Critérios de saída
- plano criado
- base para diff e preview criada
- integração com patch engine existente
- smoke verde da fase
