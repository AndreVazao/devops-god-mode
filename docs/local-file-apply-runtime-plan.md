# Local File Apply Runtime Plan

## Branch
- `feature/local-file-apply-runtime`

## Objetivo
Dar o passo seguinte ao patch engine: permitir aplicação local controlada sobre ficheiros reais no PC, com preview prévio, escrita segura, backup simples e validação mínima.

## Meta funcional
- representar um alvo local de ficheiro
- escrever backup antes de aplicar
- aplicar alteração simulada ou real sobre ficheiro local
- guardar resultado da aplicação
- devolver estado final de execução
- manter bloqueio por approval quando necessário

## Blocos desta fase
### 1. Local file apply contract
Representar:
- apply_run_id
- patch_id
- preview_id
- local_repo_path
- local_target_file
- backup_file_path
- execution_mode
- apply_result
- validation_result
- final_status

### 2. Runtime service
Adicionar serviço para:
- validar caminho local
- criar backup
- aplicar conteúdo preview em modo controlado
- guardar resultado local

### 3. Runtime routes
Endpoints para:
- criar execução local
- consultar execução
- listar execuções
- marcar validação final

### 4. Safety layer
- patch com approval pendente continua bloqueado
- execução real sem preview válido deve ser recusada
- backups obrigatórios antes de escrita real

## Critérios de saída
- plano criado
- base backend para aplicação local criada
- integração com patch engine e preview criada
- smoke verde da fase
