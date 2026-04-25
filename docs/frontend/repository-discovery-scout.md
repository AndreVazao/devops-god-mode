# Repository Discovery Scout

## Routes

- `/api/repository-discovery/status`
- `/api/repository-discovery/package`
- `/api/repository-discovery/dashboard`
- `/api/repository-discovery/plan/{project_id}`
- `/api/repository-discovery/candidates`
- `/api/repository-discovery/candidates/confirm`
- `/api/repository-discovery/proposal`
- `/api/repository-discovery/audit/{project_id}`
- `/app/repository-discovery`

## Objective

Help God Mode discover whether portfolio projects already have repositories/apps or whether a new repository should be proposed with explicit operator approval.

## Why it matters

Projects such as Bot Factory may exist under old names or may not have a repo yet. This cockpit creates a safe, auditable process before creating anything new.

## Flow

1. Pick a project.
2. Generate a search plan with likely repo names.
3. Add candidate repositories manually or from future GitHub scans.
4. Confirm a candidate to link it into Project Portfolio.
5. If no repo exists, generate a proposal for a new repo.
6. Record decisions and history in AndreOS Memory Core.

## Bot Factory search terms

- bot-factory
- good-factory
- botfactory
- bot-generator
- reverse-engineering-bots
- game-bot-factory
- factory

## Safety

Repository Discovery Scout does not create repos automatically. It only proposes new repos and links confirmed candidates.
