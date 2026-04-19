# Operation Queue And Intents Plan

## Branch
- `feature/operation-queue-and-intents`

## Objetivo
Dar o próximo salto operacional ao God Mode: transformar guidance e quick actions em intenções operacionais estruturadas, com fila simples de operações, prioridade, preview e base para execução assistida.

## Meta funcional
- definir contrato de intent operacional
- definir fila de operações
- expor preview das ações antes de execução
- consolidar prioridade e origem da ação
- preparar a fase seguinte de execução assistida com aprovação quando necessário

## Blocos desta fase
### 1. Operation intent contract
Representar:
- intent_id
- source
- runtime_mode
- action_name
- priority
- requires_approval
- preview_summary
- intent_status

### 2. Operation queue service
Criar serviço para:
- devolver fila de intents
- devolver próxima ação prioritária
- devolver preview de execução

### 3. Operation queue routes
Endpoints para:
- status
- queue
- next-intent
- preview
