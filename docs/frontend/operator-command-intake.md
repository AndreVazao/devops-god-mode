# Operator command intake

## Routes

- `/api/operator-command-intake/status`
- `/api/operator-command-intake/package`
- `/api/operator-command-intake/submit`
- `/api/operator-command-intake/commands`
- `/api/operator-command-intake/projects`
- `/app/operator-command-intake`

## Objective

Create the first natural-command entry layer for the God Mode cockpit. This is the bridge between the operator speaking on the phone and the local PC brain turning that request into structured work.

## What it does

- receives raw operator text from mobile chat or PC cockpit
- detects project target and command intent
- classifies urgency and destructive risk
- extracts provider and repo role hints
- links command to project memory
- reads Project Bootstrap readiness
- creates an initial approval-aware execution plan
- stores command history and project memory locally

## Example

Command:

> Audita o Baribudos Studio e o Website, vê o que está partido e prepara PRs com aprovação.

Expected output:

- project: `baribudos-studio`
- intent: `deep_project_audit`
- priority: `high`
- repo roles: `studio`, `website`
- execution plan with repository mapping, file scan, fix plan and mobile approval reporting

## Next phase dependency

This phase feeds the future multi-AI conversation inventory and repo graph audit planner. It does not yet log into external AI providers or modify repos by itself; it produces the structured operational command that those later phases will execute.
