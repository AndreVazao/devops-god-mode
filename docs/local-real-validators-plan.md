# Local Real Validators Plan

## Branch
- `feature/local-real-validators`

## Objetivo
Dar ao God Mode uma camada de validadores locais reais para confirmar que a escrita no PC ficou correta antes de fechar a execução como válida.

## Meta funcional
- validar existência real do ficheiro final
- validar existência real do backup
- validar conteúdo final não vazio
- validar se o conteúdo final corresponde ao preview esperado
- guardar resultado detalhado de cada check
- devolver estado final consolidado

## Blocos desta fase
### 1. Validation contract
Representar:
- validator_run_id
- write_run_id
- validator_mode
- checks
- expected_preview_excerpt
- observed_file_excerpt
- checks_result
- final_status

### 2. Validator service
Adicionar serviço para:
- criar corrida de validação
- guardar checks executados
- marcar passed/failed por check
- consolidar resultado final

### 3. Validator routes
Endpoints para:
- criar validação
- listar validações
- consultar validação
- marcar resultado observado
- fechar validação

### 4. Integration
- usar `write_run_id` de `real_local_write`
- aproveitar `preview_after` quando existir
- deixar base pronta para futuros validadores reais no runtime local do PC

## Critérios de saída
- plano criado
- contrato criado
- service backend criado
- routes criadas
- smoke verde da fase
