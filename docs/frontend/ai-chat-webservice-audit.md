# AI Chat Webservice Audit

## Objetivo

A Phase 105 audita a capacidade do God Mode para falar com IAs em chats externos via web/browser/web service.

Esta auditoria separa claramente duas coisas:

1. Chat interno do operador para o backend.
2. Controlo real de chats externos de IAs.

## Estado honesto

O God Mode já tem:

- bridge interno operador → trabalho real;
- threads internas de conversa;
- pipeline/autopilot ligado ao chat interno.

Mas a auditoria estática não encontrou prova suficiente de:

- abrir sessão de chat externo controlada;
- ler mensagens visíveis de chats externos;
- fazer scroll no histórico;
- enviar prompt/pergunta para uma IA externa;
- esperar resposta;
- extrair resposta final;
- gate de segurança dedicado para prompts externos.

## Endpoints

- `GET /api/ai-chat-webservice-audit/status`
- `POST /api/ai-chat-webservice-audit/status`
- `GET /api/ai-chat-webservice-audit/audit`
- `POST /api/ai-chat-webservice-audit/audit`
- `GET /api/ai-chat-webservice-audit/package`
- `POST /api/ai-chat-webservice-audit/package`

## Ligação à Home

A Home passa a expor:

- `Auditar chats IA`
- `/api/ai-chat-webservice-audit/audit`

## Checks principais

A auditoria valida:

- chat interno operador → trabalho real;
- store de threads internas;
- registo de IAs externas;
- abertura de sessão/browser;
- leitura de mensagens visíveis;
- scroll de histórico;
- envio de prompt;
- espera de resposta;
- extração de resposta;
- gate de segurança para prompts externos.

## Próximas fases recomendadas

Se a auditoria falhar, o próprio endpoint recomenda fases como:

- criar registo de IAs externas;
- criar sessão controlada de browser/web service;
- criar leitor/scroll de conversa;
- criar envio de prompt e extração de resposta;
- criar gate de segurança para não enviar informação sensível sem confirmação.

## Nota

Esta fase não implementa automação de browser externo. Ela torna a lacuna visível, auditável e ligada à Home para guiar a implementação correta.
