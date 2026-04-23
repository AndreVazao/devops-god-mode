# God Mode operator conversation UX

## Objective

The operator-facing frontend must feel like one continuous conversation instead of isolated command cards.

## Required behaviour

- render the main interaction as a running threaded conversation
- allow the operator to keep typing naturally while God Mode preserves tenant context
- show visible operational replies after each operator message
- surface suggested next steps under the latest God Mode reply
- keep tenant context visible at the top of the conversation
- keep provider context visible whenever a provider onboarding or deploy flow is active

## Message model

Each message should show:

- role (`user` or `god_mode`)
- content
- operational state (`active`, `waiting_login`, `processing`, `blocked`, `ready`)
- timestamp
- suggested next steps when present

## Mobile-first notes

- input stays pinned to the bottom
- conversation scroll stays continuous like a chat app
- latest state summary stays visible without hiding the thread
- operator can switch tenant explicitly before sending new work

## Backend endpoints to use

- `/api/operator-conversation-thread/open`
- `/api/operator-conversation-thread/append`
- `/api/operator-conversation-thread/get/{thread_id}`
- `/api/operator-response-guidance/build`
- `/api/tenant-provider-onboarding/build`
- `/api/tenant-browser-onboarding-executor/execute-first-run-capture`
- `/api/tenant-multirepo-linkage/build`

## Expected flow

1. open operator thread for a tenant
2. append operator message
3. request response guidance
4. display the running reply and next-step hints
5. when provider login is needed, show that inline in the same conversation
6. after login, continue the same thread without splitting the operator experience
