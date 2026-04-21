# Cleanup Repo Tree Legacy Surface Plan

## Branch
- `feature/cleanup-repo-tree-legacy-surface`

## Objetivo
Remover a superfície legacy de rotas `repo_tree*` que já não está ligada ao `backend/main.py`, reduzindo ruído antes de uma limpeza mais profunda dos serviços versionados de repo tree.

## Meta funcional
- remover rotas `repo_tree*` não ligadas ao runtime atual
- manter intacta a linha principal do backend atual
- preparar a fase seguinte de sweep dos serviços `repo_tree*`

## Âmbito desta fase
### Remoções diretas
- `backend/app/routes/repo_tree.py`
- `backend/app/routes/repo_tree_v2.py`
- `backend/app/routes/repo_tree_v3.py`
- `backend/app/routes/repo_tree_v4.py`
- `backend/app/routes/repo_tree_v5.py`
- restantes `backend/app/routes/repo_tree_v*.py` legacy

## Nota
O `backend/main.py` já não liga nenhuma destas rotas antigas. Esta fase limpa primeiro a superfície HTTP legacy; a limpeza dos serviços versionados fica para a fase seguinte com sweep de referências.
