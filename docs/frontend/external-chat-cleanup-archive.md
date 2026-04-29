# External Chat Cleanup Archive

## Objetivo

A Phase 123 prepara limpeza segura de conversas externas abertas em providers de IA.

O problema real é simples: ao longo do desenvolvimento, projetos como Baribudos Studio podem chegar à conversa 6, 7 ou mais. As primeiras conversas servem para contexto, decisões e histórico, mas depois não devem ficar a acumular lixo visual dentro dos providers.

## Endpoints

- `GET/POST /api/external-chat-cleanup/status`
- `GET/POST /api/external-chat-cleanup/panel`
- `GET/POST /api/external-chat-cleanup/policy`
- `POST /api/external-chat-cleanup/inventory`
- `POST /api/external-chat-cleanup/extract-memory`
- `POST /api/external-chat-cleanup/plan`
- `POST /api/external-chat-cleanup/approve-plan`
- `GET/POST /api/external-chat-cleanup/latest`
- `GET/POST /api/external-chat-cleanup/package`

## Regra principal

Antes de limpar qualquer conversa, o God Mode deve:

1. identificar provider e projeto;
2. extrair contexto útil;
3. guardar resumo, backlog e decisões em AndreOS/Obsidian;
4. gerar plano de limpeza;
5. pedir aprovação quando for apagar/arquivar.

## Ações possíveis

- `keep`: manter conversa ativa ou útil.
- `extract_then_archive`: extrair memória e arquivar depois.
- `extract_then_delete`: extrair memória e apagar depois.
- `needs_operator_review`: precisa revisão do operador.

## Quando pode propor apagar

- conversas temporárias de teste;
- conversas de correção rápida sem valor futuro;
- rascunhos que já foram extraídos;
- conversas antigas de projeto já concluído, com memória extraída.

## Quando deve manter

- projeto ainda ativo;
- conversa com decisões importantes ainda não extraídas;
- conversa com código ou contexto ainda útil;
- conversa sem resumo suficiente.

## Aprovação

A aprovação de plano exige a frase:

`CLEANUP EXTERNAL CHATS`

Esta fase apenas regista a aprovação. A execução real de apagar/arquivar em cada provider deve ficar para executor específico por provider.

## Segurança

Esta fase não apaga conversas por si.

Ela cria inventário, extração, plano e decisão. A eliminação real fica gated e dependente de provider executor.

## Resultado esperado

O God Mode consegue reduzir lixo de conversas externas sem perder contexto, porque primeiro consolida tudo em memória por projeto.
