# God Mode approval and operator input UX

## Objective

The frontend must support popup-style approvals and operator-entered sensitive values that are transcribed into backend-controlled flows.

## Required behaviour

- when a gated action is created, show a popup with:
  - action label
  - risk level
  - short payload summary
  - buttons for `Approve` and `Deny`
- when an operator input request is created, show a popup or inline modal with:
  - title
  - prompt text
  - field label
  - secure input when `is_sensitive=true`
- after submit, the UI must send the value to the backend and clear the visible field immediately
- operator-entered values should never remain rendered in plain text after submission

## Interaction model

1. God Mode creates an approval gate or input request
2. frontend polls or refreshes the active thread context
3. popup appears inline with the running conversation
4. operator approves, denies, or types the requested value
5. backend records the decision or masked submission
6. God Mode continues the same conversational thread

## Endpoints

- `/api/operator-approval-gate/create`
- `/api/operator-approval-gate/resolve`
- `/api/operator-input-request/create`
- `/api/operator-input-request/submit`
- `/api/operator-conversation-thread/*`
- `/api/operator-response-guidance/build`

## UX notes

- approvals should feel similar to explicit tool confirmations
- sensitive input should feel like a secure popup handed to the backend bridge
- the operator must always know which tenant and provider the popup belongs to
- after acceptance or input, the same conversation continues without opening a new workflow screen
