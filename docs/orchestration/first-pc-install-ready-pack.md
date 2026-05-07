# First PC Install Ready Pack + One-Click Local Start Contract

## Objetivo

A Phase 202 aproxima o God Mode da instalação real no PC.

Esta fase agrega readiness, artifacts, runtime verification e contrato de primeiro arranque local para `GodModeDesktop.exe`, com foco em abrir o programa no PC o mais rápido possível e manter a autoevolução futura sempre gated.

## Endpoint principal

```txt
/api/first-pc-install-ready-pack/package
```

## Página visual

```txt
/app/first-pc-install-ready-pack
/app/pc-install-ready
```

## Endpoints

- `/api/first-pc-install-ready-pack/status`
- `/api/first-pc-install-ready-pack/one-click-local-start-contract`
- `/api/first-pc-install-ready-pack/ready-pack`
- `/api/first-pc-install-ready-pack/checklist`
- `/api/first-pc-install-ready-pack/package`

## O que faz

- Define contrato de arranque local para `GodModeDesktop.exe`.
- Expõe URL local canónico: `http://127.0.0.1:8000/app/home`.
- Junta readiness final, artifacts, guia de primeiro arranque, runtime verification e global state.
- Lista rotas essenciais do PC.
- Lista sinais de sucesso e falhas seguras.
- Reforça que não há tokens/passwords/cookies/API keys no repo ou memória.
- Prepara o fluxo real de instalação e primeiro uso no PC.

## Contrato de arranque local

```txt
GodModeDesktop.exe
→ backend local porta 8000
→ /health
→ /app/home
→ /app/first-pc-install-ready-pack
```

## Fluxo real recomendado

```txt
1. Download do artifact Windows EXE.
2. Extrair no PC.
3. Executar GodModeDesktop.exe.
4. Abrir /app/home.
5. Abrir /app/first-pc-install-ready-pack.
6. Importar inventário de repos.
7. Importar conversa atual.
8. Rever candidatos de autoevolução.
9. Aprovar só ações gated.
```

## Segurança

- `can_store_secrets_in_repo=false`.
- `can_auto_update_without_gate=false`.
- Não faz auto-update final.
- Não faz merge/release/deploy autónomo.
- Não guarda segredos.
- Não automatiza login/browser privado.

## Regra de merge clarificada

O runtime autónomo do God Mode não pode fazer merge sozinho.

Durante sessão assistida, se o Oner mandar continuar/mergear depois de checks verdes, o assistente pode fazer merge para acelerar o desenvolvimento.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 201 deve ser apagado. Fica só:

- `.github/workflows/phase202-first-pc-install-ready-pack-smoke.yml`

Além dos workflows globais/builds.
