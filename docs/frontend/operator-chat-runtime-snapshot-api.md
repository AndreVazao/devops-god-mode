# Operator chat runtime snapshot API

## Objective

Give the operator chat frontend a single polling endpoint that summarizes the current tenant and active thread state without forcing the UI to orchestrate many separate calls every refresh cycle.

## Route

- `/api/operator-chat-runtime-snapshot/snapshot?tenant_id=<tenant_id>&thread_id=<thread_id>`

## What comes back

- conversation threads for the tenant
- pending attention feed
- active thread payload when `thread_id` is provided
- response guidance for the active thread
- input requests for the active thread
- approval gates for the active thread
- popup deliveries for the active thread
- resumable actions for the active thread

## Why this matters

This helps the operator UI stay responsive and more robust during reconnect cycles, because the frontend can rebuild most of the screen from one snapshot response.
