# Visible Provider Broadcast Cockpit Page + Manual Response Capture

## Objetivo

A Phase 191 torna visível no cockpit o runtime da Phase 190.

O Oner passa a ter uma página mobile-first para:

- selecionar providers/IAS;
- escrever o pedido original;
- gerar broadcast plan;
- copiar prompt para cada IA;
- colar/importar respostas manualmente;
- comparar respostas;
- enviar respostas para o Conversation Requirement Ledger como `ai_response`.

## Rotas visuais

```txt
/app/provider-broadcast-cockpit
/app/provider-prompt-broadcast
```

## Endpoints usados

- `/api/provider-prompt-broadcast-runtime/default-pane-profile`
- `/api/provider-prompt-broadcast-runtime/create-broadcast-plan`
- `/api/provider-prompt-broadcast-runtime/import-provider-response`
- `/api/provider-prompt-broadcast-runtime/compare-responses`
- `/api/provider-prompt-broadcast-runtime/package`
- `/api/conversation-ledger-cockpit-review/package`

## Entrada na Home

A Home principal recebe botão:

```txt
Broadcast IA -> /app/provider-broadcast-cockpit
```

## Fluxo mobile-first

1. Escrever pedido original.
2. Selecionar providers.
3. Ativar/desativar prompt critic seguro.
4. Criar broadcast plan.
5. Copiar prompt.
6. Colar nas IAs externas manualmente.
7. Colar resposta de cada IA no cockpit.
8. Importar resposta.
9. Comparar respostas.
10. Rever scripts/gaps no ledger antes de decidir/aplicar.

## Segurança

- Não guarda credenciais.
- Não guarda cookies/tokens.
- Não automatiza browser nesta fase.
- Resposta de IA é `ai_response`, não decisão.
- Scripts detetados exigem reconciliation antes de aplicar.
- Decisão final continua a exigir revisão do Oner.

## Por que é real

Esta fase não promete browser automation. Ela entrega um fluxo realmente utilizável agora:

- copiar prompt;
- colar em ChatGPT/Claude/Gemini/etc.;
- colar respostas no cockpit;
- comparar;
- alimentar o ledger.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 190 deve ser apagado. Fica só:

- `.github/workflows/phase191-provider-broadcast-cockpit-smoke.yml`

Além dos workflows globais/builds.
