# Controlled Self-Evolution + External Skills Lab Registry

## Objetivo

A Phase 199 prepara o God Mode para evoluir-se de forma controlada usando labs externas e novas repos descobertas.

O God Mode passa a reconhecer labs como fonte de evolução e reutilização de código/padrões, mas aplicação real continua gated: PR, testes, validação e aprovação quando houver risco.

## Endpoint principal

```txt
/api/external-skills-lab-registry/package
```

## Página visual

```txt
/app/external-skills-lab-registry
/app/skills-labs
```

## Endpoints

- `/api/external-skills-lab-registry/status`
- `/api/external-skills-lab-registry/policy`
- `/api/external-skills-lab-registry/seed-defaults`
- `/api/external-skills-lab-registry/labs`
- `/api/external-skills-lab-registry/assess-repo`
- `/api/external-skills-lab-registry/catalog-repos`
- `/api/external-skills-lab-registry/decide-reuse`
- `/api/external-skills-lab-registry/create-reuse-plan`
- `/api/external-skills-lab-registry/create-lab-creation-plan`
- `/api/external-skills-lab-registry/dashboard`
- `/api/external-skills-lab-registry/package`

## O que esta fase faz

- Regista as 10 external skills labs.
- Avalia novas repos externas descobertas.
- Decide se uma repo deve virar lab, referência, quarentena, vertical ou ser ignorada.
- Gera plano de criação de lab com README e workflow de import upstream.
- Decide quais labs/códigos/padrões usar perante um pedido do Oner.
- Cria plano de reutilização nativa.
- Cria cards de revisão para evolução controlada.
- Mantém `can_apply_code_without_gate=false`.
- Mantém `can_create_lab_without_gate=false`.

## O que esta fase não faz

- Não faz merge direto.
- Não faz release direta.
- Não guarda segredos.
- Não copia código externo às cegas.
- Não usa automação browser em quarentena sem gate explícito.
- Não executa deploy/cloud/API paga sem aprovação.

## Decisões de catalogação

- `lab_now`
- `reference_only`
- `quarantine_lab`
- `vertical_lab`
- `ignore`

## Reuse modes

- `reference`
- `adapt_native`
- `copy_with_review`
- `quarantine_review`
- `reject`

## Labs reconhecidas

- `AndreVazao/godmode-openai-skills-lab`
- `AndreVazao/godmode-anthropic-skills-lab`
- `AndreVazao/godmode-vercel-skills-cli-lab`
- `AndreVazao/godmode-android-skills-lab`
- `AndreVazao/godmode-gemini-skills-lab`
- `AndreVazao/godmode-cloudflare-skills-lab`
- `AndreVazao/godmode-awesome-copilot-lab`
- `AndreVazao/godmode-browser-act-skills-lab`
- `AndreVazao/godmode-google-cloud-skills-lab`
- `AndreVazao/godmode-heygen-skills-lab`

## Regra de realidade

O God Mode pode decidir que código/padrão usar e onde aplicar, mas só prepara planos/PRs. Merge, release, deploy, ações pagas e browser automation continuam sujeitos a gates e aprovação do Oner.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 198 deve ser apagado. Fica só:

- `.github/workflows/phase199-controlled-self-evolution-skills-labs-smoke.yml`

Além dos workflows globais/builds.
