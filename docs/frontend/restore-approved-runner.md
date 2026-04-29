# Restore Approved Runner

## Objetivo

A Phase 120 fecha o ciclo de migração para outro PC.

Depois da Phase 119 criar backup portátil, esta fase permite restaurar esse backup com segurança:

- preview antes de mexer;
- validação de caminhos do ZIP;
- bloqueio de caminhos sensíveis;
- deteção de conflitos;
- backup antes de sobrescrever;
- restore só com frase de aprovação;
- rollback a partir do pré-backup.

## Endpoints

- `GET/POST /api/restore-approved/status`
- `GET/POST /api/restore-approved/panel`
- `POST /api/restore-approved/preview`
- `POST /api/restore-approved/run`
- `POST /api/restore-approved/rollback`
- `GET/POST /api/restore-approved/latest`
- `GET/POST /api/restore-approved/package`

## Frase de aprovação

Para restaurar ou fazer rollback, o operador tem de enviar:

`RESTORE GOD MODE`

## Preview

O preview mostra:

- ficheiros seguros;
- ficheiros bloqueados;
- conflitos com ficheiros existentes;
- manifest do backup;
- se vai ser criado pré-backup.

## Restore

O restore:

1. exige frase de aprovação;
2. gera novo preview;
3. bloqueia se houver conflitos e `overwrite=false`;
4. cria ZIP de pré-restore para ficheiros que seriam sobrescritos;
5. aplica apenas ficheiros seguros;
6. guarda plano de rollback.

## Rollback

O rollback usa o ZIP de pré-restore para repor ficheiros anteriores.

Também exige a mesma frase de aprovação.

## Segurança

A fase bloqueia:

- path traversal;
- caminhos fora da allowlist;
- nomes sensíveis;
- restore sem aprovação;
- overwrite não autorizado.

## Uso esperado no PC novo

1. Instalar God Mode.
2. Copiar ZIP da pen/disco.
3. Chamar `/api/restore-approved/preview`.
4. Confirmar conflitos.
5. Chamar `/api/restore-approved/run` com frase de aprovação.
6. Se algo correr mal, usar `/api/restore-approved/rollback`.
