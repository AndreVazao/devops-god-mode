# Cross-Repo Artifact Cleanup

## Objetivo
Apagar artifacts antigos em várias repos do mesmo owner para libertar quota de GitHub Actions.

## Workflow
- `.github/workflows/prune-old-artifacts-all-repos.yml`

## Requisito obrigatório
Criar um secret no repositório `devops-god-mode` com nome:
- `GH_ADMIN_TOKEN`

## Permissões recomendadas para o token
Token clássico ou fine-grained com acesso suficiente para:
- listar repos
- listar artifacts/actions
- apagar artifacts

## Como usar
1. Ir a **Actions**
2. Abrir **Prune Old Artifacts Across Repos**
3. Carregar em **Run workflow**
4. Definir, se quiseres:
   - `owner` = `AndreVazao`
   - `older_than_days` = `3`
   - `keep_newest` = `5`
   - `repo_visibility` = `all`, `public` ou `private`

## Política prática recomendada
- manter os 5 mais recentes por repo
- apagar os restantes com mais de 3 dias

## Nota
Sem `GH_ADMIN_TOKEN`, o workflow não consegue limpar artifacts fora do próprio repositório.
