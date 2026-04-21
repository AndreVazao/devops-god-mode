# Final Summary Phase Plan

## Branch
- `feature/final-summary`

## Objetivo
Adicionar uma camada final de resumo para o God Mode conseguir mostrar, de forma leve e objetiva, o estado consolidado do projeto, os outputs principais e o ponto exato do ciclo onde cada programa terminou.

## Meta funcional
- representar resumos finais por projeto
- representar linhas finais de resumo por output
- expor pacote compacto pronto para cockpit mobile
- expor próximo resumo prioritário
- preparar a fase seguinte de limpeza operacional e hardening

## Blocos desta fase
### 1. Final summary contract
Representar:
- final_summary_id
- recovery_project_id
- summary_line_count
- primary_summary_label
- summary_status

### 2. Final summary line contract
Representar:
- final_summary_line_id
- recovery_project_id
- source_record_id
- summary_type
- summary_label
- summary_state

### 3. Services and routes
Criar backend para:
- devolver resumos finais por projeto
- devolver linhas de resumo por projeto
- devolver pacote compacto pronto para cockpit
- devolver próximo resumo prioritário

### 4. UX note
O cockpit mobile deve mostrar só o essencial: projeto, output principal, estado final e próxima ação útil. Nada de paredes de texto.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
