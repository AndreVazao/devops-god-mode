# Vault Deployment Binding + Provider Env Injection Plan

## Objetivo

A Phase 185 liga o vault real da Phase 184 aos planos de deploy/env/provider.

O God Mode passa a preparar bindings e previews usando `secret_ref_id`, sem expor valores crus.

## Endpoint principal

```txt
/api/vault-deployment-binding/package
```

## Endpoints

- `/api/vault-deployment-binding/status`
- `/api/vault-deployment-binding/policy`
- `/api/vault-deployment-binding/create-binding`
- `/api/vault-deployment-binding/create-bindings-from-contract`
- `/api/vault-deployment-binding/build-injection-plan`
- `/api/vault-deployment-binding/create-apply-gate`
- `/api/vault-deployment-binding/apply-preview`
- `/api/vault-deployment-binding/bindings`
- `/api/vault-deployment-binding/package`

## Fluxo

1. Guardar segredo no vault real local cifrado.
2. Criar binding entre `secret_ref_id` e destino.
3. Destino define:
   - projeto;
   - provider;
   - ambiente;
   - nome da variável `inject_as`;
   - provider mode.
4. Construir injection plan.
5. Criar apply gate.
6. Aprovar apply gate.
7. Gerar apply preview local com passphrase.
8. Só depois, numa fase futura, provider writer poderá escrever remotamente.

## Provider modes

- `vercel_env`
- `render_env`
- `supabase_config`
- `github_actions_secret`
- `local_process_env`
- `manual_export`

## Segurança

- Esta fase não executa escrita remota em providers.
- Usa apenas `secret_ref_id` nos planos.
- O valor só é decifrado localmente após aprovação.
- Por defeito o preview não revela valores.
- `reveal_values=true` é explícito e só para uso local controlado.
- Passphrase não é persistida.
- GitHub/AndreOS/Obsidian/logs não recebem valores crus.

## Relação com Barbudo Studio / Website

O objetivo futuro é o God Mode saber que:

- `BARBUDO_STUDIO` controla APIs/rotas/admin/automação;
- `BARBUDO_WEBSITE` recebe envs públicas e secrets de deploy;
- Supabase/Vercel/Render/GitHub Actions podem receber bindings por projeto/ambiente;
- André não precisa decorar chaves/caminhos.

## Scope desta fase

Incluído:

- bindings;
- injection plan;
- apply gate;
- apply preview local;
- integração com real vault;
- integração com env planner via secret presence.

Não incluído ainda:

- escrita real em Vercel/Render/Supabase/GitHub Actions;
- rotação automática;
- DPAPI/OS keyring;
- deploy remoto sem aprovação.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 184 deve ser apagado. Fica só:

- `.github/workflows/phase185-vault-deploy-binding-smoke.yml`

Além dos workflows globais/builds.
