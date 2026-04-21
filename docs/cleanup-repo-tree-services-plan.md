# Cleanup Repo Tree Services Plan

## Branch
- `feature/cleanup-rtree-services`

## Objetivo
Continuar a limpeza do God Mode removendo a camada principal de serviços `repo_tree*` que já ficou sem superfície HTTP e sem ligação ao runtime atual.

## Meta funcional
- remover motores legacy `repo_tree_engine*`
- remover planeadores `repo_tree_action_plan*`
- remover helpers de advice/cockpit/drift
- remover leitura legacy de snapshot
- preparar a fase seguinte para limpeza de caches, análises e provider interno `repo_tree/`

## Âmbito desta fase
### Remoções diretas
- `backend/app/services/repo_tree_engine.py`
- `backend/app/services/repo_tree_engine_v2.py`
- `backend/app/services/repo_tree_engine_v3.py`
- `backend/app/services/repo_tree_engine_v4.py`
- `backend/app/services/repo_tree_action_plan_v1.py`
- `backend/app/services/repo_tree_action_plan_v2.py`
- `backend/app/services/repo_tree_action_plan_v3.py`
- `backend/app/services/repo_tree_advice_v1.py`
- `backend/app/services/repo_tree_cockpit_v1.py`
- `backend/app/services/repo_tree_drift_v1.py`
- `backend/app/services/repo_tree_snapshot_reader_v1.py`

## Nota
O próximo passo lógico é limpar `repo_tree_analysis*`, `repo_tree_cache*` e `backend/app/services/repo_tree/` depois de confirmar que não há reaproveitamento noutra linha do produto.
