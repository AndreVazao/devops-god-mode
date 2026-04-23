# God Mode resumable offline replay UX

## Objective

If the operator fills a popup while offline, the input must be queued locally and replayed to the backend on the next sync. If the provider flow expired in the meantime, God Mode must restart from the latest safe checkpoint and then continue the original purpose.

## Required behaviour

- popup input can be submitted locally even when network is unavailable
- local UI stores a pending submission linked to the conversation thread
- after reconnect, the pending submission is synced to the backend automatically
- if the provider session is still valid, God Mode resumes from the latest safe checkpoint
- if the provider session expired, God Mode restarts the provider flow and reapplies the operator intent
- the operator should see this as one continuous conversation

## Backend endpoints

- `/api/operator-resumable-action/create`
- `/api/operator-resumable-action/submit-offline-sync`
- `/api/operator-resumable-action/resume`
- `/api/operator-pending-attention/feed`

## Status model

- `waiting_operator_sync`
- `sync_received_pending_resume`
- `resumed_from_checkpoint`
- `restarted_for_fresh_session`
- `provider_session_expired_restart_required`

## UX notes

- the conversation row should keep its badge until the replay finishes
- after replay, the thread should show whether the provider flow resumed or restarted
- the operator should see the purpose summary, not a low-level technical error wall
