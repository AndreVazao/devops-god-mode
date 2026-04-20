# Driving Mode Voice First Plan

## Branch
- `feature/driving-mode-voice-first`

## Objetivo
Dar o próximo salto ao God Mode: transformar o cockpit móvel numa superfície curta, segura e orientada por voz para uso com atenção reduzida, com resumos objetivos, confirmações rápidas e bloqueio de ações de risco.

## Meta funcional
- definir resumo de driving mode seguro
- definir prompts curtos de voz e confirmações rápidas
- expor ações seguras e ações bloqueadas por risco
- reduzir a superfície de interação a poucos toques ou respostas curtas
- preparar a fase seguinte de automação orientada por contexto real

## Blocos desta fase
### 1. Driving prompt contract
Representar:
- prompt_id
- prompt_type
- spoken_text
- expected_reply_mode
- priority
- prompt_status

### 2. Driving action guard contract
Representar:
- guard_id
- action_id
- risk_level
- requires_voice_confirmation
- allowed_in_safe_mode
- guard_status

### 3. Services and routes
Criar backend para:
- devolver resumo curto do driving mode seguro
- devolver prompts de voz prioritários
- devolver ações seguras e bloqueadas
- confirmar uma ação curta do cockpit
- devolver próxima ação apropriada para modo seguro

### 4. Scope
Nesta fase ainda não integra STT/TTS real.
Fecha a camada lógica de modo seguro e voice-first para uso resumido e protegido.
