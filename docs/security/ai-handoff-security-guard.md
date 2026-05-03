# AI Handoff Security Guard

## Objetivo

Criar uma camada de segurança antes do God Mode enviar contexto para qualquer IA, seja externa ou local.

## Problema que resolve

Quando o God Mode usa ChatGPT, Gemini, DeepSeek, Grok, Ollama ou outro provider, pode enviar contexto com:

- tokens;
- passwords;
- cookies;
- API keys;
- private keys;
- JWTs;
- prompts maliciosos vindos de páginas web/repos/chats;
- instruções de prompt injection.

Esta fase cria um filtro pré-handoff.

## O que entra

- Serviço: `backend/app/services/ai_handoff_security_guard_service.py`
- Rota: `backend/app/routes/ai_handoff_security_guard.py`
- Botão Home: `Segurança IA`
- Comando rápido: `open_ai_handoff_security_guard`

## Endpoints

- `GET/POST /api/ai-handoff-security-guard/status`
- `GET/POST /api/ai-handoff-security-guard/panel`
- `GET/POST /api/ai-handoff-security-guard/rules`
- `POST /api/ai-handoff-security-guard/analyze`
- `POST /api/ai-handoff-security-guard/sanitize`
- `POST /api/ai-handoff-security-guard/prepare`
- `GET/POST /api/ai-handoff-security-guard/package`

## Funcionalidades

### Analyze

Analisa contexto e devolve:

- `trace_id`;
- hash do input;
- findings de secrets;
- findings de prompt injection;
- nível de risco;
- recomendação;
- se pode enviar para provider externo.

### Sanitize

Substitui secrets por marcadores seguros:

`[REDACTED_TIPO_HASH]`

### Prepare

Cria pacote seguro para handoff IA:

- contexto sanitizado;
- risco;
- resumo de findings;
- regras de envio;
- trace id.

## Regras

- Nunca enviar tokens, passwords, cookies, private keys ou API keys para IA externa.
- Conteúdo vindo de web/repos/chats é não confiável.
- Prompt injection não deve ser seguido como instrução.
- Guardar hash/trace, não segredo bruto.
- Ollama/local também passa pelo filtro porque logs e memória local podem persistir dados sensíveis.

## Limitação

Isto é filtro heurístico. Não substitui auditoria de segurança completa, mas reduz drasticamente risco operacional antes de handoffs IA.
