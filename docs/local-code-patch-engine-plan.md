# Local Code Patch Engine Plan

## Branch
- `feature/local-code-patch-engine`

## Objetivo
Dar ao God Mode uma camada local capaz de ler ficheiros de projeto, receber instruções ou snippets, propor patches contextuais e aplicar alterações de baixo risco com validação e approval quando necessário.

## Meta funcional
- representar um pedido de patch local
- guardar ficheiro alvo, estratégia e risco
- gerar proposta de patch estruturada
- marcar ações de baixo risco como auto-aplicáveis
- marcar ações de médio/alto risco para approval
- preparar base para diff, validação e memória futura

## Blocos desta fase
### 1. Patch contract
Criar contrato para:
- patch_id
- repo_full_name
- target_path
- instruction
- patch_strategy
- risk_level
- approval_required
- status
- proposed_changes
- validation_plan

### 2. Patch engine service
Guardar pedidos de patch localmente com persistência simples.

### 3. Patch engine routes
Endpoints para:
- criar pedido de patch
- listar patches
- consultar patch
- sincronizar patch com approval broker quando necessário

### 4. Approval integration
- baixo risco pode nascer como `ready_to_apply`
- médio/alto risco cria approval e fica `waiting_for_approval`

## Critérios de saída
- contrato criado
- service backend criado
- routes backend criadas
- integração base com approval broker
- smoke verde da fase
