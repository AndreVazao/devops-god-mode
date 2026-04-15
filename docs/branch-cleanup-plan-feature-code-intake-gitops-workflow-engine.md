# Branch Cleanup Plan — feature/code-intake-gitops-workflow-engine

## Objetivo
Consolidar a evolução rápida desta branch numa base limpa antes do merge para `main`.

## Entry points candidatos a manter
- `backend/main_candidate.py`
- `backend/main_v13.py` (árvore)

## Router candidato a manter
- `backend/app/routes/ops_final_candidate.py`

## Ficheiros que tendem a ficar obsoletos após consolidação
### Ops entrypoints antigos
- `backend/main_ops_v1.py`
- `backend/main_ops_v2.py`
- `backend/main_ops_v3.py`
- `backend/main_ops_v4.py`
- `backend/main_ops_v5.py`
- `backend/main_ops_v6.py`
- `backend/main_ops_v7.py`

### Ops routers antigos
- `backend/app/routes/ops_v1.py`
- `backend/app/routes/ops_v2.py`
- `backend/app/routes/ops_v3.py`
- `backend/app/routes/ops_v4.py`
- `backend/app/routes/ops_v5.py`
- `backend/app/routes/ops_v6.py`
- `backend/app/routes/ops_v7.py`
- `backend/app/routes/ops_v8.py`

### Workflows de branch antigos
- `.github/workflows/branch-smoke-test-v2.yml`
- `.github/workflows/branch-smoke-test-v3.yml`
- `.github/workflows/branch-smoke-test-v4.yml`

## Próxima limpeza esperada
1. criar smoke test final candidato
2. validar `main_candidate.py`
3. remover entrypoints e routers antigos
4. manter um único workflow de smoke da branch
5. preparar merge para `main`
