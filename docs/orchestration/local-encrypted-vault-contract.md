# Local Encrypted Vault Contract + First Credential Flow

## Objetivo

A Phase 182 formaliza o contrato do vault local do God Mode.

O God Mode deve saber:

- que chave existe;
- a que projeto pertence;
- em que provider/ambiente entra;
- onde deve ser injetada;
- se é exemplo ou valor real candidato.

Mas não deve guardar valores secretos crus em GitHub, docs, memória, logs ou contexto de IA externa.

## Endpoints

- `/api/local-encrypted-vault-contract/status`
- `/api/local-encrypted-vault-contract/policy`
- `/api/local-encrypted-vault-contract/register-project`
- `/api/local-encrypted-vault-contract/classify-env-text`
- `/api/local-encrypted-vault-contract/intake-env-text`
- `/api/local-encrypted-vault-contract/first-credential-flow`
- `/api/local-encrypted-vault-contract/bootstrap-project-mapping`
- `/api/local-encrypted-vault-contract/package`

## Barbudo Studio / Website

Regra registada:

- `BARBUDO_STUDIO` é o app/controlador que gere o website.
- `BARBUDO_WEBSITE` é o site público/target.
- God Mode deve guardar mappings/placement plans para saber que API/env pertence a qual lado.
- Valores reais ficam apenas no vault local cifrado do PC quando essa camada física existir.

## `.env` intake

O endpoint `/intake-env-text` classifica cada linha:

- `real_candidate`;
- `example_value`;
- `secret_candidate`;
- `config_candidate`.

Também tenta inferir provider:

- Supabase;
- Vercel;
- Render;
- OpenAI;
- Anthropic;
- Google;
- GitHub;
- Stripe;
- PayPal.

E tenta inferir projeto:

- GOD_MODE;
- BARBUDO_STUDIO;
- BARBUDO_WEBSITE;
- UNKNOWN_PROJECT.

## Segurança

Guarda apenas:

- `secret_ref_id`;
- fingerprint curta;
- provider guess;
- project guess;
- environment;
- placement plan;
- value length;
- redacted preview.

Não guarda:

- password crua;
- token cru;
- cookie cru;
- URL sensível completa quando classificada como segredo;
- `.env` cru em memória GitHub.

## Fluxo real futuro

1. André envia/importa ficheiro `.env` no PC.
2. God Mode classifica localmente.
3. God Mode mostra exemplos vs reais.
4. André confirma projeto/ambiente.
5. Vault local cifrado guarda valor real no PC.
6. God Mode usa apenas `secret_ref_id` para deploy/injeção.
7. Ação de deploy exige aprovação.

## Obsidian

Pode sincronizar notas seguras:

- labels;
- decisões;
- placements;
- quais projetos usam quais providers.

Não deve sincronizar valores secretos crus para Obsidian cloud/GitHub.
