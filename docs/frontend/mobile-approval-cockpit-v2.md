# Mobile approval cockpit v2

## Routes

- `/api/mobile-approval-cockpit-v2/status`
- `/api/mobile-approval-cockpit-v2/package`
- `/api/mobile-approval-cockpit-v2/cards`
- `/api/mobile-approval-cockpit-v2/decide`
- `/api/mobile-approval-cockpit-v2/seed-from-latest-command`
- `/api/mobile-approval-cockpit-v2/seed-from-deploy-readiness`
- `/api/mobile-approval-cockpit-v2/dashboard`
- `/app/mobile-approval-cockpit-v2`

## Objective

Create a mobile-first approval cockpit where the PC local brain can ask the operator for decisions while work continues in the background.

## What it does

- creates chat-style cards for the phone
- supports approval, rejection, acknowledgement and change requests
- links cards to project IDs and source refs
- can seed approval cards from the latest operator command
- can seed deploy/env readiness cards from Phase 29 reports
- avoids exposing secret values
- stores decisions locally for later execution phases

## Card types

- `operator_command`
- `secret_binding_approval`
- `provider_login_request`
- `destructive_action_guard`
- `deploy_env_sync_approval`
- `pr_write_approval`
- `progress_update`

## Next phase dependency

The next phase should consume approved cards and turn them into safe execution tasks: provider env sync, PR write approval, deploy preparation and local PC background execution.
