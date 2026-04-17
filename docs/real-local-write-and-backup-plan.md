# Real Local Write And Backup Plan

## Branch
- `feature/real-local-write-and-backup-v2`

## Objetivo
Dar ao God Mode capacidade de escrita local real em ficheiros do PC com backup físico, restore simples e validação mínima depois da aplicação.

## Meta funcional
- validar ficheiro alvo real no disco
- criar backup físico antes da escrita
- escrever conteúdo final no ficheiro real
- guardar metadados da execução
- permitir restore simples a partir do backup
- marcar resultado final da validação

## Blocos desta fase
### 1. Real write contract
Representar:
- write_run_id
- apply_run_id
- local_repo_path
- local_target_file
- resolved_target_path
- backup_file_path
- write_mode
- write_result
- restore_available
- validation_result
- final_status

### 2. Runtime service
Adicionar serviço para:
- resolver caminho alvo
- validar existência do ficheiro pai
- criar backup físico
- escrever conteúdo final real
- marcar restore disponível

### 3. Restore route
Endpoints para:
- criar execução real de escrita
- consultar execução
- listar execuções
- restaurar backup
- marcar validação final

### 4. Safety layer
- apply_run tem de estar pronto
- preview válido obrigatório
- backups obrigatórios antes da escrita real
- restore simples disponível em caso de falha

## Critérios de saída
- plano criado
- base backend para escrita real criada
- backup e restore modelados
- smoke verde da fase
