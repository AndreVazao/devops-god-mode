# Operator chat action journal

## Objective

Give the operator and the frontend a structured operational trail of what happened in each conversation thread.

## What the journal is for

The action journal is meant to answer, in plain operational terms:

- what entered the local queue
- what was synchronized later
- what failed
- what was replayed
- what required restart because the provider session expired

## Backend routes

- `/api/operator-action-journal/status`
- `/api/operator-action-journal/list`
- `/api/operator-action-journal/log`

## Runtime snapshot integration

The runtime snapshot now includes:

- tenant-level recent journal entries
- thread-level recent journal entries

This allows the frontend to rebuild not only the current chat and pending actions, but also the operational history that explains how the system arrived at the present state.

## Why this matters

This is a key visibility layer for real use. Without it, the operator sees only the current state. With it, the operator can understand the sequence of sync, replay, restart and recovery events.
