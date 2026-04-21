# Initial Inventory Project Graph Phase Plan

## Branch
- `feature/initial-inventory-project-graph-v2`

## Objetivo
Adicionar uma camada de inventário inicial e grafo de projeto para o God Mode conseguir mapear logo no arranque repos, conversas, providers, fragmentos de projeto e relações prováveis, antes de iniciar operação pesada.

## Meta funcional
- representar inventários iniciais por fonte
- representar nós e ligações do grafo de projeto
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de inventário
- preparar a fase seguinte de classificação automática e continuidade inter-provider

## Blocos desta fase
### 1. Initial inventory source contract
Representar:
- initial_inventory_id
- source_type
- source_priority
- inventory_scope
- inventory_status

### 2. Project graph link contract
Representar:
- project_graph_link_id
- source_type
- source_name
- probable_project_name
- link_role
- link_status

### 3. Services and routes
Criar backend para:
- devolver fontes de inventário inicial
- devolver ligações do grafo de projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que já foi descoberto, o que está a ser agrupado e qual o próximo passo útil. O PC faz o inventário pesado.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
