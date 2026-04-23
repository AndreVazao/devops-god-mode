# God Mode operator chat runtime UI

## Objective

Expose a real operator-facing UI that feels like one continuous conversation while reflecting live backend state for approvals, secure input, popup reissue and resumable actions.

## Route

- `/app/operator-chat`

## What the operator sees

- thread list on the left
- pending badge bubbles on conversations
- active conversation header with tenant, thread and pending count
- continuous chat stream in the main pane
- fixed composer at the bottom
- inline state cards for:
  - pending approval gates
  - pending secure input
  - popup reissue after offline gap
  - resumable action replay state

## Behaviour

- selecting a conversation reloads thread state from backend
- pending attention feed reorders conversations by urgency
- secure input can be submitted from modal popup
- approval can be accepted or denied inline
- popup reissue can reopen the request after delivery failure
- resumable actions can be replayed with valid or expired provider session modes

## Notes

This UI is intentionally backend-served for this phase so the operator already has a usable cockpit while the richer standalone frontend continues evolving in later phases.
