# Provider Prompt Broadcast + Pane Manifest Runtime

## Objetivo

A Phase 190 implementa o runtime nativo inspirado no `smol-ai/GodMode`, sem adicionar dependência externa.

O God Mode passa a criar perfis de panes/providers, gerar planos de broadcast e importar respostas de providers para o Conversation Requirement Ledger.

## Endpoint principal

```txt
/api/provider-prompt-broadcast-runtime/package
```

## Endpoints

- `/api/provider-prompt-broadcast-runtime/status`
- `/api/provider-prompt-broadcast-runtime/policy`
- `/api/provider-prompt-broadcast-runtime/default-pane-profile`
- `/api/provider-prompt-broadcast-runtime/create-pane-profile`
- `/api/provider-prompt-broadcast-runtime/create-broadcast-plan`
- `/api/provider-prompt-broadcast-runtime/import-provider-response`
- `/api/provider-prompt-broadcast-runtime/compare-responses`
- `/api/provider-prompt-broadcast-runtime/plans`
- `/api/provider-prompt-broadcast-runtime/package`

## O que esta fase faz

- Cria pane profile multi-IA.
- Permite selecionar providers para uma missão.
- Preserva pedido original do Oner.
- Opcionalmente aplica prompt critic local e determinístico.
- Gera provider jobs.
- Importa respostas manualmente/futuro runtime.
- Regista respostas no ledger como `ai_response`.
- Compara respostas e aponta scripts/gaps para review.

## O que esta fase ainda não faz

- Não automatiza input real no browser.
- Não guarda credenciais.
- Não guarda cookies/tokens.
- Não aplica scripts.
- Não faz decisões automáticas com base numa resposta de IA.

## Regra crítica

Resposta de provider é `ai_response`, não decisão.

A decisão continua a exigir revisão/aceitação do Oner e evidência real quando aplicável.

## Segurança

- Browser automation fica desativado nesta fase.
- Credential entry exige fase/gate futuro.
- Scripts extraídos exigem reconciliation antes de aplicar.
- Repo write/deploy/merge/release continuam protegidos por gates.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 189 deve ser apagado. Fica só:

- `.github/workflows/phase190-provider-prompt-broadcast-runtime-smoke.yml`

Além dos workflows globais/builds.
