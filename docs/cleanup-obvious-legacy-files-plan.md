# Cleanup Obvious Legacy Files Phase Plan

## Branch
- `feature/cleanup-obvious-legacy-files`

## Objetivo
Remover ficheiros legados e duplicados que já não encaixam na linha atual do God Mode, reduzindo ruído estrutural antes de uma limpeza mais profunda com varredura de imports.

## Meta funcional
- remover entrypoints antigos e candidatos obsoletos
- remover workflow temporário antigo fora da rotação atual
- remover rotas ops legadas acumuladas
- remover ficheiros de teste e duplicados óbvios
- preparar a fase seguinte de limpeza profunda com sweep de referências

## Âmbito desta fase
### Remoções seguras e óbvias
- `.github/workflows/platform-control-hardening-phase.yml`
- `backend/app_main.py`
- `backend/main_candidate.py`
- `backend/repo_tree_service.py`
- `docs/z_test.txt`
- `backend/app/routes/ops_final_candidate.py`
- `backend/app/routes/ops_v1.py` até `ops_v8.py`

### Próxima fase
Fazer sweep de imports/referências antes de remover famílias mais arriscadas como `repo_tree*` e serviços versionados auxiliares.
