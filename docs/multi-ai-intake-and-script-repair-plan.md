# Multi AI Intake And Script Repair Plan

## Branch
- `feature/multi-ai-intake-and-script-repair`

## Objetivo
Levar o God Mode para uma camada mais operacional no problema real do utilizador: trabalhar com várias IAs/conversas como fontes de contexto e conseguir detetar, diagnosticar e reparar scripts com avarias.

## Meta funcional
- representar intake multi-AI
- priorizar fontes entre várias IAs
- representar scripts com falhas e respetivo diagnóstico
- expor plano de reparação assistida
- preparar a fase seguinte de reparação e execução ainda mais automatizada

## Blocos desta fase
### 1. Multi AI source contract
Representar:
- source_id
- source_platform
- source_type
- source_priority
- intake_status
- notes

### 2. Broken script contract
Representar:
- script_issue_id
- script_id
- failure_type
- severity
- detection_reason
- repair_status

### 3. Repair step contract
Representar:
- repair_step_id
- script_issue_id
- repair_action
- expected_fix
- confirmation_required
- step_status

### 4. Services and routes
Criar backend para:
- devolver fontes multi-AI priorizadas
- devolver scripts com falhas detetadas
- devolver plano de reparação
- devolver próxima reparação prioritária

### 5. Scope
Nesta fase ainda não executa reparação invisível total.
Fecha a camada de intake multi-AI e repair planning para scripts com avarias.
