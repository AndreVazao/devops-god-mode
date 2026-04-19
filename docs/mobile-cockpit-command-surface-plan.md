# Mobile Cockpit Command Surface Plan

## Branch
- `feature/mobile-cockpit-command-surface`

## Objetivo
Dar o próximo salto ao God Mode: transformar o telemóvel num cockpit operacional forte, capaz de ver o estado consolidado do sistema, receber a próxima ação recomendada e comandar o browser control, intake e fila operacional do PC.

## Meta funcional
- definir superfície de comando mobile
- consolidar estado crítico do runtime, browser control e operation queue
- expor quick actions seguras para avançar o trabalho no PC
- expor próxima ação prioritária para uso rápido em mobilidade
- preparar a fase seguinte de modo driving/voice-first

## Blocos desta fase
### 1. Mobile cockpit card contract
Representar:
- card_id
- card_type
- title
- summary
- priority
- source_mode
- status

### 2. Mobile quick action contract
Representar:
- action_id
- action_type
- label
- target_id
- requires_confirmation
- action_status

### 3. Services and routes
Criar backend para:
- devolver cockpit summary consolidado
- devolver cards operacionais do telemóvel
- devolver quick actions disponíveis
- avançar uma quick action assistida
- devolver próxima ação crítica do cockpit

### 4. Scope
Nesta fase ainda não inclui voz nem automação invisível total.
Fecha a superfície de comando móvel para operar o cérebro no PC com poucos toques.
