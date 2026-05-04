# Playbook Templates Library v1

## Objetivo

Criar uma biblioteca de receitas reutilizáveis para o God Mode executar fluxos repetíveis sem depender sempre de conversas longas.

## Templates iniciais

- `godmode_feature_safe`
- `bugfix_release`
- `external_repo_research`
- `apk_exe_validation`
- `memory_sync_runtime`
- `provider_fallback_code`
- `approved_github_patch`
- `local_pc_diagnostics`

## Endpoints

- `GET/POST /api/playbook-templates/status`
- `GET/POST /api/playbook-templates/panel`
- `GET/POST /api/playbook-templates/rules`
- `GET /api/playbook-templates/templates`
- `GET /api/playbook-templates/templates/{template_id}`
- `POST /api/playbook-templates/template`
- `POST /api/playbook-templates/to-pipeline`
- `POST /api/playbook-templates/run`
- `GET/POST /api/playbook-templates/package`

## Fluxo

```txt
Template
→ overrides opcionais
→ playbook
→ Orchestration Playbooks v1
→ Real Orchestration Pipeline
→ safe action queue
```

## Segurança

- `operator_approved=false` por defeito.
- Templates não executam destrutivo.
- GitHub/release/memória persistente continuam a exigir gates.
- Contexto sensível deve preferir Ollama/local e Security Guard.

## Valor

O God Mode passa a ter receitas prontas para:

- novas features;
- bugfix/release;
- investigação de repos externos;
- validação APK/EXE;
- sync de memória;
- fallback de providers;
- patch GitHub aprovado;
- diagnóstico local do PC.

## Próxima fase

Phase 168 — GitHub Approved Actions Executor.
