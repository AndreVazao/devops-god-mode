# Conversation Source Import Automation + Work Map Feed

## Objetivo

A Phase 196 cria o importador de conversas/fontes para alimentar o Conversation Requirement Ledger e o Real Work Map.

O Oner pode colar uma conversa/transcrição no telemóvel. O God Mode separa pedido do Oner de resposta da IA, alimenta o ledger e cria ligação ao mapa real do projeto.

## Endpoint principal

```txt
/api/conversation-source-import-feed/package
```

## Página visual

```txt
/app/conversation-source-import-feed
/app/conversation-import
```

## Endpoints

- `/api/conversation-source-import-feed/status`
- `/api/conversation-source-import-feed/policy`
- `/api/conversation-source-import-feed/import-text`
- `/api/conversation-source-import-feed/import-messages`
- `/api/conversation-source-import-feed/create-review-cards`
- `/api/conversation-source-import-feed/dashboard`
- `/api/conversation-source-import-feed/package`

## O que esta fase faz

- Importa conversa/transcrição colada no telemóvel.
- Importa lista estruturada de mensagens.
- Separa Oner/User de Assistant/ChatGPT/Claude/Gemini.
- Alimenta o Conversation Requirement Ledger.
- Liga a conversa ao Real Work Map.
- Classifica por grupo/frente.
- Cria cards de revisão quando faltam labels ou o projeto fica incerto.
- Redige linhas óbvias de segredo como `[REDACTED_SECRET_LINE]` antes de analisar.

## Labels recomendadas

```txt
Oner: pedido do André/Oner
Assistant: resposta da IA
ChatGPT: resposta do ChatGPT
Claude: resposta do Claude
Gemini: resposta do Gemini
```

## O que esta fase não faz

- Não guarda passwords.
- Não guarda tokens.
- Não guarda cookies.
- Não trata resposta de IA como decisão final.
- Não descarta pedidos antigos do Oner.

## Regra de realidade

A conversa importada é fonte de evidência. Pedido do Oner é intenção. Resposta de IA é proposta até ser aceite, implementada e validada.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 195 deve ser apagado. Fica só:

- `.github/workflows/phase196-conversation-source-import-feed-smoke.yml`

Além dos workflows globais/builds.
