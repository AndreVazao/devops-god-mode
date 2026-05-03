# AI Provider Router

## Objetivo

Escolher o provider IA mais adequado para cada tarefa do God Mode, com score, fallback, segurança e política de uso.

## Providers iniciais

- `chatgpt`
- `gemini`
- `deepseek`
- `grok`
- `ollama`
- `claude_code_or_codex_local`

## Regra principal

O Provider Router recomenda qual IA usar. Ele não automatiza web UI nesta fase.

Fluxo correto:

```txt
Goal Planner
→ Agent Roles
→ AI Handoff Security Guard
→ AI Provider Router
→ AI Handoff Trace
→ execução / PR / build / memória
```

## Política

- ChatGPT é provider principal por defeito para PT, planeamento, arquitetura, debugging e revisão.
- Ollama/local é preferido para contexto sensível, triagem privada, resumo local e modo offline.
- DeepSeek é fallback forte para código quando o provider principal recusa ou não conclui.
- Gemini é forte para contexto grande, pesquisa, multimodal e cross-check.
- Grok é útil para segunda opinião, ideação e cross-check rápido.
- Todo handoff passa pelo AI Handoff Security Guard antes de enviar contexto.
- Se houver secrets, providers externos ficam bloqueados até sanitização.

## Endpoints

- `GET/POST /api/ai-provider-router/status`
- `GET/POST /api/ai-provider-router/panel`
- `GET/POST /api/ai-provider-router/rules`
- `GET /api/ai-provider-router/providers`
- `GET /api/ai-provider-router/policy`
- `POST /api/ai-provider-router/route`
- `GET/POST /api/ai-provider-router/package`

## Exemplo payload

```json
{
  "goal": "Gerar código para corrigir o workflow e validar build",
  "task_tags": ["code_generation", "debugging"],
  "context": "Workflow falhou no GitHub Actions.",
  "sensitive": false,
  "needs_code": true,
  "needs_large_context": false,
  "needs_multimodal": false,
  "primary_failed": false,
  "provider_availability": {
    "chatgpt": true,
    "deepseek": true,
    "gemini": true,
    "grok": true,
    "ollama": true
  }
}
```

## Segurança

- O router não envia contexto para providers.
- O router só escolhe e ordena providers.
- O contexto deve passar pelo Security Guard antes do handoff.
- Providers externos só recebem contexto sanitizado quando houver risco.

## Próxima evolução

- Persistir estatísticas reais de sucesso/falha por provider.
- Aprender com resultados do AI Handoff Trace.
- Integrar disponibilidade real via browser/CLI/local APIs.
- Ligar com execução automática quando o utilizador aprovar.
