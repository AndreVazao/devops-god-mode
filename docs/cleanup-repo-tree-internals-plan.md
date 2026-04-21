# Cleanup Repo Tree Internals Plan

## Branch
- `feature/cleanup-rtree-internals`

## Objective
Remove remaining legacy repo tree internals that became orphaned after removing the repo tree routes and main repo tree services.

## Scope
- `backend/app/services/repo_tree_analysis_v1.py`
- `backend/app/services/repo_tree_analysis_v2.py`
- `backend/app/services/repo_tree_cache_v2.py`
- `backend/app/services/repo_tree_cache_v3.py`
- `backend/app/services/repo_tree/github_lazy_provider.py`

## Next Step
After this cleanup, review the rest of `backend/app/services/repo_tree/` for any remaining dead files or empty directories.
