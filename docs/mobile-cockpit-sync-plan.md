# Mobile Cockpit Sync Plan

## Branch
- `feature/mobile-command-bridge`

## Objective
Add a local first sync layer so the mobile cockpit can send requests to the PC runtime and receive compact results back without relying on cloud runtime as the primary path.

## Scope
- represent incoming mobile requests
- represent compact result sync back to mobile
- expose a compact package for the cockpit
- expose the next sync action
