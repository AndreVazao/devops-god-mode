# GitHub Approved Actions Executor

## Objetivo

A Phase 168 adiciona um executor real para ações GitHub aprovadas pelo Oner.

O executor fecha a ligação entre:

```txt
approved_github_patch
→ Repo/File Patch Hub
→ preview/checkpoint/approval
→ GitHub Approved Actions Executor
→ branch + commits + PR
→ GitHub Actions
→ aprovação explícita do Oner para merge
```

## O que executa

O executor pode:

- garantir/criar branch a partir da base branch;
- criar ou atualizar ficheiros já aprovados no plano;
- gerar commits através da GitHub Contents API;
- abrir pull request;
- registar o run no `Repo/File Patch Hub`.

## O que nunca executa

O executor não faz:

- merge automático;
- release;
- delete de ficheiros;
- force push;
- publicação de packages;
- alterações de tokens, passwords, cookies, credenciais, pagamentos ou licenças;
- bypass aos checks.

## Aprovação obrigatória

A frase obrigatória continua a ser:

```txt
APPLY REPO PATCH
```

Sem essa frase exata, a execução é recusada.

## Endpoints

- `GET/POST /api/github-approved-actions/status`
- `GET/POST /api/github-approved-actions/panel`
- `GET/POST /api/github-approved-actions/policy`
- `GET/POST /api/github-approved-actions/rules`
- `POST /api/github-approved-actions/execute`
- `GET/POST /api/github-approved-actions/latest`
- `GET/POST /api/github-approved-actions/package`

## Execução segura

Por defeito, `dry_run=true`.

Em `dry_run`, o serviço valida o plano e mostra as ações que iria executar:

1. ensure branch;
2. write approved files;
3. open pull request;
4. wait for GitHub Actions.

Em execução real, o serviço escreve apenas os ficheiros presentes em `safe_files` do plano aprovado.

## Relação com GitHub Actions

Depois do PR abrir, GitHub Actions deve validar:

- Universal Total Test;
- Android APK Build/smoke quando aplicável;
- Windows EXE Build/smoke quando aplicável.

O merge continua bloqueado até checks verdes e aprovação explícita do Oner.

## Regra de memória

Quando a fase for merged, a AndreOS GitHub memory deve ser atualizada com:

- HISTORICO.md;
- ULTIMA_SESSAO.md;
- DECISOES.md se houver decisão técnica nova.
