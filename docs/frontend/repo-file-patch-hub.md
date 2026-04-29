# Repo File Patch Hub

## Objetivo

A Phase 132 cria o hub de patches reais para ficheiros/repos.

Esta fase prepara execução segura em projetos reais com:

- plano;
- preview diff;
- checkpoint;
- metadados de rollback;
- validação;
- aprovação;
- contrato para executor abrir PR.

## Endpoints

- `GET/POST /api/repo-file-patch/status`
- `GET/POST /api/repo-file-patch/panel`
- `GET/POST /api/repo-file-patch/policy`
- `POST /api/repo-file-patch/plan`
- `POST /api/repo-file-patch/preview`
- `POST /api/repo-file-patch/checkpoint`
- `POST /api/repo-file-patch/approve`
- `POST /api/repo-file-patch/record-run`
- `GET/POST /api/repo-file-patch/latest`
- `GET/POST /api/repo-file-patch/package`

## Política

- Criar plano antes de mexer.
- Mostrar preview/diff por ficheiro.
- Criar checkpoint com hash original.
- Guardar rollback metadata.
- Bloquear caminhos sensíveis.
- Não mexer em `.git`.
- Não aplicar patches sem aprovação explícita.

## Frase de aprovação

`APPLY REPO PATCH`

## Caminhos bloqueados

O hub bloqueia caminhos com partes como:

- `.env`
- `secret`
- `token`
- `password`
- `cookie`
- `credential`
- `authorization`
- `bearer`
- `api_key`
- `private_key`
- `.git/`

## Fluxo esperado

1. Criar plano em `/plan`.
2. Gerar preview em `/preview`.
3. Criar checkpoint em `/checkpoint`.
4. Aprovar com `/approve`.
5. Executor aprovado aplica ficheiros exatos em branch alvo.
6. Executor corre validações.
7. Executor abre PR.
8. Resultado é registado em `/record-run`.

## Segurança

Esta fase não escreve ficheiros reais automaticamente.

Ela cria o contrato seguro para o executor real aplicar só depois de preview/aprovação.
