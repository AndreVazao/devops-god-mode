# Context Aware Orchestration Layer Plan

## Branch
- `feature/context-aware-automation-layer`

## Objetivo
Dar o próximo salto ao God Mode: passar de superfícies operacionais separadas para uma camada orientada por contexto, capaz de decidir quando puxar intake, quando avançar browser control, quando adaptar, quando pedir confirmação e quando apenas esperar.

## Meta funcional
- definir contexto operacional consolidado
- decidir próxima estratégia com base em runtime, browser control, intake, adaptação e driving mode
- expor decisão recomendada e respetiva razão
- separar ações seguras de ações que exigem confirmação
- preparar a fase seguinte de execução contextual mais profunda

## Blocos desta fase
### 1. Context decision contract
Representar:
- decision_id
- decision_type
- target_mode
- target_id
- confidence_score
- requires_confirmation
- decision_reason
- decision_status

### 2. Orchestration lane contract
Representar:
- lane_id
- lane_type
- priority
- source_modes
- lane_summary
- lane_status

### 3. Services and routes
Criar backend para:
- devolver contexto operacional consolidado
- devolver lanes priorizadas
- devolver decisão contextual seguinte
- devolver ações seguras e ações que exigem confirmação
- aplicar uma decisão contextual assistida

### 4. Scope
Nesta fase ainda não executa automação invisível contínua.
Fecha a camada de decisão contextual que vai orientar as próximas fases de execução real.
