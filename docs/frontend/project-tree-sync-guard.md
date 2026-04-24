# Project Tree Sync Guard

## Routes

- `/api/project-tree-sync-guard/status`
- `/api/project-tree-sync-guard/package`
- `/api/project-tree-sync-guard/dashboard`
- `/api/project-tree-sync-guard/check`
- `/app/project-tree-sync-guard`

## Objective

Keep `PROJECT_TREE.txt` synchronized with repository structure after every structural change.

## Rule

Whenever a file is created, deleted, moved or renamed, `PROJECT_TREE.txt` must be updated in the same branch/PR.

## Why this matters

`PROJECT_TREE.txt` is the operator-facing structural map. It lets God Mode and the operator understand what kind of project exists, what modules are present, what is missing and where the next audit should focus.

## What it checks

- whether `PROJECT_TREE.txt` exists
- generated tree line count
- committed tree line count
- lines missing from committed tree
- stale lines still present in committed tree

## Workflow policy

This phase also follows the cleanup rule:

- delete the previous phase temporary workflow first
- create only the current phase temporary workflow
- delete this workflow at the start of the next phase
