# Local Project Application Execution Plan

## Branch
- `feature/local-apply-exec`

## Objetivo
Adicionar uma camada de aplicação semi-automática ao projeto local para o God Mode conseguir pegar nos itens preparados, aplicar no PC de forma controlada e manter verify e rollback como checkpoints explícitos.

## Meta funcional
- representar execuções de aplicação local por projeto
- representar resultados de verify e rollback por execução
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de aplicação local
- preparar a fase seguinte de remoção definitiva da dependência histórica de cloud runtime no fluxo principal

## Blocos desta fase
### 1. Local application execution contract
Representar:
- local_application_execution_id
- target_project
- execution_mode
- prepared_item_count
- execution_status

### 2. Local apply safeguard contract
Representar:
- local_apply_safeguard_id
- target_project
- safeguard_type
- safeguard_result
- safeguard_status

### 3. Services and routes
Criar backend para:
- devolver execuções de aplicação local
- devolver safeguards de verify e rollback
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que vai ser aplicado agora, se o verify passou e se existe rollback pronto caso algo corra mal.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
