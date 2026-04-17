# Write Verify And Rollback Plan

## Branch
- `feature/write-verify-and-rollback`

## Objetivo
Dar ao God Mode a fase seguinte da escrita local: verificar resultado após escrita, marcar falhas, e executar rollback simples quando a validação falhar.

## Meta funcional
- registar verificação pós-escrita
- guardar resultado de validação local
- distinguir sucesso, falha e rollback
- ligar rollback ao backup criado antes da escrita
- preparar base para validadores locais reais no PC

## Blocos desta fase
### 1. Verify contract
Representar:
- verify_run_id
- write_run_id
- verification_mode
- verification_checks
- verification_result
- rollback_triggered
- final_status

### 2. Verify service
Adicionar serviço para:
- criar verificação para uma escrita real
- marcar validação passada ou falhada
- disparar rollback lógico quando falhar
- guardar resultado final

### 3. Verify routes
Endpoints para:
- criar verificação
- listar verificações
- consultar verificação
- marcar falha
- marcar sucesso
- executar rollback lógico

### 4. Safety layer
- só verificar writes existentes
- rollback só disponível quando houver backup
- escrita já restaurada não deve reexecutar rollback

## Critérios de saída
- plano criado
- base backend para verify/rollback criada
- integração com real local write criada
- smoke verde da fase
