# Final Cleanup Candidates

## Branch
- `cleanup-final-docs-workflows`

## Objetivo
Fechar a limpeza final de docs transitórias e workflows que já não acrescentam valor à estrutura atual do God Mode.

## Candidatos fortes a remover
### Docs transitórias já consumidas
- `docs/handsfree-local-tunnel-next-plan.md`
- `docs/promote-handsfree-primary-plan.md`

Motivo:
- ambas documentam fases já concluídas e mergeadas
- a shell principal já está promovida para a linha handsfree
- o workflow unificado já existe como validação principal

### Workflow potencialmente obsoleto
- `.github/workflows/mobile-shell-artifact.yml`

Motivo:
- hoje falha por quota de artifacts do GitHub
- só continua útil se ainda quiseres empacotar artifact zip da shell via GitHub Actions
- se o objetivo principal for validação e deploy, o workflow unificado já cobre melhor a integridade

## O que deve ficar
- `.github/workflows/god-mode-unified-validation.yml`
- `.github/workflows/prune-old-artifacts-all-repos.yml`
- `frontend/mobile-shell/backend-presets.example.json`
- shell principal em `frontend/mobile-shell/index.html`, `app.js`, `styles.css`

## Observação
O conector permitiu abrir a branch e PR, mas falhou nas operações diretas de delete nesta fase. A remoção pode ser feita pelo GitHub web mantendo esta PR como trilho limpo da decisão final.
