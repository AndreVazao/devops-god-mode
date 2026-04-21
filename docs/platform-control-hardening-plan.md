# Platform Control Hardening Phase Plan

## Branch
- `feature/platform-control-hardening`

## Objetivo
Adicionar uma camada de controlo de plataformas para o God Mode conseguir consolidar, num ponto único, o estado operacional de GitHub, Vercel, Render e Supabase, mantendo o cockpit leve e preparando ligações reais a cada plataforma sem espalhar decisões pela interface.

## Meta funcional
- representar control surfaces por plataforma
- representar ações prioritárias por plataforma
- expor pacote compacto de controlo para cockpit mobile
- expor próxima ação operacional prioritária
- preparar a fase seguinte de ligações reais por plataforma

## Blocos desta fase
### 1. Platform control surface contract
Representar:
- platform_control_id
- platform_name
- control_scope
- readiness_status
- priority_action_count

### 2. Platform control action contract
Representar:
- platform_control_action_id
- platform_name
- action_type
- action_label
- action_status
- capability_state

### 3. Services and routes
Criar backend para:
- devolver control surfaces por plataforma
- devolver ações por plataforma
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O cockpit mobile deve continuar muito leve. Esta fase deve mostrar só plataforma, estado, próxima ação e capacidade disponível. Nada de formulários longos.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
