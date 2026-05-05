# Conversation Ledger Cockpit Cards + Open Requirements Review

## Objetivo

A Phase 188 coloca o Conversation Requirement Ledger em formato operacional para cockpit mobile/PC.

O Oner passa a ter cards para rever requisitos abertos ou parcialmente cumpridos e marcar cada pedido como:

- confirmado;
- ainda aberto;
- migrado;
- obsoleto;
- implementado;
- proposta IA rejeitada.

## Endpoint principal

```txt
/api/conversation-ledger-cockpit-review/package
```

## Endpoints

- `/api/conversation-ledger-cockpit-review/status`
- `/api/conversation-ledger-cockpit-review/policy`
- `/api/conversation-ledger-cockpit-review/cards`
- `/api/conversation-ledger-cockpit-review/review`
- `/api/conversation-ledger-cockpit-review/batch-review`
- `/api/conversation-ledger-cockpit-review/summary`
- `/api/conversation-ledger-cockpit-review/history`
- `/api/conversation-ledger-cockpit-review/package`

## Regras

1. Pedido aberto não pode desaparecer em silêncio.
2. Resposta de IA não vira decisão sem revisão do Oner.
3. Requisito implementado deve ter evidência quando possível.
4. Mudança de arquitetura deve ser marcada como migrada, não apagada.
5. Requisitos obsoletos exigem nota do operador.

## Card mobile

Cada card contém:

- pedido original;
- prioridade;
- temas;
- decisões ligadas;
- gaps de realidade;
- ações recomendadas;
- botões de decisão.

## Botões

- Confirmar;
- Manter aberto;
- Migrado;
- Obsoleto;
- Implementado;
- Rejeitar proposta IA.

## Relação com God Mode real

Esta fase força o God Mode a confrontar o que foi pedido com o que foi realmente implementado.

Uma feature só deve ser considerada real se houver evidência:

- endpoint;
- código;
- PR;
- merge;
- GitHub Actions;
- smoke/build;
- proof local.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 187 deve ser apagado. Fica só:

- `.github/workflows/phase188-ledger-cockpit-review-smoke.yml`

Além dos workflows globais/builds.
