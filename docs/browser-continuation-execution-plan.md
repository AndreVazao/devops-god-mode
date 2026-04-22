# Browser Continuation Execution Plan

## Branch
- `feature/browser-cont-exec`

## Objetivo
Adicionar uma camada de execução semi-automática em browser para o God Mode conseguir aplicar prompts de continuação preparados, abrir a conversa certa, escolher o provider certo e avançar o projeto com menos intervenção manual.

## Meta funcional
- representar sessões de execução em browser por projeto
- representar prompts de continuação prontos para execução
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de execução em browser
- preparar a fase seguinte de captura de resposta e reconciliação automática com o projeto

## Blocos desta fase
### 1. Browser continuation execution contract
Representar:
- browser_continuation_execution_id
- target_project
- target_provider
- execution_mode
- prepared_prompt_id
- execution_status

### 2. Browser continuation prompt contract
Representar:
- browser_continuation_prompt_id
- target_project
- target_provider
- prompt_goal
- prompt_readiness
- prompt_status

### 3. Services and routes
Criar backend para:
- devolver execuções em browser preparadas
- devolver prompts de continuação prontos
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: qual projeto vai continuar, em que provider, com que prompt e se já está pronto para abrir e seguir.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
