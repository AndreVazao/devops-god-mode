# God Mode Self-Diagnosis Mission Control + Fix-What-Is-Missing Queue

## Objetivo

A Phase 203 cria o cockpit para o God Mode diagnosticar o que ainda falta nele mesmo para ficar real, instalável e capaz de autoevoluir de forma controlada.

Esta fase não corrige código diretamente. Ela cria diagnóstico, lacunas e uma fila `self_fix_queue_item` priorizada para o próximo passo: gerar planos de PR gated.

## Endpoint principal

```txt
/api/god-mode-self-diagnosis/package
```

## Página visual

```txt
/app/god-mode-self-diagnosis
/app/self-fix-mission-control
```

## Endpoints

- `/api/god-mode-self-diagnosis/status`
- `/api/god-mode-self-diagnosis/policy`
- `/api/god-mode-self-diagnosis/run`
- `/api/god-mode-self-diagnosis/queue`
- `/api/god-mode-self-diagnosis/update-queue-item`
- `/api/god-mode-self-diagnosis/create-pr-planning-brief`
- `/api/god-mode-self-diagnosis/dashboard`
- `/api/god-mode-self-diagnosis/package`

## O que agrega

- First PC Install Ready Pack;
- First PC Runtime Verification;
- Artifacts Center;
- God Mode Global State;
- Module Registry Snapshot;
- Native Skills Adoption Queue;
- Mobile Approval Cockpit.

## O que produz

- `diagnostic_run`;
- lista de lacunas reais;
- `self_fix_queue_item`;
- severidade: `blocker`, `high`, `medium`, `low`;
- separação entre bloqueante de instalação e melhoria futura;
- `PR planning brief` gated;
- card mobile de revisão.

## Segurança

- `can_apply_fix_without_gate=false`.
- `can_merge_without_oner_approval=false`.
- Não aplica código diretamente.
- Não faz merge/release/deploy autónomo.
- Não guarda segredos.
- Não executa browser automation.
- Não faz update final sem gate.

## Fluxo recomendado

```txt
/app/first-pc-install-ready-pack
→ /app/god-mode-self-diagnosis
→ run diagnosis
→ self_fix_queue_item
→ create PR planning brief
→ futuro PR gated
→ GitHub Actions
→ aprovação Oner
→ merge assistido quando autorizado
→ AndreOS memory
```

## Prioridade operacional

O God Mode deve resolver primeiro lacunas que bloqueiam instalação e primeiro uso no PC.

Só depois deve avançar para:

- candidate-to-PR generator;
- self-update staged installer;
- mobile-to-PC connection guide;
- outros programas/projetos.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 202 deve ser apagado. Fica só:

- `.github/workflows/phase203-self-diagnosis-mission-control-smoke.yml`

Além dos workflows globais/builds.
