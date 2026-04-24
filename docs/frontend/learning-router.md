# Learning Router

## Routes

- `/api/learning-router/status`
- `/api/learning-router/package`
- `/api/learning-router/dashboard`
- `/api/learning-router/route`
- `/api/learning-router/learn`
- `/api/learning-router/unknowns`
- `/app/learning-router`

## Objective

Let the operator talk naturally. If God Mode understands the message, it routes it to Mission Control. If confidence is low, it stores the utterance as unknown for later correction or external AI interpretation.

## Learning model

This is not opaque machine learning. It is an explainable adaptive router:

- keyword intent scoring
- learned phrase patterns
- confidence score
- unknown utterance capture
- operator correction through `/learn`
- history persisted in AndreOS Memory Core

## Supported intents

- `continue_project`
- `deep_audit`
- `build_check`
- `memory_review`
- `fix_plan`
- `delivery_summary`

## Safety

The router never bypasses approval. Confident messages are submitted to Mission Control, which still creates approval cards for execution flows.

## Future bridge

Unknown messages can later be forwarded to a browser provider bridge for interpretation by ChatGPT web or other AI provider, then converted into a learned pattern after operator approval.
