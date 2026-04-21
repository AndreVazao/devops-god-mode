# Platform Failure Triage And Continuation Plan

## Branch
- `feature/platform-failure-triage`

## Objetivo
Adicionar uma camada de triagem de falhas de plataforma para o God Mode conseguir distinguir erros bloqueantes de erros não bloqueantes, continuar o fluxo principal quando for seguro e deixar a correção detalhada para depois.

## Meta funcional
- representar falhas de checks e plataformas externas
- classificar impacto real no avanço do projeto
- expor decisão de continuação ou bloqueio por API
- expor pacote compacto pronto para cockpit mobile
- preparar a fase seguinte de continuação autónoma orientada por projeto

## Blocos desta fase
### 1. Platform failure contract
Representar:
- platform_failure_id
- platform_name
- failure_type
- impact_level
- continuation_policy
- failure_status

### 2. Continuation decision contract
Representar:
- continuation_decision_id
- target_project
- decision_type
- decision_reason
- requires_immediate_fix
- decision_status

### 3. Services and routes
Criar backend para:
- devolver falhas classificadas
- devolver decisões de continuação
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve ver só o essencial: o que falhou, se bloqueia ou não, e se o sistema pode seguir em frente já.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
