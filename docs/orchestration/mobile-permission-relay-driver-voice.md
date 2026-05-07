# Mobile Permission Relay + Driver Voice Mode + Offline Resend Queue

## Objetivo

A Phase 205 implementa o contrato central de operação real:

- cérebro do God Mode no PC de casa;
- telemóvel como cockpit/popup de permissão;
- modo condução por voz;
- espera no PC até resposta;
- reenvio/sincronização se o telemóvel estiver sem rede/túnel;
- pedidos sensíveis com formulário, sem guardar segredo bruto.

## Endpoint principal

```txt
/api/mobile-permission-relay/package
```

## Página visual

```txt
/app/mobile-permission-relay
/app/driver-voice-permissions
```

## Endpoints

- `/api/mobile-permission-relay/status`
- `/api/mobile-permission-relay/policy`
- `/api/mobile-permission-relay/create-request`
- `/api/mobile-permission-relay/mark-sent`
- `/api/mobile-permission-relay/mark-delivered`
- `/api/mobile-permission-relay/mark-offline-wait`
- `/api/mobile-permission-relay/mark-resend-pending`
- `/api/mobile-permission-relay/decide`
- `/api/mobile-permission-relay/voice-event`
- `/api/mobile-permission-relay/poll`
- `/api/mobile-permission-relay/wait-status/{permission_request_id}`
- `/api/mobile-permission-relay/dashboard`
- `/api/mobile-permission-relay/package`

## Estados

- `queued`
- `sent`
- `delivered`
- `acknowledged`
- `approved`
- `rejected`
- `expired`
- `resend_pending`
- `offline_wait`

## Tipos de pedido

- `approval`
- `login_manual`
- `sensitive_fill`
- `pause_continue`
- `blocking_decision`
- `voice_confirm`
- `credential_prompt`

## Integração com o que já existia

Esta fase reutiliza `mobile_approval_cockpit_v2_service.py`.

Não duplica o cockpit de approvals. O relay cria permission requests e também cria cards no mobile approval cockpit quando faz sentido.

## Contrato real

```txt
PC God Mode brain
→ precisa de autorização / login / preenchimento / decisão
→ cria permission_request
→ cria mobile card / popup contract
→ cria wait_lock
→ mobile poll recebe pedido
→ Oner aprova/rejeita/preenche/fala
→ PC recebe decisão
→ wait_lock liberta ou bloqueia
→ tarefa continua ou fica bloqueada
```

## Offline / túnel / sem rede

Se o telemóvel estiver sem rede:

```txt
permission_request
→ offline_wait
→ resend_pending
→ poll quando rede volta
→ delivered
→ approved/rejected
→ PC resume
```

## Modo condução / voz

O modo condução deve:

- aceitar comandos curtos por voz;
- falar respostas curtas;
- evitar toque enquanto o Oner conduz;
- pedir para parar em segurança quando há credenciais ou texto sensível.

Exemplos:

```txt
"aprovar continua"
"rejeita isso"
"pausa"
"recebido"
```

## Segurança

- `can_resend_after_offline=true`.
- `supports_driver_voice_mode=true`.
- `can_store_raw_secrets=false`.
- `can_unlock_sensitive_action_without_oner=false`.
- Não guarda passwords/tokens/cookies/API keys.
- Não força interação enquanto o Oner conduz.
- Não faz autofill sensível sem gate/vault.
- Não faz merge/release/deploy/pagamentos sem aprovação.

## Próxima ligação necessária

A próxima fase deve ligar diretamente:

```txt
Autonomous IA Work Session Operator
→ Mobile Permission Relay
→ Provider Launcher / resposta IA / credential prompt / wait mode
```

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 204 deve ser apagado. Fica só:

- `.github/workflows/phase205-mobile-permission-relay-driver-voice-smoke.yml`

Além dos workflows globais/builds.
