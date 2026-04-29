# Resumable Job Checkpoint Engine

## Objetivo

A Phase 134 adiciona um motor genérico de jobs retomáveis com checkpoints.

Isto é crítico para o God Mode trabalhar durante tarefas longas e continuar/retomar quando acontecer:

- APK desligado;
- net em baixo;
- provider limitado;
- sessão browser perdida;
- PC reiniciado;
- trabalho pausado;
- login manual necessário;
- aprovação necessária;
- validação falhada.

## Endpoints

- `GET/POST /api/resumable-jobs/status`
- `GET/POST /api/resumable-jobs/panel`
- `GET/POST /api/resumable-jobs/policy`
- `POST /api/resumable-jobs/create`
- `POST /api/resumable-jobs/checkpoint`
- `POST /api/resumable-jobs/stop`
- `POST /api/resumable-jobs/resume-plan`
- `POST /api/resumable-jobs/resume`
- `POST /api/resumable-jobs/complete`
- `GET/POST /api/resumable-jobs/latest`
- `GET/POST /api/resumable-jobs/package`

## Política

- Criar job antes de trabalho longo.
- Guardar checkpoint depois de cada passo seguro.
- Guardar stop reason quando parar.
- Não guardar tokens, passwords, cookies, API keys ou secrets.
- Retomar do último checkpoint `safe_to_resume=true`.
- Se houver hard stop, exigir operador.
- Se terminar, congelar estado final.

## Stop reasons seguros

- `apk_disconnected`
- `network_offline`
- `provider_rate_limited`
- `browser_session_lost`
- `pc_restarted`
- `job_paused_by_operator`
- `needs_operator_login`
- `needs_operator_ok`
- `validation_failed`
- `work_completed`

## Hard stops

- `unsafe_or_sensitive_request`
- `destructive_action_without_approval`
- `secret_detected`
- `unknown_critical_error`

## Fluxo esperado

1. `/create` cria o job.
2. `/checkpoint` grava o estado depois de cada passo seguro.
3. `/stop` regista porque parou.
4. `/resume-plan` calcula se pode retomar.
5. `/resume` cria contrato para executor continuar.
6. `/complete` marca o trabalho como concluído.

## Segurança

Metadados e artifacts passam por redaction básica para evitar guardar dados sensíveis.

O motor não executa ações destrutivas. Ele só guarda estado, checkpoints e contratos de retoma.
