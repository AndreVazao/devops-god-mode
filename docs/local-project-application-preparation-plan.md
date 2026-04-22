# Local Project Application Preparation Plan

## Branch
- `feature/local-apply-prep`

## Objetivo
Adicionar uma camada de preparação de aplicação local ao projeto para o God Mode conseguir transformar a reconciliação anterior num plano aplicável ao PC, separando ficheiros, patches, riscos e ordem de aplicação antes de mexer no projeto real.

## Meta funcional
- representar preparações de aplicação local por projeto
- representar itens aplicáveis ao projeto local
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de aplicação local
- preparar a fase seguinte de aplicação semi-automática ao projeto real com verify e rollback

## Blocos desta fase
### 1. Local application preparation contract
Representar:
- local_application_preparation_id
- target_project
- preparation_mode
- prepared_output_kind
- preparation_status

### 2. Local application item contract
Representar:
- local_application_item_id
- target_project
- item_kind
- target_path
- apply_mode
- item_status

### 3. Services and routes
Criar backend para:
- devolver preparações locais por projeto
- devolver itens aplicáveis ao projeto local
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que está pronto para aplicar, onde vai entrar no projeto e se o item é ficheiro completo, patch ou ação operacional.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
