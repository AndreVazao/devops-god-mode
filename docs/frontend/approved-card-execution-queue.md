# Approved card execution queue

## Routes

- `/api/approved-card-execution-queue/status`
- `/api/approved-card-execution-queue/package`
- `/api/approved-card-execution-queue/ingest-approved-cards`
- `/api/approved-card-execution-queue/tasks`
- `/api/approved-card-execution-queue/tasks/status`
- `/api/approved-card-execution-queue/dashboard`
- `/app/approved-card-execution-queue`

## Objective

Consume approved/acknowledged cards from the Mobile Approval Cockpit v2 and convert them into safe, auditable PC-local execution tasks.

## What it does

- reads approved/acknowledged cards
- avoids double-processing the same card
- converts card types into deterministic task steps
- applies guardrails to every task
- tracks queued/running/blocked/completed/failed/cancelled status
- exposes queue dashboard for the operator

## Guardrails

- never expose secret values
- never execute destructive actions without secondary confirmation
- write actions require executor guard
- progress must be reported back to mobile

## Limit

This phase queues safe task bundles. It still does not perform real external writes. Future executor phases should consume this queue and run provider/repo actions under guards.
