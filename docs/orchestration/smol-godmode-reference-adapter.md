# smol-ai GodMode Reference Adapter + Multi-AI Cockpit Patterns

## Objetivo

A Phase 189 avalia o repo público `smol-ai/GodMode` e absorve apenas os padrões úteis para o nosso God Mode.

O repo externo ajuda como referência de UX, não como dependência central.

## Veredicto

Ajuda em:

- cockpit multi-IA;
- webapps completas em panes;
- prompt broadcast para várias IAs;
- provider toggle;
- layout com resize/reorder/popout;
- prompt critic;
- fallback para providers sem API.

Não substitui:

- backend FastAPI;
- PC brain;
- mobile cockpit;
- vault local cifrado;
- PR/GitHub automation;
- deployment gates;
- AndreOS memory;
- requirement ledger;
- build/install pipeline.

## Endpoint principal

```txt
/api/smol-godmode-reference-adapter/package
```

## Endpoints

- `/api/smol-godmode-reference-adapter/status`
- `/api/smol-godmode-reference-adapter/capability-fit`
- `/api/smol-godmode-reference-adapter/patterns`
- `/api/smol-godmode-reference-adapter/provider-pane-manifest`
- `/api/smol-godmode-reference-adapter/prompt-broadcast-contract`
- `/api/smol-godmode-reference-adapter/prompt-critic-policy`
- `/api/smol-godmode-reference-adapter/package`

## Padrões absorvidos

### Dedicated multi-AI browser

O nosso God Mode deve conseguir abrir/controlar várias IAs como webapps completas quando a API não chega.

### Prompt broadcast

Enviar o mesmo pedido a várias IAs para comparar respostas, captar scripts e alimentar o ledger.

### Full webapp over API when needed

Usar webapp quando API não oferece uploads, multimodal, code interpreter ou funcionalidades recentes.

### Provider toggle/layout

O Oner escolhe quais IAs entram numa missão. O PC guarda layout/preferências.

### Prompt critic

Antes de enviar a várias IAs, melhorar o prompt sem alterar a intenção original do Oner.

## Regra de segurança

- Não guardar credenciais.
- Não guardar cookies/tokens.
- Usar sessão local do browser do PC quando aprovado.
- Cada resposta de IA entra no ledger como `ai_response`, não como decisão.
- Scripts extraídos exigem reconciliation antes de aplicar.
- Qualquer browser automation sensível exige approval gate.

## Próxima fase recomendada

Phase 190 — Provider Prompt Broadcast + Pane Manifest Runtime.

Objetivo: implementar nativamente o runtime de pane manifest + broadcast plan ligado ao ledger/provider proof.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 188 deve ser apagado. Fica só:

- `.github/workflows/phase189-smol-godmode-reference-adapter-smoke.yml`

Além dos workflows globais/builds.
