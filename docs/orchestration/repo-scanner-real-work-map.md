# Repo Scanner Auto-Populate Real Work Map

## Objetivo

A Phase 194 adiciona um scanner/sugestor de repos para alimentar o Real Work Map.

Ele ajuda o God Mode a perceber que repo pertence a que projeto/grupo e que frente representa: website, studio, backend, mobile, desktop, admin ou labs.

## Endpoint principal

```txt
/api/repo-scanner-real-work-map/package
```

## Página visual

```txt
/app/repo-scanner-real-work-map
/app/repo-scanner
```

## Endpoints

- `/api/repo-scanner-real-work-map/status`
- `/api/repo-scanner-real-work-map/policy`
- `/api/repo-scanner-real-work-map/scan`
- `/api/repo-scanner-real-work-map/suggest-repo`
- `/api/repo-scanner-real-work-map/apply-suggestion`
- `/api/repo-scanner-real-work-map/create-review-cards`
- `/api/repo-scanner-real-work-map/dashboard`
- `/api/repo-scanner-real-work-map/package`

## O que esta fase faz

- Recebe lista de repos.
- Sugere grupo/projeto.
- Sugere frente: website, studio, backend, mobile, desktop, admin, labs.
- Deteta pares `website + studio` no mesmo grupo.
- Pode aplicar automaticamente ligações de alta confiança.
- Cria cards de revisão para confiança média/baixa ou frente desconhecida.
- Alimenta o Real Work Map através de `real_work_fast_path_service.link_repo`.

## O que esta fase não faz

- Não apaga repos.
- Não faz merge entre repos.
- Não altera settings do GitHub.
- Não guarda segredos.
- Não aplica sugestões incertas sem revisão.

## Grupos reconhecidos

- `god_mode`
- `baribudos_platform`
- `proventil`
- `unclassified`

## Exemplos

```txt
AndreVazao/devops-god-mode -> god_mode / backend
AndreVazao/andreos-memory -> god_mode / backend
AndreVazao/godmode-smol-ai-lab -> god_mode / labs
AndreVazao/baribudos-website -> baribudos_platform / website
AndreVazao/baribudos-studio -> baribudos_platform / studio
```

## Regra de realidade

O scanner sugere. Só aplica automaticamente quando a confiança é alta e a frente é conhecida.

Quando existe dúvida, cria card para o Oner confirmar.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 193 deve ser apagado. Fica só:

- `.github/workflows/phase194-repo-scanner-real-work-map-smoke.yml`

Além dos workflows globais/builds.
