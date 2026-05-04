# Provider Outcome Learning

## Objetivo

A Phase 171 adiciona aprendizagem sobre resultados dos providers IA.

O God Mode passa a conseguir guardar metadados seguros de outcome e gerar recomendações para o AI Provider Router:

```txt
provider usado
→ task tags
→ outcome/qualidade/latência/custo
→ scorecard
→ hints para router
→ simulação de rota aprendida
```

## O que guarda

Guarda apenas metadados sanitizados:

- `provider_id`
- `task_tags`
- `outcome`
- `quality_score`
- `latency_ms`
- `cost_hint`
- `failure_reason`
- `sensitive`
- `requires_safety_guard`
- `operator_rating`
- `notes_summary` sanitizado

## O que nunca guarda

- prompt completo bruto;
- resposta completa bruta;
- tokens;
- passwords/senhas;
- cookies;
- private keys;
- API keys;
- dumps privados de repo;
- headers Authorization/Bearer.

## Segurança

A aprendizagem nunca pode recomendar fallback para contornar:

- bloqueios de segurança;
- recusa política;
- operador negou aprovação;
- segredo detetado;
- contexto sensível não sanitizado.

Providers externos continuam dependentes do `AI Handoff Security Guard`.

## Endpoints

- `GET/POST /api/provider-outcome-learning/status`
- `GET/POST /api/provider-outcome-learning/panel`
- `GET/POST /api/provider-outcome-learning/policy`
- `GET/POST /api/provider-outcome-learning/rules`
- `POST /api/provider-outcome-learning/record-outcome`
- `POST /api/provider-outcome-learning/scorecard`
- `POST /api/provider-outcome-learning/router-hints`
- `POST /api/provider-outcome-learning/simulate-route`
- `GET/POST /api/provider-outcome-learning/latest`
- `GET/POST /api/provider-outcome-learning/package`

## Relação com AI Provider Router

A Phase 171 não altera destrutivamente os pesos base do router.

Ela gera recomendações explicáveis em modo `advisory_v1`:

- boost quando provider tem sucesso consistente numa task;
- neutral quando evidência ainda é fraca;
- deprioritize quando falha muito;
- não boost quando há penalidade de segurança.

## Futuro

Fases futuras podem:

- aplicar pesos aprendidos automaticamente com aprovação;
- cruzar outcomes com playbooks/pipelines;
- medir custo real quando houver integração de API;
- ligar provider outcome ao Home/App Control Surface.
