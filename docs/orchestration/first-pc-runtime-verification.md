# First PC Install Operator Guide + Runtime Verification Cockpit

## Objetivo

A Phase 198 torna o primeiro teste real no PC mais direto.

Ela cria uma página de verificação runtime com rotas essenciais, checklist curto de EXE/APK e o primeiro fluxo operacional real.

## Endpoint principal

```txt
/api/first-pc-runtime-verification/package
```

## Página visual

```txt
/app/first-pc-runtime-verification
/app/pc-runtime-check
```

## Endpoints

- `/api/first-pc-runtime-verification/status`
- `/api/first-pc-runtime-verification/guide`
- `/api/first-pc-runtime-verification/checks`
- `/api/first-pc-runtime-verification/package`

## Rotas essenciais verificadas

- `/app/home`
- `/app/real-work-fast-path`
- `/app/github-repo-inventory-feed`
- `/app/repo-scanner-real-work-map`
- `/app/conversation-source-import-feed`
- `/app/provider-browser-local-launcher`
- `/app/provider-broadcast-cockpit`
- `/app/mobile-approval-cockpit-v2`

## Primeiro fluxo real

1. Importar inventário de repos.
2. Scan/classificação de repos.
3. Importar conversa.
4. Criar provider launcher package.
5. Colar captura/importar resposta.
6. Rever ledger/cards.

## Instrução curta PC

1. Descarregar artifact Windows EXE mais recente.
2. Extrair o bundle se necessário.
3. Executar `GodModeDesktop.exe`.
4. Confirmar `/app/home`.
5. Abrir `/app/first-pc-runtime-verification`.
6. Seguir o fluxo real rápido.

## Regra de realidade

Esta fase não finge instalação. Ela mostra rotas, estados e passos que o Oner deve verificar no PC.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 197 deve ser apagado. Fica só:

- `.github/workflows/phase198-first-pc-runtime-verification-smoke.yml`

Além dos workflows globais/builds.
