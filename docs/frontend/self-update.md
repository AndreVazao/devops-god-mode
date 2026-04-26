# Self Update Cockpit

## Routes

- `/api/self-update/status`
- `/api/self-update/package`
- `/api/self-update/dashboard`
- `/api/self-update/git-state`
- `/api/self-update/plan`
- `/api/self-update/backup-manifest`
- `/api/self-update/execute`
- `/app/self-update`

## Objective

Allow God Mode to plan and eventually run safe local updates without deleting operator state, AndreOS memory, local data or environment files.

## Preserved paths

- `data/`
- `memory/`
- `.env`
- `backend/.env`
- `frontend/mobile-shell/backend-presets.example.json`

## Managed paths

- `backend/`
- `frontend/`
- `desktop/`
- `scripts/`
- `docs/`
- `.github/workflows/`
- `README.md`
- `PROJECT_TREE.txt`

## Safe flow

1. Inspect Git state.
2. Block update if worktree is dirty.
3. Create backup manifest for memory/data.
4. Dry-run planned commands.
5. Only run real update on the PC local runtime when explicitly allowed.
6. Rebuild EXE/APK when backend/frontend changes require it.
7. Keep AndreOS memory and local state preserved.

## Safety

The cockpit defaults to dry-run. It never deletes `data/`, `memory/` or `.env` files. A real update must be explicit and should run only on the PC local runtime.
