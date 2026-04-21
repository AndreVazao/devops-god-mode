# Inter-Provider Handoff Adaptation Phase Plan

## Branch
- `feature/inter-provider-handoff-adaptation`

## Objetivo
Adicionar uma camada de handoff e adaptação inter-provider para o God Mode conseguir passar partes bloqueadas de um projeto para outra IA, recuperar a saída útil e adaptá-la ao projeto real já existente sem perder continuidade.

## Meta funcional
- representar handoffs entre providers
- representar adaptações modulares de fragmentos recuperados
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de handoff e adaptação
- preparar a fase seguinte de parsing multi-ficheiro e colocação automática

## Blocos desta fase
### 1. Inter-provider handoff contract
Representar:
- inter_provider_handoff_id
- source_provider
- target_provider
- handoff_scope
- handoff_status

### 2. Fragment adaptation contract
Representar:
- fragment_adaptation_id
- probable_project_name
- fragment_origin
- adaptation_target
- adaptation_status

### 3. Services and routes
Criar backend para:
- devolver handoffs inter-provider
- devolver adaptações de fragmentos
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: quem começou, quem continua, o que está a ser adaptado e qual o próximo passo útil. O PC faz a fusão real.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
