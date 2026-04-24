# Mission Control Cockpit

## Routes

- `/api/mission-control/status`
- `/api/mission-control/package`
- `/api/mission-control/dashboard`
- `/api/mission-control/command`
- `/app/mission-control`

## Objective

Create one mobile-first cockpit that makes God Mode easier to use by merging the most important operational surfaces into a single screen.

## What it aggregates

- AndreOS Memory Core project readiness
- Operator Command Intake
- Mobile Approval Cockpit pending approvals
- Approved Card Execution Queue
- System Integrity Audit
- PROJECT_TREE sync guard

## Main operator flow

1. Choose the active project.
2. Type or dictate a command.
3. Mission Control sends it to Operator Command Intake.
4. Operator Command Intake loads AndreOS project memory.
5. Mission Control creates a mobile approval card.
6. The operator approves or rejects.
7. The decision is persisted to the Obsidian-compatible memory.

## UX goal

One simple screen with:

- readiness traffic light
- quick command box
- project memory score cards
- pending approval and queue counters
- quick links to Memory, Approvals and Audit

## Safety

Mission Control does not bypass approval. It creates cards and keeps destructive or sensitive actions behind approval gates.
