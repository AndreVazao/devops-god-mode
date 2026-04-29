# Approved Work Queue Mobile Panel

## Objetivo

A Phase 114 cria o painel visual mobile da fila aprovada.

Esta camada transforma estado de prontidão, fila, execução segura e pontos de decisão em cartões claros para Home/APK.

## Endpoints

- `GET/POST /api/approved-work-queue-mobile/status`
- `GET/POST /api/approved-work-queue-mobile/panel`
- `POST /api/approved-work-queue-mobile/run-safe`
- `GET/POST /api/approved-work-queue-mobile/package`

## Ligação à Home

A Home passa a expor:

- `Painel fila`
- `/api/approved-work-queue-mobile/panel`

## Cartões principais

### Prioridades

Mostra se a execução profunda está desbloqueada ou se ainda é preciso confirmar prioridades.

### Fila aprovada

Mostra:

- queue_id;
- total de itens;
- itens seguros;
- itens que precisam de decisão;
- itens seguros por executar;
- itens seguros já submetidos.

### Execução segura

Mostra próximos passos seguros e último run.

Botão:

- `Executar próximos seguros`
- `POST /api/approved-work-queue-mobile/run-safe`

### Gates / decisões

Mostra ações bloqueadas até confirmação explícita:

- consulta externa por IA;
- organizar conversas;
- criar repos;
- escrever ficheiros;
- materializar código;
- disparar build;
- fundir/apagar módulos.

## Segurança

Esta fase não executa ações destrutivas.

Ela só chama o runner seguro da Phase 113, que já bloqueia:

- escrita de ficheiros;
- criação de repos;
- consultas externas automáticas;
- renomeação de conversas;
- qualquer ação que precise de confirmação.

## Próximo passo recomendado

Phase 115 deve ligar este painel ao modo fácil visual, para aparecer como cartão principal no telemóvel com botões grandes:

- Confirmar prioridades;
- Criar fila;
- Executar seguros;
- Ver decisões;
- Continuar.
