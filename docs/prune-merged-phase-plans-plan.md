# Prune Merged Phase Plans Plan

## Branch
- `feature/big-docs-workflow-prune`

## Objective
Remove merged phase plan documents and stale cleanup workflow files that no longer add operational value in the main tree.

## Scope
- remove old remote/mobile phase plan docs already absorbed into the codebase history
- remove merged cleanup plan docs that only described one-off cleanup batches
- remove stale cleanup workflow files that were temporary validation scaffolding

## Expected Result
- smaller `docs/` surface
- less maintenance noise in `.github/workflows/`
- faster navigation through the real runtime files that still matter
