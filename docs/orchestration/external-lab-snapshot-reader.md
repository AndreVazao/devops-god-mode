# External Lab Snapshot Reader + Native Skill Candidate Planner

## Objetivo

A Phase 200 transforma as external skills labs em fonte prática de evolução controlada.

O God Mode passa a conseguir ler snapshots sanitizados das labs, especialmente `docs/UPSTREAM_SNAPSHOT.json`, e gerar candidatos nativos para implementação futura no core sem copiar código externo às cegas.

## Endpoint principal

```txt
/api/external-lab-snapshot-reader/package
```

## Página visual

```txt
/app/external-lab-snapshot-reader
/app/lab-snapshot-reader
```

## Endpoints

- `/api/external-lab-snapshot-reader/status`
- `/api/external-lab-snapshot-reader/policy`
- `/api/external-lab-snapshot-reader/ingest-snapshot-text`
- `/api/external-lab-snapshot-reader/ingest-snapshot`
- `/api/external-lab-snapshot-reader/generate-candidates-from-registry`
- `/api/external-lab-snapshot-reader/candidates`
- `/api/external-lab-snapshot-reader/create-candidate-plan`
- `/api/external-lab-snapshot-reader/dashboard`
- `/api/external-lab-snapshot-reader/package`

## O que faz

- Lê JSON colado no telemóvel a partir de `docs/UPSTREAM_SNAPSHOT.json`.
- Lê payload estruturado de snapshot.
- Extrai paths de `SKILL.md` e metadados equivalentes.
- Cria `native_skill_candidate` com:
  - origem;
  - lab;
  - upstream;
  - path;
  - domínio alvo;
  - confiança;
  - risco;
  - modo de reutilização;
  - aprovações exigidas.
- Gera fallback de candidatos a partir do registry das labs quando os snapshots reais ainda não foram importados.
- Cria plano gated para candidato específico.
- Cria card de revisão no cockpit mobile.

## Domínios de candidato

- `god_mode_core`
- `android_mobile`
- `provider_router`
- `cloud_deploy`
- `verbaforge_content`
- `github_workflow`
- `browser_quarantine`

## Modos de reutilização

- `adapt_native`
- `reference`
- `quarantine_review`
- `reject`

## Segurança

- Não guarda tokens, passwords, cookies, API keys ou segredos.
- Rejeita texto de snapshot com padrões óbvios de segredo.
- Não importa código bruto de lab para o core.
- Não torna labs dependências centrais.
- Não faz deploy, release, browser automation, merge ou ação paga.
- Candidato só vira código através de branch/PR, GitHub Actions e aprovação do Oner quando aplicável.
- `can_apply_candidate_without_gate=false`.
- `can_import_raw_lab_code_without_review=false`.

## Integração com Phase 199

A Phase 199 regista labs e decide se novas repos externas servem como lab/referência/quarentena.

A Phase 200 lê evidência desses labs e propõe candidatos nativos para evolução futura.

Fluxo recomendado:

```txt
External Skills Lab Registry
→ Import upstream snapshot no lab
→ Colar/lêr docs/UPSTREAM_SNAPSHOT.json
→ External Lab Snapshot Reader
→ native_skill_candidate
→ candidate plan
→ PR gated no core
→ GitHub Actions
→ aprovação Oner
→ merge
→ AndreOS memory
```

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 199 deve ser apagado. Fica só:

- `.github/workflows/phase200-external-lab-snapshot-reader-smoke.yml`

Além dos workflows globais/builds.
