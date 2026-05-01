# DevOps God Mode

Centro de controlo DevOps privado, com cérebro principal no PC e operação móvel-first.

## Objetivo

Transformar o God Mode num sistema operacional pessoal para:
- correr o cérebro principal no PC de casa;
- usar o telemóvel como cockpit principal;
- organizar conversas, scripts e projetos vindos do browser;
- decidir o que continuar, adaptar, reaproveitar ou apenas arquivar;
- comandar browser control, intake e execução assistida a partir do cockpit móvel;
- mexer em repos/programas com plano, preview, aprovação, rollback e registo de memória.

## Pivot estratégico

A foundation inicial passou por uma fase com:
- Supabase como base de dados;
- Render como backend online;
- Vercel como deploy de testes.

Essa fase deixou de ser a direção principal.
O projeto está agora consolidado como **local-first**, com foco em:
- PC como cérebro principal;
- telefone como cockpit principal;
- operação pensada para uso na rua e em condução assistida;
- redução de dependências cloud antigas que já não servem o fluxo real.

## Arquitetura atual

### PC como cérebro principal
- backend FastAPI como núcleo operacional;
- runtime local e handoff PC + telemóvel;
- escrita local, validação e rollback;
- packaging desktop Windows com launcher e bundle de onboarding.

### Telemóvel como cockpit principal
- mobile cockpit command surface;
- driving mode seguro e voice-first;
- quick actions e próxima ação crítica;
- controlo assistido do browser e do intake.

### Camada de conhecimento e reaproveitamento
- chat inventory;
- script extraction and reuse mapping;
- adaptation planner;
- conversation organization intelligence;
- context aware orchestration.

## Regra de memória persistente

O God Mode tem duas memórias diferentes, com funções diferentes.

```text
PC / Obsidian local
└── memória operacional viva
    ├── progresso real de trabalho
    ├── estado dos projetos em uso
    ├── últimas sessões
    ├── contexto para continuar tarefas
    └── runtime privado do computador

GitHub / AndreVazao/andreos-memory
└── memória técnica de programação/repos
    ├── o que foi mexido nas repos
    ├── decisões técnicas
    ├── auditorias
    ├── histórico de programação
    └── contexto para ChatGPT/God Mode continuar código
```

A memória local pode ser colocada fora da repo pública usando:

```text
GOD_MODE_MEMORY_ROOT=C:\AndreOS\GodModeMemory
```

Se esta variável não existir, o sistema mantém compatibilidade com a pasta `memory/` existente na repo.

## GitHub Memory Sync

O God Mode agora tem camada própria para sincronizar memória técnica para o repo privado:

```text
AndreVazao/andreos-memory
```

Endpoints:

```text
GET  /api/github-memory-sync/status
GET  /api/github-memory-sync/panel
GET  /api/github-memory-sync/policy
GET  /api/github-memory-sync/latest
POST /api/github-memory-sync/sync-project
POST /api/github-memory-sync/record-repo-work
```

Esta camada só deve guardar contexto de programação/repos. Não deve guardar memória viva do PC, ficheiros runtime, dados privados de clientes, tokens, passwords, cookies, API keys ou segredos.

## Repo/File Patch Hub

O God Mode tem hub para alterações em repos com:
- plano;
- preview diff;
- checkpoint;
- aprovação explícita;
- validação;
- contrato para executor;
- registo de run.

A frase de aprovação é:

```text
APPLY REPO PATCH
```

## Estado atual

O `main` já não está em bootstrap inicial.
O sistema já expõe múltiplas APIs operacionais para:
- runtime supervision;
- browser intake e browser control;
- operação por cockpit móvel;
- driving mode seguro;
- orquestração contextual;
- adaptação e reaproveitamento de scripts;
- memória local/Obsidian;
- sync técnico para `AndreVazao/andreos-memory`;
- patch hub para repos.

## Nota sobre repos públicas temporárias

Repos públicas podem existir temporariamente para permitir builds grátis e evitar limites de cota em privado.

Isto não autoriza guardar segredos ou memória operacional viva em repos públicas.

Quando o builder/pipeline estiver concluído e os programas estiverem fechados, o destino final dos componentes privados deve ser repo privada.

## Nota sobre foundations antigas

Algumas peças Android e de packaging inicial continuam na repo como foundation histórica/placeholder e ainda não representam o fluxo final real. A consolidação e limpeza dessas peças está mapeada em `docs/repo-consolidation-and-legacy-mapping.md`.

## Nota sobre legado cloud

Supabase, Render e Vercel passaram a legado arquitetural.
A repo deve tratá-los como contexto histórico a remover, arquivar ou isolar, nunca como destino principal da stack.
