# God Mode offline pending attention UX

## Objective

When the operator goes offline, pending approvals or pending sensitive input requests must not disappear. The next sync should surface them clearly in the conversation list and inside the active thread.

## Required behaviour

- each conversation row can show a badge bubble when action is pending
- badge count equals pending approvals plus pending input requests for that thread
- after reconnect or refresh, the feed should restore pending state immediately
- the active conversation should show the same pending items inline
- the operator must know which tenant the pending action belongs to

## Backend endpoint

- `/api/operator-pending-attention/feed?tenant_id=<tenant_id>`

## Conversation list rules

- show bubble on the thread row when `has_pending_attention=true`
- show the latest summary under the title
- keep the conversation list similar to a normal chat inbox
- pending rows should sort above fully idle rows when useful

## Active thread rules

- pending approval gate should render as actionable popup or inline card
- pending input request should reopen as secure popup or inline modal
- after resolve or submit, refresh the feed and remove the bubble

## Offline behaviour

- local UI may cache the last known pending state
- on reconnection, backend feed is source of truth
- if several actions are pending, the bubble count should show the total
