# New Project Start Intake

## Objetivo

A Phase 115 adiciona o caminho para projetos novos do zero.

As fases anteriores focaram projetos, repos e conversas já existentes. Esta fase cobre ideias novas que ainda não têm conversa, repo, memória ou ficheiros.

## Endpoints

- `GET/POST /api/new-project-start/status`
- `GET/POST /api/new-project-start/panel`
- `GET/POST /api/new-project-start/template`
- `POST /api/new-project-start/propose`
- `POST /api/new-project-start/approve-plan`
- `GET/POST /api/new-project-start/creation-gates`
- `GET/POST /api/new-project-start/latest`
- `GET/POST /api/new-project-start/package`

## Ligação à Home

A Home passa a expor:

- `Projeto novo`
- `/api/new-project-start/panel`

## O que faz

A partir de uma ideia em linguagem normal, o God Mode prepara:

- nome normalizado;
- project_id;
- sugestão de repo;
- tipo de projeto;
- plataformas alvo;
- módulos sugeridos;
- arquitetura inicial;
- primeiros passos seguros;
- gates de criação;
- sugestão de prioridade.

## Tipos suportados

- app
- website
- backend
- mobile_apk
- desktop_exe
- automation_bot
- content_system
- business_system
- game_bot
- ai_tool
- unknown

## Segurança

Esta fase não cria nada real sem aprovação.

Não faz automaticamente:

- criar repo;
- escrever ficheiros;
- criar memória de projeto;
- configurar builds;
- executar primeiro build.

Tudo isso fica atrás de gates de aprovação.

## Fluxo

1. Operador dá ideia nova.
2. God Mode cria proposta estruturada.
3. Operador aprova plano.
4. God Mode mostra gates de criação.
5. Só depois uma fase seguinte deve materializar memória/repo/ficheiros/builds com aprovação.

## Próximo passo recomendado

Phase 116 deve criar o `New Project Creation Gate Runner`, para transformar a proposta aprovada em ações reais controladas:

- criar memória do projeto;
- criar repo;
- escrever ficheiros base;
- configurar workflows;
- disparar primeiro build.
