# Real Local Encrypted Value Store + Approval Gate

## Objetivo

A Phase 184 implementa o primeiro vault real local do God Mode para guardar valores secretos cifrados no PC.

O contrato da Phase 182 já definia que o God Mode podia guardar refs, fingerprints e placement plans. A Phase 184 adiciona a camada física local cifrada.

## Endpoint principal

```txt
/api/real-local-encrypted-vault/package
```

## Endpoints

- `/api/real-local-encrypted-vault/status`
- `/api/real-local-encrypted-vault/policy`
- `/api/real-local-encrypted-vault/create-write-gate`
- `/api/real-local-encrypted-vault/create-read-gate`
- `/api/real-local-encrypted-vault/store-secret`
- `/api/real-local-encrypted-vault/read-secret`
- `/api/real-local-encrypted-vault/entries`
- `/api/real-local-encrypted-vault/audit`
- `/api/real-local-encrypted-vault/package`

## O que fica guardado

Localmente no PC:

- `data/local_encrypted_vault/*.vault` com valor cifrado;
- `data/local_encrypted_vault/vault_index.json` com metadados redigidos;
- `data/local_encrypted_vault/vault_audit.json` com audit log redigido.

Metadados permitidos:

- `secret_ref_id`;
- `project_id`;
- `provider`;
- `environment`;
- `key_name`;
- `fingerprint`;
- `value_length`;
- caminho do ficheiro cifrado;
- IDs de approval gate.

## O que não fica guardado

- password crua;
- token cru;
- cookie cru;
- passphrase;
- `.env` cru;
- valor secreto em GitHub/AndreOS/Obsidian cloud/logs.

## Fluxo de escrita

1. Criar approval gate com `/create-write-gate`.
2. O operador aprova o gate no cockpit.
3. Chamar `/store-secret` com valor + passphrase local.
4. O valor é cifrado para ficheiro `.vault`.
5. O índice só guarda metadados e fingerprint.
6. O audit log regista evento redigido.

## Fluxo de leitura/uso

1. Criar approval gate com `/create-read-gate`.
2. O operador aprova o gate.
3. Chamar `/read-secret` com passphrase local e propósito.
4. O valor é decifrado apenas para uso local imediato.
5. Por defeito a resposta não precisa de revelar o valor; pode confirmar que está disponível para injeção local.
6. Audit log regista evento redigido.

## Cifra atual

Implementação sem dependências externas para estabilidade do artifact Windows:

- PBKDF2-HMAC-SHA256;
- keystream HMAC-SHA256;
- XOR stream;
- HMAC authentication.

Isto é a primeira camada real local. Futuro hardening recomendado:

- Windows DPAPI;
- OS keyring;
- rotação;
- token temporal de aprovação mobile;
- isolamento por projeto/tenant.

## Segurança

- Approval gate obrigatório para escrita/leitura.
- Passphrase não é persistida.
- Status/package/list/audit não retornam valores crus.
- Merge/release/deploy/injeção continuam dependentes de gates próprios.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 183 deve ser apagado. Fica só:

- `.github/workflows/phase184-real-local-encrypted-vault-smoke.yml`

Além dos workflows globais/builds.
