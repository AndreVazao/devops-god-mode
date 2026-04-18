# Local PC Runtime Orchestrator Plan

## Branch
- `feature/local-pc-runtime-orchestrator`

## Objetivo
Dar o próximo salto no God Mode: preparar um orquestrador local do PC para arrancar o runtime principal, coordenar launcher + bundle desktop + handoff mobile e aproximar ainda mais o modo real `abrir e trabalhar`.

## Meta funcional
- definir perfil do orquestrador local do PC
- consolidar estado do runtime principal
- representar arranque do backend local e do cockpit local
- ligar handoff desktop/mobile ao arranque do runtime
- preparar uma sequência operacional simples para o utilizador final

## Blocos desta fase
### 1. Runtime orchestrator contract
Representar:
- orchestrator_id
- runtime_mode
- backend_runtime
- shell_runtime
- desktop_bundle
- mobile_handoff
- startup_sequence
- orchestrator_status

### 2. Runtime orchestrator service
Criar serviço para:
- devolver estado consolidado do runtime local
- devolver sequência de arranque do PC
- expor resumo do handoff mobile

### 3. Runtime orchestrator routes
Endpoints para:
- status
- runtime-state
- startup-sequence
- mobile-handoff-state

### 4. Build alignment
Preparar a fase seguinte para alinhar:
- launcher desktop
- bundle Windows
- bootstrap do PC
- bundle mobile
