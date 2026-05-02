# Ruflo Research Lab Adapter

## Decisão

Ruflo deve ser estudado como laboratório externo controlado, não como dependência central do God Mode.

## Repos

- God Mode: `AndreVazao/devops-god-mode`
- Laboratório: `AndreVazao/godmode-ruflo-lab`
- Upstream: `ruvnet/ruflo`

## Upstream

Ruflo é um projeto MIT focado em orquestração multi-agent, swarms, MCP, memória vetorial, provider routing, goal planning, local LLM/Ollama, federation e segurança.

## O que foi feito no lab

No repo `AndreVazao/godmode-ruflo-lab`:

- README expandido;
- workflow `.github/workflows/sync-upstream-ruflo.yml` criado;
- plano `docs/RUFLO_TO_GODMODE_EXTRACTION_PLAN.md` criado;
- branch prevista `upstream-ruflo` para espelho automático do upstream.

## O que foi feito no God Mode

- Serviço: `backend/app/services/ruflo_research_lab_service.py`
- Rota: `backend/app/routes/ruflo_research_lab.py`
- Home atualizada com botão `Ruflo Lab`
- Ecossistema atualizado para reconhecer `AndreVazao/godmode-ruflo-lab`

## Endpoints

- `GET/POST /api/ruflo-research-lab/status`
- `GET/POST /api/ruflo-research-lab/panel`
- `GET/POST /api/ruflo-research-lab/policy`
- `GET/POST /api/ruflo-research-lab/mapping`
- `GET/POST /api/ruflo-research-lab/extraction-plan`
- `GET/POST /api/ruflo-research-lab/reusable-registry-seed`
- `GET/POST /api/ruflo-research-lab/package`

## Política

- Não copiar módulos Ruflo para o God Mode sem análise.
- Manter licença MIT e atribuição se houver código derivado.
- Preferir implementação nativa/adaptada no God Mode.
- Registar padrões úteis no Reusable Code Registry.
- Não adicionar dependências Node grandes sem necessidade real.
- Cada extração deve ser uma fase/PR isolada.

## Primeiro lote recomendado

1. Goal Planner God Mode.
2. AI Handoff Security Guard.
3. MCP Compatibility Map.
4. Agent Roles Registry.
5. Provider Router scoring/fallback.

## Estado operacional

O adaptador não executa Ruflo. Ele regista o lab, expõe política, mapeamento e plano de extração para o God Mode decidir o que aproveitar.
