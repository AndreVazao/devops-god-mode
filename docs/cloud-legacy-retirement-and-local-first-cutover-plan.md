# Cloud Legacy Retirement And Local First Cutover Plan

## Branch
- `feature/cloud-legacy-retire`

## Objetivo
Desativar explicitamente a herança operacional de Render e Supabase do fluxo principal do God Mode, consolidando o modo local-first onde o PC é o cérebro e o telemóvel é o cockpit.

## Meta funcional
- representar stacks cloud legadas a retirar do fluxo principal
- representar ações de cutover para runtime local-first
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de retirement
- preparar a fase seguinte de limpeza explícita de referências cloud residuais do runtime principal

## Blocos desta fase
### 1. Cloud legacy retirement contract
Representar:
- cloud_legacy_retirement_id
- legacy_stack
- retirement_mode
- runtime_role_after_retirement
- retirement_status

### 2. Local first cutover action contract
Representar:
- local_first_cutover_action_id
- target_runtime
- action_type
- target_component
- cutover_status

### 3. Services and routes
Criar backend para:
- devolver stacks cloud legadas a retirar
- devolver ações de cutover local-first
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que sai do fluxo principal, o que passa a ser local-first e se a cloud ficou apenas opcional.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
