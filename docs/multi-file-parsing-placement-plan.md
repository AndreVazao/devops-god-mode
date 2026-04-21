# Multi-File Parsing Placement Phase Plan

## Branch
- `feature/multi-file-parsing-placement`

## Objetivo
Adicionar uma camada de parsing multi-ficheiro e colocação automática para o God Mode conseguir desmontar respostas gigantes com vários ficheiros misturados, identificar fronteiras prováveis, reconstruir a estrutura e colocar cada fragmento no sítio certo do projeto.

## Meta funcional
- representar lotes de parsing multi-ficheiro
- representar decisões de colocação automática por fragmento
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de parsing e placement
- preparar a fase seguinte de aplicação automática e reconciliação estrutural

## Blocos desta fase
### 1. Multi-file parsing batch contract
Representar:
- multi_file_parsing_batch_id
- source_origin
- batch_scope
- boundary_detection_mode
- parsing_status

### 2. Automatic placement decision contract
Representar:
- automatic_placement_decision_id
- probable_file_name
- probable_target_path
- placement_mode
- decision_status

### 3. Services and routes
Criar backend para:
- devolver batches de parsing multi-ficheiro
- devolver decisões de colocação automática
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador não deve ter de separar manualmente saídas gigantes no telefone. O PC faz parsing, propõe colocação e só pede confirmação curta quando houver ambiguidade real.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
