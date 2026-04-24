# God Mode operator chat sync runtime UI

## Route

- `/app/operator-chat-sync`

## Objective

Provide an operator-facing cockpit that reconstructs itself from the runtime snapshot API, keeps a small local queue for offline actions, and resynchronizes automatically when connectivity returns.

## Key behaviour

- snapshot-driven polling
- local cache fallback when backend is unavailable
- local queue for offline message append and sensitive input submission
- automatic flush on reconnect
- pending badge continuity in the thread list
- popup reissue and resumable replay reflected inline in the same conversation

## Why this phase matters

This gives the operator a more resilient working surface while keeping the same backend model introduced in the earlier phases.
