# Project Tree Autorefresh

## Routes

- `/api/project-tree-autorefresh/status`
- `/api/project-tree-autorefresh/package`
- `/api/project-tree-autorefresh/dashboard`
- `/api/project-tree-autorefresh/current`
- `/api/project-tree-autorefresh/generated`
- `/api/project-tree-autorefresh/compare`
- `/api/project-tree-autorefresh/write`
- `/app/project-tree-autorefresh`

## Objective

Keep `PROJECT_TREE.txt` aligned with the real repository structure so phase work does not drift.

## Why it matters

The operator manually had to fix the tree after merges. This module gives God Mode a cockpit and API to compare current tree versus generated tree before opening or merging future phases.

## Flow

1. Generate tree from the local repository filesystem.
2. Read current `PROJECT_TREE.txt`.
3. Compare missing and obsolete lines.
4. Show differences in cockpit.
5. Only overwrite with explicit `allow_overwrite=true`.

## Safety

The write endpoint refuses to overwrite by default. This prevents accidental tree replacement without explicit approval.

## Phase rule

Whenever a phase adds or removes files, update `PROJECT_TREE.txt` in the same PR or use this cockpit to detect drift.
