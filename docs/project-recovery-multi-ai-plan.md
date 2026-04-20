# Project Recovery Across Multi AI Sources Plan

## Branch
- `feature/project-recovery-v2`

## Objetivo
Levar o God Mode para a recuperação real de projetos espalhados por várias IAs e conversas antigas, transformando fontes distribuídas em projetos reconstruíveis com scripts, contexto e árvore inicial de repo.

## Meta funcional
- representar projetos recuperáveis
- ligar projetos a múltiplas fontes AI e conversas
- representar scripts recuperáveis por projeto
- expor blueprint inicial de repo reconstruída
- preparar a fase seguinte de recuperação assistida com escrita no browser e continuação de projeto

## Blocos desta fase
### 1. Recoverable project contract
Representar:
- recovery_project_id
- project_key
- project_name
- source_count
- recoverable_script_count
- recovery_status
- recovery_summary

### 2. Project recovery source contract
Representar:
- recovery_source_id
- recovery_project_id
- source_platform
- conversation_hint
- source_role
- recovery_priority
- source_status

### 3. Recoverable script contract
Representar:
- recoverable_script_id
- recovery_project_id
- script_id
- script_role
- source_platform
- recovery_confidence
- script_status

### 4. Services and routes
Criar backend para:
- devolver projetos recuperáveis
- devolver fontes por projeto
- devolver scripts recuperáveis por projeto
- devolver blueprint de repo por projeto
- devolver próxima recuperação prioritária

### 5. Scope
Nesta fase ainda não faz escrita automática no browser.
Fecha a camada de recuperação de projetos distribuídos por várias IAs e conversas antigas.
