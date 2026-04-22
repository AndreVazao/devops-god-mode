# DevOps God Mode

Centro de controlo DevOps privado, com cérebro principal no PC e operação móvel-first.

## Objetivo

Transformar o God Mode num sistema operacional pessoal para:
- correr o cérebro principal no PC de casa
- usar o telemóvel como cockpit principal
- organizar conversas, scripts e projetos vindos do browser
- decidir o que continuar, adaptar, reaproveitar ou apenas arquivar
- comandar browser control, intake e execução assistida a partir do cockpit móvel

## Pivot estratégico

A foundation inicial passou por uma fase com:
- Supabase como base de dados
- Render como backend online
- Vercel como deploy de testes

Essa fase deixou de ser a direção principal.
O projeto está agora consolidado como **local-first**, com foco em:
- PC como cérebro principal
- telefone como cockpit principal
- operação pensada para uso na rua e em condução assistida
- redução de dependências cloud antigas que já não servem o fluxo real

## Arquitetura atual

### PC como cérebro principal
- backend FastAPI como núcleo operacional
- runtime local e handoff PC + telemóvel
- escrita local, validação e rollback
- packaging desktop Windows com launcher e bundle de onboarding

### Telemóvel como cockpit principal
- mobile cockpit command surface
- driving mode seguro e voice-first
- quick actions e próxima ação crítica
- controlo assistido do browser e do intake

### Camada de conhecimento e reaproveitamento
- chat inventory
- script extraction and reuse mapping
- adaptation planner
- conversation organization intelligence
- context aware orchestration

## Estado atual

O `main` já não está em bootstrap inicial.
O sistema já expõe múltiplas APIs operacionais para:
- runtime supervision
- browser intake e browser control
- operação por cockpit móvel
- driving mode seguro
- orquestração contextual
- adaptação e reaproveitamento de scripts

## Nota sobre foundations antigas

Algumas peças Android e de packaging inicial continuam na repo como foundation histórica/placeholder e ainda não representam o fluxo final real. A consolidação e limpeza dessas peças está mapeada em `docs/repo-consolidation-and-legacy-mapping.md`.

## Nota sobre legado cloud

Supabase, Render e Vercel passaram a legado arquitetural.
A repo deve tratá-los como contexto histórico a remover, arquivar ou isolar, nunca como destino principal da stack.
