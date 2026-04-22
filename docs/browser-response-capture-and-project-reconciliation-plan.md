# Browser Response Capture And Project Reconciliation Plan

## Branch
- `feature/response-reconcile`

## Objetivo
Adicionar uma camada de captura de resposta no browser e reconciliação automática com o projeto para o God Mode conseguir ler a saída da continuação executada, separar o que é útil, classificar impacto e preparar aplicação ao projeto real.

## Meta funcional
- representar capturas de resposta por execução
- representar reconciliações de resposta com o projeto alvo
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de reconciliação
- preparar a fase seguinte de aplicação semi-automática ao projeto local

## Blocos desta fase
### 1. Browser response capture contract
Representar:
- browser_response_capture_id
- target_project
- source_provider
- source_execution_id
- capture_mode
- capture_status

### 2. Project reconciliation contract
Representar:
- project_reconciliation_id
- target_project
- reconciliation_mode
- extracted_output_kind
- reconciliation_status

### 3. Services and routes
Criar backend para:
- devolver capturas de resposta
- devolver reconciliações de projeto
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: a resposta já foi capturada, se é útil para o projeto, e qual o próximo passo para integrar essa saída.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
