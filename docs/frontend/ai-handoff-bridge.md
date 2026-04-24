# AI Handoff Bridge

## Routes

- `/api/ai-handoff/status`
- `/api/ai-handoff/package`
- `/api/ai-handoff/dashboard`
- `/api/ai-handoff/handoffs`
- `/api/ai-handoff/handoffs/{handoff_id}`
- `/api/ai-handoff/from-latest-unknown`
- `/api/ai-handoff/from-unknown`
- `/api/ai-handoff/resolve`
- `/app/ai-handoff`

## Objective

When the Learning Router cannot understand an operator message, the AI Handoff Bridge prepares a provider-ready prompt for ChatGPT, Gemini, Claude, Grok or DeepSeek.

## Flow

1. Learning Router stores an unknown message.
2. AI Handoff Bridge creates a handoff from that unknown.
3. The bridge builds a prompt with compact AndreOS project memory.
4. A Mobile Approval card is created before external provider use.
5. The operator can copy the prompt and open the provider.
6. The operator pastes the provider response back into God Mode.
7. If approved, the phrase can teach the Learning Router.
8. The resolution is logged into AndreOS Memory Core.

## Safety

This phase does not automate browser control or provider login. It prepares prompts and approval cards. Secrets must never be pasted into providers or stored in Obsidian memory.

## Future

A later phase can connect this to a browser provider bridge for controlled web automation, still behind explicit approval.
