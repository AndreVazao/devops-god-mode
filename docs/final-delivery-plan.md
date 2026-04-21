# Final Delivery Phase Plan

## Branch
- `feature/final-delivery-v2`

## Objetivo
Adicionar uma camada final de entrega para o God Mode conseguir destacar o output principal, expor ações diretas de entrega e manter o cockpit mobile leve, intuitivo e rápido até ao momento do download final.

## Meta funcional
- representar sessões finais de entrega por projeto
- representar ações finais de entrega por output
- expor pacote compacto pronto para cockpit mobile
- expor próxima entrega prioritária
- preparar a fase seguinte de handoff final ao utilizador

## Blocos desta fase
### 1. Final delivery contract
Representar:
- final_delivery_id
- recovery_project_id
- deliverable_count
- primary_deliverable_name
- delivery_status

### 2. Final delivery action contract
Representar:
- final_delivery_action_id
- recovery_project_id
- build_output_entry_id
- action_type
- action_label
- action_status

### 3. Services and routes
Criar backend para:
- devolver sessões finais de entrega
- devolver ações finais por projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima entrega prioritária

### 4. UX note
O cockpit mobile deve manter foco em uma ação principal por output, nomes claros e zero formulários desnecessários.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
