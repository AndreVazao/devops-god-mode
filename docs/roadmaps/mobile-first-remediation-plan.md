# Mobile-First Remediation Plan

## Decisão operacional

O próximo passo do ecossistema é desenvolver primeiro o **DevOps God Mode** para correr com comando principal no telemóvel do owner.

## Princípio

O Studio e o Website **não serão arranjados manualmente primeiro**.

A ordem correta é:

1. construir o DevOps God Mode;
2. ligar GitHub, Vercel e estado de sistema;
3. fazer o God Mode auditar, alinhar e reparar o Studio e o Website;
4. usar o telemóvel como painel principal de operação.

## Modelo de execução

### No telemóvel
- painel principal;
- controlo administrativo;
- visão de estado;
- alertas;
- aprovação de ações;
- leitura de logs resumidos;
- disparo de repair jobs.

### Na cloud
- backend Python no Render;
- scanners GitHub/Vercel;
- filas de jobs;
- análise de repositórios;
- plano de correção;
- execução de ações DevOps.

## O que o God Mode tem de fazer antes de mexer no Baribudos

### Fase 0 — fundação
- backend vivo;
- secrets vivos;
- health/config OK.

### Fase 1 — scanners
- listar repositórios GitHub;
- listar projetos/deploys Vercel;
- classificar stacks;
- identificar risco.

### Fase 2 — registry
- guardar inventário de repos;
- guardar relações de ecossistema;
- guardar regras manuais.

### Fase 3 — remediation engine
- detetar desalinhamentos;
- detetar segredos em repo;
- detetar contrato quebrado;
- detetar build drift;
- sugerir repair plan.

### Fase 4 — execution engine
- abrir branch de reparação;
- aplicar correções;
- preparar rollback;
- registar auditoria.

## Aplicação ao caso Baribudos

Quando estas fases estiverem prontas, o God Mode deve conseguir:

- auditar `baribudos-studio`;
- auditar `baribudos-studio-website`;
- validar contrato Studio -> Website;
- validar risco de segurança;
- propor alinhamento sem destruir o que já está feito;
- executar reparações controladas.

## Regra principal

O God Mode é o sistema que vai arranjar e alinhar os outros sistemas.

No caso Baribudos:
- o Studio continua a ser soberano do seu ecossistema;
- o Website continua a ser runtime público;
- o God Mode entra como ferramenta de auditoria, reparação e alinhamento, operada a partir do telemóvel.

## Meta imediata

A meta imediata é entregar no God Mode:
- scanner GitHub real;
- scanner Vercel real;
- registry de ecossistemas;
- painel mobile-first para decidir reparações.
