# Vault-aware deploy env planner

## Routes

- `/api/vault-deploy-env-planner/status`
- `/api/vault-deploy-env-planner/package`
- `/api/vault-deploy-env-planner/secret-presence`
- `/api/vault-deploy-env-planner/project-env-manifest`
- `/api/vault-deploy-env-planner/readiness-report`
- `/api/vault-deploy-env-planner/readiness-reports`
- `/api/vault-deploy-env-planner/dashboard`
- `/api/vault-deploy-env-planner/seed-demo-baribudos-secrets`
- `/app/vault-deploy-env-planner`

## Objective

Create the vault-aware deployment and environment planning layer between the repo graph and future real deploy/build execution.

This phase does not expose secret values and does not deploy. It only tracks secret presence, expected environment variables and readiness blockers.

## What it does

- reads project/repo roles and deploy targets from the repo relationship graph
- derives required env vars from provider targets such as Vercel, Render, Supabase and GitHub Actions
- derives required env vars from repo roles such as website, frontend, backend, studio and vault
- separates public env vars from secret vault values
- registers secret presence without storing secret values
- builds project env manifests
- builds deployment readiness reports
- creates approval steps before provider env sync

## Example: Baribudos Studio

For the Baribudos Studio graph, expected requirements can include:

- `GITHUB_TOKEN`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_API_URL`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `ADMIN_BASE_URL`
- `SECRET_VAULT_NAMESPACE`

Public variables can be shown safely. Secret variables are tracked only as present/missing.

## Next phase dependency

The next phase should turn approved readiness reports into provider-specific env sync and build/deploy preparation without revealing secret values in logs or UI.
