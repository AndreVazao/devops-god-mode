# Multi-AI conversation inventory

## Routes

- `/api/multi-ai-conversation-inventory/status`
- `/api/multi-ai-conversation-inventory/package`
- `/api/multi-ai-conversation-inventory/stage`
- `/api/multi-ai-conversation-inventory/seed-from-command`
- `/api/multi-ai-conversation-inventory/conversations`
- `/api/multi-ai-conversation-inventory/project-map`
- `/api/multi-ai-conversation-inventory/dashboard`
- `/app/multi-ai-conversation-inventory`

## Objective

Create the local-first inventory layer for conversations captured from multiple AI providers.

This phase does not yet scrape provider accounts. It defines the storage, mapping and cockpit surface that browser/session bridges can feed later.

## Supported providers

- ChatGPT
- Claude
- Gemini
- Grok
- DeepSeek
- Unknown/manual seed

## What it does

- stages captured conversation snippets
- normalizes provider names
- guesses target project
- extracts repo roles such as website, studio, backend, frontend, mobile, workflow and vault
- extracts language hints
- builds project map conversation -> project -> provider -> repo role
- can seed inventory from an operator command created in Phase 26
- exposes a cockpit view for recent conversations and detected project groups

## Example target flow

1. Operator says: `Audita o Baribudos Studio e o Website`.
2. Phase 26 creates a structured operator command.
3. Phase 27 can seed that command into the conversation inventory.
4. Later browser/session phases will add real ChatGPT, Claude, Gemini, Grok and DeepSeek conversations into the same project map.

## Next phase dependency

This feeds the repo relationship graph and deep audit planner. Once conversations are grouped by project and repo role, the next layer can map them to actual GitHub repositories and plan a deep audit.
