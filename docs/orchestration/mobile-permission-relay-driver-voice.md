# Mobile Permission Relay + Driver Voice Mode + Offline Resend Queue + Local Vault Intake

## Objetivo

A Phase 205 implementa o contrato central de operação real:

- cérebro do God Mode no PC de casa;
- telemóvel como cockpit/popup de permissão;
- modo condução por voz;
- espera no PC até resposta;
- reenvio/sincronização se o telemóvel estiver sem rede/túnel;
- pedidos sensíveis com formulário;
- Vault local/encriptado para guardar chaves, tokens, passwords, URLs e variáveis de deploy aprovadas;
- classificador para identificar providers/projetos/finalidade e ignorar placeholders/fictícios.

## Endpoints principais

```txt
/api/mobile-permission-relay/package
/api/god-mode-vault/status
/api/god-mode-vault/intake-text
```

## Páginas visuais

```txt
/app/mobile-permission-relay
/app/driver-voice-permissions
/app/god-mode-vault
/app/vault-intake
```

## Endpoints do Permission Relay

- `/api/mobile-permission-relay/status`
- `/api/mobile-permission-relay/policy`
- `/api/mobile-permission-relay/create-request`
- `/api/mobile-permission-relay/popup-contract-examples`
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

## Endpoints do Vault

- `/api/god-mode-vault/status`
- `/api/god-mode-vault/store-secret`
- `/api/god-mode-vault/intake-text`
- `/api/god-mode-vault/plan-needed-token`
- `/api/god-mode-vault/references`
- `/api/god-mode-vault/reveal-for-runtime`
- `/api/god-mode-vault/intake-status`

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
→ se houver segredo aprovado: guarda no Local Vault encriptado
→ PC recebe decisão + vault_reference
→ wait_lock liberta ou bloqueia
→ tarefa continua ou fica bloqueada
```

## Contrato visual de popup

O padrão visual alvo é equivalente aos popups de autorização ChatGPT/GitHub usados durante desenvolvimento assistido.

O popup deve mostrar:

- serviço/origem, por exemplo `GitHub`, `Provider`, `God Mode PC`, `Vault`;
- ação, por exemplo `Update GitHub file`, `Delete workflow file`, `Create pull request`, `Provider login required`;
- descrição curta da ação;
- repositório/projeto/branch/ficheiro quando aplicável;
- bloco `A partilha de dados inclui` com nomes de campos e valores sanitizados;
- botões principais `Confirmar` e `Recusar`;
- opção de `Alterar` quando o pedido permite edição;
- campos preenchíveis quando o request_type é `sensitive_fill`, `credential_prompt` ou `login_manual`.

## Vault local / intake de segredos

Regra correta:

```txt
Não guardar segredo bruto no repo ou memória normal.
Guardar segredo real aprovado no Vault local/encriptado do PC.
O resto do God Mode usa vault_reference.
```

O God Mode deve aceitar intake bulk de:

- `.env`;
- tokens;
- passwords;
- API keys;
- URLs de deploy;
- connection strings;
- provider credentials;
- project paths/configs úteis.

O classificador deve:

- identificar provider: GitHub, Vercel, Render, Supabase, OpenAI, Anthropic, Gemini, Google Cloud, Cloudflare, HeyGen, Stripe, PayPal, Railway, database;
- identificar tipo: token, api_key, password, cookie, private_key, connection_string, webhook_secret, url, config_value;
- identificar projeto: GOD_MODE, BARIBUDOS, PROVENTIL ou outro hint;
- identificar finalidade: deploy, repo, workflow, database, AI provider, payments, DNS, etc.;
- ignorar placeholders/fictícios como `your_key_here`, `example`, `dummy`, `fake`, `changeme`;
- guardar valores reais no vault com label, purpose, provider, project_id, scope e reuse_policy.

## Criação/planeamento de tokens pelo God Mode

Quando o God Mode perceber que precisa de um token, deve criar um `token_generation_plan` com:

- provider;
- projeto;
- finalidade;
- scopes mínimos;
- label de armazenamento;
- passos de criação;
- gate do Oner/provider;
- destino no Vault.

Depois de criado ou preenchido uma vez, o token deve ficar reutilizável por referência segura.

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
- `can_store_raw_secrets_in_normal_memory=false`.
- `can_store_sensitive_values_in_local_vault=true`.
- `can_unlock_sensitive_action_without_oner=false`.
- Não guarda passwords/tokens/cookies/API keys no repo.
- Não força interação enquanto o Oner conduz.
- Não faz autofill sensível sem gate/vault.
- Não faz merge/release/deploy/pagamentos sem aprovação.
- `data/private/` e `backend/data/private/` ficam no `.gitignore`.

## Próxima ligação necessária

A próxima fase deve ligar diretamente:

```txt
Autonomous IA Work Session Operator
→ Mobile Permission Relay
→ God Mode Local Vault
→ Provider Launcher / resposta IA / credential prompt / wait mode
```

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 204 deve ser apagado. Fica só:

- `.github/workflows/phase205-mobile-permission-relay-driver-voice-smoke.yml`

Além dos workflows globais/builds.
