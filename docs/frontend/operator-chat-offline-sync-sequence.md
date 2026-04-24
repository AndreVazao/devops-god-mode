# Operator chat offline sync sequence

## Goal

Document the exact behaviour expected when the operator is working in the sync cockpit and connectivity drops or comes back.

## Sequence

### 1. Operator is online
- frontend polls the runtime snapshot API
- thread list, badges and inline cards are rebuilt from snapshot data
- user actions are sent immediately to backend

### 2. Connectivity drops
- UI switches to offline state
- latest snapshot stays visible from local cache
- new operator actions are written to the local queue
- the conversation still shows those queued actions inline so the operator does not lose context

### 3. Connectivity returns
- UI switches back to online state
- local queue starts flushing automatically
- queued message appends and queued secure input submissions are replayed first
- once the queue is flushed, the frontend fetches a fresh runtime snapshot
- badges, popup state and resumable state are rebuilt from the new server truth

## Important rules

- the operator must never lose the active thread context
- local queued actions should remain visible until confirmed flushed
- cached state is a temporary visual fallback, not the source of truth
- after reconnect, the snapshot becomes authoritative again
