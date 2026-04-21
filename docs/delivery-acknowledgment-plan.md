# Delivery Acknowledgment Phase Plan

## Branch
- `feature/delivery-acknowledgment`

## Objetivo
Adicionar uma camada de confirmação final para o God Mode conseguir saber se o output foi entregue, visto ou descarregado, mantendo o cockpit mobile simples e com feedback objetivo sobre o estado final de cada build.

## Meta funcional
- representar confirmações finais por projeto
- representar eventos de acknowledgment por output
- expor pacote compacto para cockpit mobile
- expor próxima confirmação prioritária
- preparar a fase seguinte de histórico final e rastreio de entrega

## Blocos desta fase
### 1. Delivery acknowledgment contract
Representar:
- delivery_acknowledgment_id
- recovery_project_id
- acknowledged_output_count
- pending_ack_count
- acknowledgment_status

### 2. Delivery acknowledgment event contract
Representar:
- delivery_ack_event_id
- recovery_project_id
- final_delivery_action_id
- event_type
- event_label
- event_status

### 3. Services and routes
Criar backend para:
- devolver confirmações finais por projeto
- devolver eventos por projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima confirmação prioritária

### 4. UX note
O cockpit mobile deve mostrar só o essencial: entregue, visto, descarregado, pendente. Nada de formulários longos nem passos confusos.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
