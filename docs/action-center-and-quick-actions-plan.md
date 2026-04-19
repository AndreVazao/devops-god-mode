# Action Center And Quick Actions Plan

## Branch
- `feature/action-center-and-quick-actions`

## Objetivo
Adicionar uma camada operacional rápida ao God Mode para transformar guidance em ações práticas: centro de ações, quick actions para o runtime local, e comandos diretos para acelerar o fluxo PC + telemóvel.

## Meta funcional
- definir contrato do action center
- consolidar quick actions recomendadas
- expor ações operacionais rápidas por API
- alinhar guidance com execução prática
- aproximar o God Mode de um assistente operacional mais útil no dia a dia

## Blocos desta fase
### 1. Action center contract
Representar:
- action_center_id
- runtime_mode
- quick_actions
- blocked_actions
- recommended_action
- action_center_status

### 2. Action center service
Criar serviço para:
- devolver centro de ações consolidado
- devolver quick actions disponíveis
- devolver ação recomendada principal

### 3. Action center routes
Endpoints para:
- status
- summary
- quick-actions
- recommended-action
