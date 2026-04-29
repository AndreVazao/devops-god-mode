# Approved Deep Execution Plan

## Objetivo

A Phase 112 cria a camada de plano de execução profunda aprovado.

Ela fica entre:

- intake unificado;
- confirmação de prioridades;
- pipeline real de trabalho.

A execução profunda só fica pronta quando o operador já confirmou prioridades e grupos na Phase 111.

## Endpoints

- `GET/POST /api/approved-deep-execution/status`
- `GET/POST /api/approved-deep-execution/readiness`
- `GET/POST /api/approved-deep-execution/plan`
- `POST /api/approved-deep-execution/approval-cards`
- `POST /api/approved-deep-execution/start-safe`
- `GET/POST /api/approved-deep-execution/latest`
- `GET/POST /api/approved-deep-execution/package`

## Ligação à Home

A Home passa a expor:

- `Execução aprovada`
- `/api/approved-deep-execution/plan`

## O que faz

- Verifica se o intake/prioridades já foram confirmados.
- Se não foram, bloqueia execução profunda.
- Se foram, cria lanes por projeto conforme prioridade do operador.
- Separa ações seguras de ações com aprovação obrigatória.
- Prepara gates para escrita, prompts externos, criação de repos, renomeação de conversas e merge/delete de módulos.

## Ações seguras sem aprovação extra

- Ler inventário.
- Ler árvore do projeto.
- Ler metadata de repo.
- Ler snapshot visível de chat.
- Resumir findings.
- Preparar patch preview.

## Ações com aprovação obrigatória

- Enviar prompt para IA externa.
- Renomear conversa externa.
- Criar repo em falta.
- Escrever ficheiros de projeto.
- Materializar código vindo de conversa.
- Disparar build real.
- Fundir/apagar módulos duplicados.

## Segurança

Esta fase não executa mudanças profundas sozinha.

`start-safe` só envia comando para executar passos seguros:

- sem escrever ficheiros;
- sem criar repos;
- sem renomear conversas;
- sem enviar prompts externos;
- com aprovação antes de qualquer ação destrutiva.

## Próximo passo recomendado

Phase 113 deve transformar as lanes aprovadas em fila real de trabalho controlada, reaproveitando `request_worker_loop`, `real_work_command_pipeline`, `operation_queue` e `mobile_approval_cockpit_v2`.
