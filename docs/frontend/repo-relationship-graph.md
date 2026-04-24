# Repo relationship graph and audit planner

## Routes

- `/api/repo-relationship-graph/status`
- `/api/repo-relationship-graph/package`
- `/api/repo-relationship-graph/repositories`
- `/api/repo-relationship-graph/seed-from-conversation-inventory`
- `/api/repo-relationship-graph/seed-demo-baribudos`
- `/api/repo-relationship-graph/graph`
- `/api/repo-relationship-graph/dashboard`
- `/api/repo-relationship-graph/audit-plan`
- `/api/repo-relationship-graph/audit-plans`
- `/app/repo-relationship-graph`

## Objective

Create the relationship graph between projects, conversations and GitHub repositories, then generate a deep audit plan before any real write operation.

## What it does

- stores repositories linked to projects
- detects repo roles such as website, studio, backend, frontend, mobile, workflow and vault
- infers stack hints such as Python, FastAPI, TypeScript, Next.js, GitHub Actions and Supabase
- imports project links from the Phase 27 multi-AI conversation inventory
- keeps project links with conversation IDs, providers and repo roles
- generates read-only deep audit plans
- marks repair/fix PR generation as approval-gated
- exposes a cockpit view in `/app/repo-relationship-graph`

## Example: Baribudos Studio

The demo seed links two repos to the same project:

- `AndreVazao/baribudos-studio` as studio/backend/frontend/vault
- `AndreVazao/baribudos-studio-website` as website/frontend/workflow

This models the desired real-world relationship: the Studio cockpit controls and feeds the Website, but both repos belong to the same product.

## Audit plan shape

Each repo receives a sequence of read-only checks:

- file inventory
- dead/duplicate file scan
- imports/routes/contracts scan
- workflow/build scan
- frontend audit when applicable
- backend/env/vault audit when applicable
- approval-gated fix PR plan

## Next phase dependency

The next phase should connect this graph to vault-aware deployment/environment planning so the God Mode can understand required secrets, env vars, Vercel/Render/Supabase targets and build readiness before proposing PRs or deploys.
