# Request Orchestrator

## Cockpit

- `/app/request-orchestrator`

## API

- `GET /api/request-orchestrator/status`
- `GET /api/request-orchestrator/package`
- `GET /api/request-orchestrator/dashboard`
- `GET /api/request-orchestrator/jobs`
- `GET /api/request-orchestrator/job/{job_id}`
- `POST /api/request-orchestrator/submit`
- `POST /api/request-orchestrator/resume`
- `POST /api/request-orchestrator/run/{job_id}`

## Chat integration

- `POST /api/chat-inline-card-renderer/send-orchestrated`

## Objetivo

Permitir que o operador dê ordens em linguagem normal e que o backend execute o processo até ao fim ou até chegar a um bloqueio que exige intervenção humana.

O APK pode desligar. O job fica guardado no backend em `data/request_orchestrator.json`.

## Regras principais

- O operador dá a ordem no chat.
- O backend cria um job durável.
- O backend executa todos os passos automáticos seguros.
- O backend só pára quando precisa de:
  - aprovação explícita;
  - login manual num provider externo;
  - input manual que não deve ser guardado.
- Credenciais e valores sensíveis nunca devem ser guardados.
- Quando o operador aprova ou confirma, o job pode ser retomado.

## Estados de job

- `queued`
- `running`
- `blocked_approval`
- `blocked_credentials`
- `blocked_manual_input`
- `completed`
- `failed`

## Intents iniciais

- `money_flow`
- `provider_handoff`
- `build_or_publish`
- `controlled_execution`
- `general_backend_request`

## Bloqueios

### Aprovação

Quando o backend chega a um passo que precisa do OK do operador, cria:

- card no Mobile Approval Cockpit;
- card inline no chat;
- estado `blocked_approval` no job.

### Login/provider

Quando o backend precisa que o operador faça login num provider, cria:

- request de credencial manual;
- card no Mobile Approval Cockpit;
- card inline no chat;
- estado `blocked_credentials` no job.

O operador deve fazer login diretamente no provider. Não deve escrever passwords, tokens, cookies ou keys no chat.

## Retomar job

Depois do OK/login/input manual:

- `POST /api/request-orchestrator/resume`

O backend marca o passo bloqueado como concluído e continua até novo bloqueio ou conclusão.

## Segurança

Esta fase não adiciona execução livre. Ela cria o motor persistente, estados, bloqueios e integrações com aprovações/cartões. Execuções reais sensíveis continuam dependentes de aprovação explícita.
