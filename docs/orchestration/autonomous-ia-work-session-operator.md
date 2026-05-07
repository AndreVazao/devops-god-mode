# Autonomous IA Work Session Operator + Provider Work Pack Queue

## Objetivo

A Phase 204 permite que o God Mode continue trabalho com IAs quando o Oner está ausente, na rua ou ocupado.

O God Mode cria sessões de trabalho, work packets por provider, prompts controlados, contratos de envio/captura manual e importação de respostas. O objetivo é o God Mode fazer andar trabalho e só chamar o Oner para decisões bloqueantes ou de risco.

## Endpoint principal

```txt
/api/autonomous-ia-work-session/package
```

## Página visual

```txt
/app/autonomous-ia-work-session
/app/ia-work-operator
```

## Endpoints

- `/api/autonomous-ia-work-session/status`
- `/api/autonomous-ia-work-session/policy`
- `/api/autonomous-ia-work-session/create-session`
- `/api/autonomous-ia-work-session/create-work-packet`
- `/api/autonomous-ia-work-session/create-packets-from-self-diagnosis`
- `/api/autonomous-ia-work-session/mark-packet-status`
- `/api/autonomous-ia-work-session/import-response`
- `/api/autonomous-ia-work-session/convert-response-to-tasks`
- `/api/autonomous-ia-work-session/create-provider-launcher-contract`
- `/api/autonomous-ia-work-session/packets`
- `/api/autonomous-ia-work-session/dashboard`
- `/api/autonomous-ia-work-session/package`

## Estados de work packet

- `drafted`
- `ready_to_send`
- `waiting_response`
- `response_imported`
- `converted_to_tasks`
- `blocked_needs_oner`
- `cancelled`

## O que faz

- Cria `ia_work_session`.
- Cria `ia_work_packet` por provider.
- Gera prompt controlado e sanitizado.
- Cria packets a partir do self-diagnosis queue.
- Permite importar resposta IA para Conversation Source Import Feed.
- Converte resposta importada em tarefas de revisão.
- Cria contrato de provider launcher sem login automático.
- Separa trabalho seguro de decisões que exigem Oner.

## Segurança

- `can_operate_while_oner_busy=true`.
- `can_send_without_manual_provider_gate=false`.
- `can_login_or_scrape_private_chats=false`.
- `can_merge_without_oner_approval=false`.
- Não guarda tokens, passwords, cookies, API keys ou segredos.
- Não automatiza login privado.
- Não faz scrape de conversas privadas.
- Não chama APIs pagas sem aprovação.
- Não faz merge/release/deploy autónomo.

## Fluxo recomendado

```txt
God Mode Self Diagnosis
→ self_fix_queue_item
→ Autonomous IA Work Session
→ ia_work_packet
→ provider manual/gated send/capture
→ import-response
→ Conversation Source Import Feed
→ convert-response-to-tasks
→ futuro PR planning
→ GitHub Actions
→ aprovação Oner quando necessário
```

## Regra para Oner ocupado/na rua

O God Mode deve preparar trabalho e manter o estado. O Oner não deve ter de interagir enquanto conduz.

Quando houver risco, o packet fica `blocked_needs_oner` ou cria card mobile para revisão posterior.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 203 deve ser apagado. Fica só:

- `.github/workflows/phase204-autonomous-ia-work-session-operator-smoke.yml`

Além dos workflows globais/builds.
