# Atomic JSON Store

## Objective

Create a small local-first persistence helper for God Mode JSON stores before real concurrent PC execution starts.

## File

- `backend/app/utils/atomic_json_store.py`

## What it does

- loads JSON files with default fallback
- writes through a temporary file
- fsyncs before replace
- atomically replaces the target file
- keeps a `.bak` backup of the previous valid file
- uses a `.lock` file during read/write operations
- works on Windows and Linux/macOS with platform-specific file locking

## Why this matters

Several God Mode services persist local state in JSON under `data/`. Direct `write_text` is acceptable for early MVP work but risky once the PC executor starts doing concurrent work, because interrupted writes can corrupt state.

## Integration started

The system integrity audit now saves its report through `AtomicJsonStore` and checks for writers that still need migration.

## Migration rule

Critical runtime stores should move from direct JSON `write_text` to `AtomicJsonStore` before enabling real write executors.
