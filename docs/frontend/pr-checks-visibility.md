# PR Checks Visibility

## Objetivo

Dar ao God Mode uma leitura clara do estado dos checks de uma PR.

A Phase 93 adiciona um classificador para distinguir:

- `green`;
- `red`;
- `pending`;
- `no_checks_reported`;
- `unknown`.

## API

- `GET /api/pr-checks-visibility/status`
- `GET /api/pr-checks-visibility/package`
- `GET /api/pr-checks-visibility/demo`
- `POST /api/pr-checks-visibility/classify`

## Regra principal

`no_checks_reported` não é verde.

Se a PR estiver pronta para integrar, mas o GitHub não devolver workflow runs nem statuses, o God Mode deve mostrar que não há sinais suficientes.

## Uso pretendido

Antes de avançar com uma PR, o God Mode deve classificar:

1. metadata da PR;
2. workflow runs visíveis;
3. statuses visíveis.

Só `green` com PR aberta e pronta deve ser tratado como seguro.

## Segurança operacional

- Vermelho: corrigir.
- Pendente: aguardar.
- Sem checks: confirmar sinais.
- Unknown: investigar.
- Verde: pode avançar.
