# Conversation Requirement Ledger + Request/Decision Reconciliation

## Objetivo

A Phase 187 cria uma camada para o God Mode distinguir:

- pedidos do Oner;
- respostas/propostas das IAs;
- decisões aceites;
- scripts/code blocks extraídos;
- mudanças de direção arquitetural;
- evidência real de implementação;
- requisitos esquecidos ou parcialmente cumpridos.

Isto responde diretamente ao problema de conversas longas e múltiplas IAs: o God Mode não pode tratar uma resposta de IA como verdade final. O pedido do Oner é a fonte de intenção.

## Endpoint principal

```txt
/api/conversation-requirement-ledger/package
```

## Endpoints

- `/api/conversation-requirement-ledger/status`
- `/api/conversation-requirement-ledger/policy`
- `/api/conversation-requirement-ledger/analyze-text`
- `/api/conversation-requirement-ledger/analyze-messages`
- `/api/conversation-requirement-ledger/compare-project`
- `/api/conversation-requirement-ledger/open-requirements`
- `/api/conversation-requirement-ledger/realness-scorecard`
- `/api/conversation-requirement-ledger/package`

## Regras

1. Pedido do Oner é a fonte da intenção.
2. Resposta de IA é proposta até ser confirmada, implementada e validada.
3. Mudança de direção não apaga pedidos antigos.
4. Migrações ficam registadas, por exemplo cloud/Supabase/Render/Vercel para PC brain + mobile cockpit.
5. Feature só é marcada como real quando há evidência:
   - endpoint;
   - código;
   - PR;
   - merge;
   - GitHub Actions;
   - smoke/build;
   - proof local.

## Fluxo

1. Importar ou colar transcript/conversa.
2. O ledger separa mensagens do operador e respostas de IA.
3. Extrai pedidos, decisões, scripts e migrações.
4. Compara pedido vs decisão/evidência.
5. Gera open requirements e realness scorecard.
6. God Mode usa isto para não esquecer pedidos antigos.

## Exemplo God Mode

O projeto começou com hipóteses cloud:

- Supabase;
- Render;
- Vercel.

Depois migrou para:

- PC como cérebro;
- telemóvel como cockpit;
- backend local;
- vault local;
- provider/dry-run gates.

A migração é válida, mas os pedidos antigos não devem desaparecer. O ledger preserva intenção e mostra o que ainda falta reconciliar.

## Segurança

- Não guarda segredos crus.
- Guarda fingerprints/scripts previews.
- Não assume que código de IA é correto.
- Scripts extraídos exigem reconciliation antes de aplicar.
- Requisitos abertos precisam de decisão/evidência.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 186 deve ser apagado. Fica só:

- `.github/workflows/phase187-conversation-requirement-ledger-smoke.yml`

Além dos workflows globais/builds.
