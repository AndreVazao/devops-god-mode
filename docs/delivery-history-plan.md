# Delivery History Phase Plan

## Branch
- `feature/delivery-history-v2`

## Objetivo
Adicionar uma camada de histórico final para o God Mode conseguir manter rastreio simples e leve dos outputs entregues, vistos e descarregados, sem poluir o cockpit mobile.

## Meta funcional
- representar históricos finais por projeto
- representar registos históricos por output
- expor pacote compacto para consulta rápida
- expor próxima revisão prioritária
- preparar a fase seguinte de resumo final e limpeza operacional

## Blocos desta fase
### 1. Delivery history contract
Representar:
- delivery_history_id
- recovery_project_id
- total_history_items
- latest_delivery_state
- history_status

### 2. Delivery history record contract
Representar:
- delivery_history_record_id
- recovery_project_id
- delivery_ack_event_id
- record_type
- record_label
- record_status

### 3. Services and routes
Criar backend para:
- devolver históricos finais por projeto
- devolver registos históricos por projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima revisão prioritária

### 4. UX note
O cockpit mobile deve mostrar histórico em formato curto, claro e objetivo, sem listas pesadas nem excesso de detalhe.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
