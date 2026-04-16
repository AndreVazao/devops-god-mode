# Cleanup Obsolete Files Plan

## Branch
- `chore/cleanup-obsolete-files`

## Objetivo
Limpar ficheiros obsoletos, duplicados ou já ultrapassados sem mexer na lógica funcional do God Mode.

## Princípio
Nesta branch só entram remoções ou consolidações de ficheiros que já não são necessários.

## Candidatos fortes a limpeza
### Mobile shell — ficheiros intermédios/históricos
- `frontend/mobile-shell/index.hybrid.html`
- `frontend/mobile-shell/app.hybrid.js`
- `frontend/mobile-shell/styles.hybrid.css`

Motivo:
- a shell híbrida já foi promovida para os ficheiros principais
- estes ficheiros ficaram como intermédios de transição

### Docs de transição já consumidas
- `docs/mobile-first-cockpit-shell-port-note.md`
- `docs/mobile-shell-next-phase-plan.md`
- `docs/mobile-shell-primary-promotion.md`

Motivo:
- serviram para port, promoção e fase intermédia
- confirmar se queres manter histórico documental ou limpar

### Workflows antigos substituídos
Verificar se ainda existem e remover os que já não fazem sentido manter:
- `.github/workflows/mobile-hybrid-shell-smoke.yml`
- `.github/workflows/mobile-shell-next-phase-smoke.yml`
- `.github/workflows/mobile-shell-promote-primary-smoke.yml`

Motivo:
- fases intermédias já fechadas e mergeadas
- manter só os workflows finais que continuam úteis

## Candidatos que exigem cuidado antes de apagar
### Limpeza de artifacts
- `.github/workflows/prune-old-artifacts-all-repos.yml`
- `.github/workflows/prune-old-artifacts-all-repos-v2.yml`
- `.github/workflows/prune-old-artifacts.yml`

Motivo:
- confirmar qual é a versão final realmente usada
- idealmente manter só uma

## Regra de execução
1. rever ficheiros existentes no `main`
2. apagar apenas os claramente obsoletos
3. correr smoke/workflows necessários
4. abrir PR pequena de cleanup

## Resultado esperado
- repo mais limpa
- menos docs e workflows transitórios
- menos duplicação no mobile shell
