# Provider Env Writers Draft + Dry-Run Apply Gate

## Objetivo

A Phase 186 prepara writers específicos para providers em modo dry-run.

Esta fase **não executa escrita remota real**. Ela transforma o apply preview do vault/deployment binding em payloads provider-specific redigidos, validados e guardados sem valores crus.

## Endpoint principal

```txt
/api/provider-env-writers-dry-run/package
```

## Endpoints

- `/api/provider-env-writers-dry-run/status`
- `/api/provider-env-writers-dry-run/policy`
- `/api/provider-env-writers-dry-run/create-gate`
- `/api/provider-env-writers-dry-run/build-from-plan`
- `/api/provider-env-writers-dry-run/build-from-preview`
- `/api/provider-env-writers-dry-run/writer-specs`
- `/api/provider-env-writers-dry-run/dry-runs`
- `/api/provider-env-writers-dry-run/package`

## Providers suportados em dry-run

- Vercel env;
- Render env;
- Supabase config/secrets;
- GitHub Actions secrets;
- local process env;
- manual export.

## Fluxo

1. Criar injection plan com `/api/vault-deployment-binding/build-injection-plan`.
2. Criar dry-run gate com `/api/provider-env-writers-dry-run/create-gate`.
3. Aprovar o gate no cockpit.
4. Chamar `/api/provider-env-writers-dry-run/build-from-plan` com passphrase local.
5. O sistema cria apply preview local aprovado.
6. O writer transforma cada export em payload específico do provider.
7. O payload é guardado redigido, com hash e metadados.
8. Nenhuma chamada remota é feita.

## Segurança

- `remote_write_enabled=false`.
- `no_network_calls=true`.
- Não guarda valor cru.
- Não guarda passphrase.
- Não escreve em Vercel/Render/Supabase/GitHub Actions.
- Guarda apenas request shape redigido, hash, target e metadata.

## Futuro

A escrita real em providers só entra em fase futura com:

- aprovação explícita do Oner;
- gate separado por provider;
- rollback/backup possível;
- audit redigido;
- confirmação de target real.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 185 deve ser apagado. Fica só:

- `.github/workflows/phase186-provider-env-writers-dry-run-smoke.yml`

Além dos workflows globais/builds.
