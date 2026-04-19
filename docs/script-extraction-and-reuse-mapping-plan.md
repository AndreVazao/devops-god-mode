# Script Extraction And Reuse Mapping Plan

## Branch
- `feature/script-extraction-and-reuse-mapping`

## Objetivo
Dar o próximo salto ao God Mode: passar de inventário de conversas para extração estruturada de scripts, mapeamento de reaproveitamento e base para adaptação entre projetos sem depender sempre de reabrir chats antigos.

## Meta funcional
- definir contrato de script extraído
- definir contrato de reuse map
- expor scripts candidatos por projeto e tags
- expor ligações entre conversa, script e projeto alvo
- preparar a fase seguinte de adaptação assistida

## Blocos desta fase
### 1. Extracted script contract
Representar:
- script_id
- conversation_id
- inferred_filename
- language
- project_key
- tags
- reuse_score
- extraction_status

### 2. Reuse mapping contract
Representar:
- reuse_map_id
- source_project
- target_project
- source_scripts
- adaptation_hint
- reuse_status

### 3. Services and routes
Criar backend para:
- devolver scripts extraídos
- devolver agrupamento por projeto
- devolver reuse maps
- devolver melhores candidatos a adaptação

### 4. Scope
Nesta fase ainda não executa adaptação automática real.
Fecha a base lógica para extração e reaproveitamento estruturado.
