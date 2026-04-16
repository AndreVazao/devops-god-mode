# Execution Waits For Approval Plan

## Branch
- `feature/execution-waits-for-approval`

## Objetivo
Ligar o approval broker ao fluxo real de execução sensível, para que certas ações só avancem depois da resposta do utilizador no cockpit móvel.

## Meta funcional
- backend cria approval quando a ação é sensível
- execução fica em estado `waiting_for_approval`
- cockpit móvel mostra o pedido pendente
- utilizador responde `OK`, `ALTERA` ou `REJEITA`
- backend só continua quando a resposta permitir

## Casos alvo iniciais
### 1. Ações Git sensíveis
- branch creation com impacto relevante
- PR execution com alteração estrutural
- replace file em ficheiros críticos

### 2. Ações de conectores/integrações
- pedidos de permissão
- ações externas com risco médio/alto

## Blocos desta fase
### 1. Approval-gated action contract
Criar estrutura para representar:
- ação pedida
- approval associado
- estado atual
- resultado após aprovação

### 2. Waiting state
Adicionar estado explícito de espera:
- `pending`
- `waiting_for_approval`
- `approved_to_continue`
- `rejected`
- `needs_changes`

### 3. Polling simples inicial
O backend pode começar com polling simples ao approval broker antes de continuar a execução.

### 4. Feedback ao cockpit
O mobile shell deve ver não só o approval, mas também o estado resumido da execução associada.

## Critérios de saída
- branch limpa
- pelo menos um fluxo sensível fica realmente bloqueado até aprovação
- estado de espera visível
- smoke verde da fase
