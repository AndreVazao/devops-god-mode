# Money Command Center

## Cockpit

- `/app/money-command-center`

## API

- `GET /api/money-command-center/status`
- `GET /api/money-command-center/package`
- `GET /api/money-command-center/dashboard`
- `GET /api/money-command-center/matrix`
- `GET /api/money-command-center/top-project`
- `GET /api/money-command-center/blockers`
- `GET /api/money-command-center/sellable-offers`
- `POST /api/money-command-center/revenue-sprint`
- `POST /api/money-command-center/approval-card`
- `POST /api/money-command-center/prepare-mvp-delivery`

## Objetivo

Unificar Monetization Readiness, Revenue Sprint Planner, Project Portfolio e Mobile Approval Cockpit num ecrã mobile-first.

A pergunta principal é simples:

> Qual é o próximo passo mais curto para começar a ganhar dinheiro?

## Botões do cockpit

- Ver projeto com maior chance de dinheiro
- Criar sprint de receita
- Aprovar próximo passo
- Ver bloqueios para ganhar dinheiro
- Ver primeiro produto vendável por projeto
- Preparar entrega MVP

## Como decide o projeto prioritário

O serviço usa a matriz de monetização e calcula uma ordem prática com base em:

- prioridade do projeto;
- readiness score;
- existência de repo/app ligado;
- quantidade de blockers;
- bónus estratégico para projetos com caminho mais direto para receita.

Projetos com caminho comercial direto, como ProVentil, Baribudos Website, Baribudos Studio e VerbaForge, sobem no ranking quando têm capacidade real de gerar oferta, proposta, landing page ou produto vendável.

## Fluxo recomendado

1. Abrir `/app/money-command-center` no telemóvel.
2. Tocar em **Ver projeto com maior chance de dinheiro**.
3. Tocar em **Criar sprint de receita**.
4. Tocar em **Aprovar próximo passo**.
5. A aprovação fica no Mobile Approval Cockpit.
6. A próxima fase deve transformar o sprint aprovado em PRs pequenas, auditoria, build/deploy e checklist de entrega.

## Memória AndreOS

O Money Command Center escreve histórico e última sessão em `GOD_MODE` sempre que:

- escolhe projeto prioritário;
- cria sprint de receita;
- cria cartão de aprovação;
- prepara entrega MVP.

Não escreve tokens, passwords, cookies, authorization, bearer, API keys ou secrets.

## Segurança

Esta fase não executa deploy, não cria repos e não aplica alterações destrutivas. Ela cria decisão, sprint, cartão de aprovação e checklist de entrega MVP.

A execução real deve continuar em fases pequenas, com PRs pequenas e aprovação explícita.
