# Memory Core Cockpit

## Routes

- `/api/memory-core/status`
- `/api/memory-core/package`
- `/api/memory-core/initialize`
- `/api/memory-core/projects`
- `/api/memory-core/projects/{project_name}`
- `/api/memory-core/decisions`
- `/api/memory-core/history`
- `/api/memory-core/last-session`
- `/api/memory-core/backlog`
- `/api/memory-core/context/{project_name}`
- `/api/memory-core/obsidian/{project_name}/{file_name}`
- `/app/memory-core`

## Objective

Expose the AndreOS Memory Core in the God Mode cockpit and API.

## What it does

- initializes the Obsidian-compatible memory structure
- creates project memory folders
- reads project memory
- logs decisions
- logs history
- updates last session
- adds backlog tasks
- builds compact AI context
- creates Obsidian deep links
- blocks sensitive keyword storage
