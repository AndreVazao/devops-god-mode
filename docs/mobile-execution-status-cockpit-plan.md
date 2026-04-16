# Mobile Execution Status Cockpit Plan

## Branch
- `feature/mobile-execution-status-cockpit`

## Objetivo
Mostrar no cockpit móvel não só approvals pendentes, mas também o estado das execuções sensíveis ligadas a esses approvals.

## Meta funcional
- listar execuções bloqueadas por approval
- mostrar estado atual de cada execução
- permitir atualizar o estado sem sair do cockpit
- ligar visualmente approval e execução quando existir associação

## Estados alvo
- `waiting_for_approval`
- `approved_to_continue`
- `rejected`
- `needs_changes`

## Blocos desta fase
### 1. Execution status panel
Adicionar ao mobile shell:
- contador de execuções monitorizadas
- cards com resumo, repo, path e estado
- refresh rápido

### 2. Sync action
Cada execução deve poder fazer sync com o approval broker para refletir o estado mais recente.

### 3. Feedback curto
Mostrar no cockpit um resumo rápido do que mudou depois do sync.

## Critérios de saída
- execuções visíveis no telemóvel
- sync manual funcional
- estado refletido no cockpit
- smoke verde da fase
