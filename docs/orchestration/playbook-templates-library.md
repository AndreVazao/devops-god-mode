# Playbook Templates Library

## Objetivo

Criar uma biblioteca de receitas reutilizáveis para o God Mode executar fluxos repetíveis sem depender sempre de conversas longas.

Esta fase traz para o God Mode o lado mais prático de Praison/Ruflo: padrões de workflow reutilizáveis, mas implementados nativamente.

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
→ playbook God Mode
→ Orchestration Playbooks
→ Real Orchestration Pipeline
→ Safe Action Queue
```

## Segurança

- Templates não executam ações destrutivas.
- `operator_approved=false` por defeito.
- GitHub/release/memória persistente continuam a passar por gates.
- Contexto sensível deve preferir Ollama/local e Security Guard.

## Próxima evolução

- Expor templates na Home/App.
- Permitir salvar templates customizados localmente.
- Criar templates por projeto: ProVentil, VerbaForge, Bot Lords, ECU, Baribudos.
- Ligar templates ao executor aprovado GitHub.
