# Cleanup Repo Tree Final Route Surface Plan

## Branch
- `feature/cleanup-rtree-next`

## Objetivo
Concluir a limpeza da superfície legacy de rotas `repo_tree*` removendo as versões restantes que já não participam no runtime atual do God Mode.

## Meta funcional
- remover as rotas `repo_tree_v6.py` até `repo_tree_v13.py`
- reduzir ruído estrutural na pasta `backend/app/routes`
- manter intacto o `backend/main.py` atual
- preparar a fase seguinte de sweep dos serviços `repo_tree*`

## Âmbito desta fase
### Remoções diretas
- `backend/app/routes/repo_tree_v6.py`
- `backend/app/routes/repo_tree_v7.py`
- `backend/app/routes/repo_tree_v8.py`
- `backend/app/routes/repo_tree_v9.py`
- `backend/app/routes/repo_tree_v10.py`
- `backend/app/routes/repo_tree_v11.py`
- `backend/app/routes/repo_tree_v12.py`
- `backend/app/routes/repo_tree_v13.py`

## Nota
O `backend/main.py` já não liga nenhuma destas rotas. O próximo passo lógico é fazer varredura dos serviços e helpers `repo_tree*` antes de apagar versões internas auxiliares.
