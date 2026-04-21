# Automatic Project Classification Phase Plan

## Branch
- `feature/automatic-project-classification`

## Objetivo
Adicionar uma camada de classificação automática de projetos para o God Mode conseguir inferir o tipo de cada repo, conversa, fragmento e continuação, agrupando tudo com mais inteligência antes de avançar para handoff e adaptação inter-provider.

## Meta funcional
- representar classificações automáticas por item
- representar decisões de agrupamento e continuidade
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de classificação
- preparar a fase seguinte de handoff inter-provider e adaptação modular

## Blocos desta fase
### 1. Automatic project classification contract
Representar:
- automatic_project_classification_id
- source_kind
- source_name
- probable_project_type
- classification_status

### 2. Project grouping decision contract
Representar:
- project_grouping_decision_id
- source_kind
- probable_project_name
- grouping_action
- confidence_band
- decision_status

### 3. Services and routes
Criar backend para:
- devolver classificações automáticas
- devolver decisões de agrupamento
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que o sistema acha que cada coisa é, o que vai juntar e o que precisa de confirmação curta.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
