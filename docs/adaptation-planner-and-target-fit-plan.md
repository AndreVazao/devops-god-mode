# Adaptation Planner And Target Fit Plan

## Branch
- `feature/adaptation-planner-and-target-fit`

## Objetivo
Dar o próximo salto ao God Mode: passar de extração e reaproveitamento para planeamento de adaptação, avaliação de compatibilidade com o projeto alvo e preparação de mudanças assistidas antes da execução.

## Meta funcional
- definir contrato de adaptation plan
- definir avaliação de target fit
- expor etapas de adaptação por script e por projeto
- priorizar scripts mais compatíveis com o alvo
- preparar a fase seguinte de aplicação assistida

## Blocos desta fase
### 1. Adaptation plan contract
Representar:
- adaptation_id
- source_script_id
- target_project
- compatibility_score
- required_changes
- adaptation_steps
- adaptation_status

### 2. Target fit contract
Representar:
- target_fit_id
- target_project
- candidate_scripts
- fit_summary
- blockers
- target_fit_status

### 3. Services and routes
Criar backend para:
- devolver adaptation plans
- devolver target fit summaries
- devolver melhores planos por projeto alvo
- devolver blockers e passos sugeridos

### 4. Scope
Nesta fase ainda não aplica mudanças reais no código.
Fecha a base lógica para planeamento de adaptação assistida.
