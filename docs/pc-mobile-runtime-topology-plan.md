# PC Mobile Runtime Topology Plan

## Branch
- `feature/pc-mobile-topology-v2`

## Objetivo
Consolidar oficialmente o God Mode em modo PC + telemóvel, retirando a cloud do papel central e expondo uma topologia de runtime onde o PC é o cérebro e o telemóvel é o cockpit operacional.

## Meta funcional
- representar topologias de runtime suportadas
- representar políticas de cloud opcional ou desativada
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de consolidação de runtime
- preparar a fase seguinte de limpeza explícita da herança Render e Supabase do fluxo principal

## Blocos desta fase
### 1. Runtime topology contract
Representar:
- runtime_topology_id
- primary_brain_node
- remote_cockpit_node
- cloud_runtime_role
- topology_status

### 2. Cloud dependency policy contract
Representar:
- cloud_dependency_policy_id
- target_stack
- policy_mode
- cloud_providers
- policy_status

### 3. Services and routes
Criar backend para:
- devolver topologias suportadas
- devolver políticas de cloud
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: PC como cérebro, telemóvel como cockpit, cloud apenas opcional e nunca bloqueante para o fluxo principal.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
