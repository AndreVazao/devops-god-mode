# Native Skills Runtime + Candidate Adoption Queue

## Objetivo

A Phase 201 transforma os `native_skill_candidate` criados pela Phase 200 numa fila real de adoção controlada.

Esta fase ainda não aplica código. Ela organiza candidatos, estados, planos e gates para que o God Mode consiga decidir o que merece virar implementação nativa futura.

## Endpoint principal

```txt
/api/native-skills-adoption-queue/package
```

## Página visual

```txt
/app/native-skills-adoption-queue
/app/native-skills-runtime
```

## Endpoints

- `/api/native-skills-adoption-queue/status`
- `/api/native-skills-adoption-queue/policy`
- `/api/native-skills-adoption-queue/promote-candidate`
- `/api/native-skills-adoption-queue/promote-candidates-by-filter`
- `/api/native-skills-adoption-queue/queue`
- `/api/native-skills-adoption-queue/update-status`
- `/api/native-skills-adoption-queue/create-implementation-plan`
- `/api/native-skills-adoption-queue/dashboard`
- `/api/native-skills-adoption-queue/package`

## Estados da fila

- `proposed`
- `needs_review`
- `approved_for_planning`
- `planned`
- `rejected`
- `quarantined`

## O que faz

- Promove `native_skill_candidate` para `adoption_queue_item`.
- Promove candidatos por filtro de domínio/risco.
- Mantém status controlado com transições permitidas.
- Cria planos de implementação nativa sem aplicar código.
- Consulta `module_registry_snapshot_service` antes de recomendar módulo novo.
- Cria cards mobile para revisão.
- Gera decision log sanitizado.

## Segurança

- `can_apply_code_without_gate=false`.
- `can_merge_without_oner_approval=false`.
- Não copia código bruto das labs.
- Não aplica candidato automaticamente.
- Não cria PR sozinho nesta fase.
- Não faz merge/release/deploy.
- Não executa browser automation.
- Não guarda tokens, passwords, cookies, chaves ou segredos.

## Fluxo recomendado

```txt
External Lab Snapshot Reader
→ native_skill_candidate
→ Native Skills Adoption Queue
→ adoption_queue_item
→ approved_for_planning
→ implementation_plan
→ PR gated futuro
→ GitHub Actions
→ aprovação Oner
→ merge
→ AndreOS memory
```

## Relação com fases anteriores

- Phase 199 cataloga labs externas e novas repos.
- Phase 200 lê snapshots e cria candidatos nativos.
- Phase 201 decide quais candidatos entram na fila de adoção e prepara planos controlados.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 200 deve ser apagado. Fica só:

- `.github/workflows/phase201-native-skills-adoption-queue-smoke.yml`

Além dos workflows globais/builds.
