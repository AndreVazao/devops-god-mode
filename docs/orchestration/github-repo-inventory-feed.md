# GitHub Repo Inventory Connector + Real Work Scanner Feed

## Objetivo

A Phase 195 cria uma camada de inventário real de repos para alimentar o Repo Scanner e o Real Work Map.

O backend do God Mode não executa diretamente o GitHub connector interno da sessão ChatGPT. Em vez disso, recebe snapshots sanitizados do connector ou lista manual colada pelo Oner.

## Endpoint principal

```txt
/api/github-repo-inventory-feed/package
```

## Página visual

```txt
/app/github-repo-inventory-feed
/app/repo-inventory
```

## Endpoints

- `/api/github-repo-inventory-feed/status`
- `/api/github-repo-inventory-feed/policy`
- `/api/github-repo-inventory-feed/import-connector-snapshot`
- `/api/github-repo-inventory-feed/import-repo-names`
- `/api/github-repo-inventory-feed/seed-connector-seen`
- `/api/github-repo-inventory-feed/create-new-repo-cards`
- `/api/github-repo-inventory-feed/dashboard`
- `/api/github-repo-inventory-feed/package`

## O que esta fase faz

- Guarda inventário sanitizado de repos.
- Alimenta automaticamente o Repo Scanner.
- Persiste snapshot de inventário.
- Cria cards para repos desconhecidos.
- Suporta fallback por lista colada no telemóvel.
- Inclui seed com os repos vistos pelo GitHub connector nesta sessão.

## O que esta fase não faz

- Não guarda segredos.
- Não clona repos automaticamente.
- Não apaga repos.
- Não altera settings do GitHub.
- Não faz merge entre repos.

## Repos vistos pelo connector nesta sessão

Inclui exemplos reais como:

- `AndreVazao/devops-god-mode`
- `AndreVazao/andreos-memory`
- `AndreVazao/godmode-ruflo-lab`
- `AndreVazao/godmode-praison-lab`
- `AndreVazao/godmode-smol-ai-lab`
- `AndreVazao/baribudos-studio`
- `AndreVazao/baribudos-studio-website`
- `AndreVazao/baribudos-studio-primary`
- `AndreVazao/baribudos-studio-home-edition`
- `AndreVazao/proventil`
- `AndreVazao/universal-build-platform`
- `AndreVazao/build-control-panel`
- `AndreVazao/build-control-center`
- `AndreVazao/GitHub-auto-builder`

## Regra de realidade

Inventário é metadado sanitizado. O scanner classifica e sugere. O Real Work Map recebe links. Repos desconhecidos viram cards para revisão.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 194 deve ser apagado. Fica só:

- `.github/workflows/phase195-github-repo-inventory-feed-smoke.yml`

Além dos workflows globais/builds.
