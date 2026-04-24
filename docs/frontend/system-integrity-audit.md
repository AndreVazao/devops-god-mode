# System Integrity Audit

## Routes

- `/api/system-integrity-audit/status`
- `/api/system-integrity-audit/package`
- `/api/system-integrity-audit/run`
- `/api/system-integrity-audit/dashboard`
- `/app/system-integrity-audit`

## Objective

Create a local/read-only self-audit layer for the God Mode repository before real executors are connected.

## What it checks

- canonical workflow policy
- route modules with APIRouter
- frontend route modules with docs
- service syntax
- likely service/route linkage issues
- services writing JSON directly
- data-store risk before concurrent execution

## Workflow policy

The project should keep only:

- canonical total test workflow
- prune workflows
- Windows EXE build workflows
- Android APK build workflows

Old phase-specific test workflows should be removed after their phase is merged into canonical coverage.

## Why this matters

The backend auto-loads route modules. A broken route import can stop the whole app. The audit catches this earlier and gives the operator a cockpit-level readiness status.

## Next phase dependency

After this audit is clean enough, the next step should be a common atomic JSON store and then guarded local executors that consume the approved task queue.
