# God Mode undelivered popup reissue UX

## Objective

If the backend creates a popup but the operator never receives it because the device is offline, the intent must remain alive. On the next sync, the system should reissue the popup inside the same conversation and continue from the latest safe checkpoint.

## Required behaviour

- popup creation and popup delivery are separate states
- a popup may exist in `pending_delivery` even if the operator never saw it
- when sync returns, undelivered popups should be reissued automatically
- the conversation row should keep its pending badge until the popup is delivered and answered
- the active conversation should explain that the previous popup was reissued after an offline gap

## Backend endpoints

- `/api/operator-popup-delivery/create`
- `/api/operator-popup-delivery/mark-delivered`
- `/api/operator-popup-delivery/reissue`
- `/api/operator-popup-delivery/acknowledge-response`
- `/api/operator-pending-attention/feed`
- `/api/operator-resumable-action/*`

## Status model

- `pending_delivery`
- `delivered_waiting_operator`
- `reissue_required`
- `operator_response_acknowledged`

## UX notes

- do not show the operator a technical failure wall when the popup was never delivered
- show a clear inline message like: `Ligação interrompida. O pedido foi reenviado.`
- keep the thread continuous instead of spawning a separate workflow screen
- after the operator answers the reissued popup, continue the original intent in the same conversation
