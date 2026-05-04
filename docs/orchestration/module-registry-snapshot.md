# Module Registry Snapshot + GOD_MODE Tree Integration

## Objetivo

A Phase 178 liga a tree oficial `GOD_MODE_TREE.md` ao estado global do God Mode e cria um snapshot vivo dos módulos existentes.

Isto serve para evitar duplicações quando o `main` avança rapidamente com muitos ficheiros.

## Endpoints

- `GET/POST /api/module-registry-snapshot/status`
- `GET/POST /api/module-registry-snapshot/tree-status`
- `GET/POST /api/module-registry-snapshot/summary`
- `GET/POST /api/module-registry-snapshot/snapshot`
- `POST /api/module-registry-snapshot/search`
- `GET/POST /api/module-registry-snapshot/package`

## Integração Global State

O endpoint abaixo passa a incluir `project_tree_model` e `module_registry`:

```txt
/api/god-mode-global-state/package
```

## Categorias

O snapshot classifica módulos por nomes de ficheiros em categorias operacionais:

- cockpit/home/mobile;
- GitHub/repo/patch/build;
- memory/knowledge/RAG;
- provider/AI/browser;
- local/PC/runtime;
- self-update/vault/security;
- project/recovery/portfolio;
- orchestration/execution;
- money/deploy/delivery;
- uncategorized.

## Regra reuse-first

Antes de criar um novo módulo:

1. procurar no `/api/module-registry-snapshot/search`;
2. confirmar a categoria existente;
3. preferir extender módulos já existentes;
4. só criar novo módulo se não houver capacidade equivalente.

## Tree oficial

Tree oficial:

```txt
docs/project-tree/GOD_MODE_TREE.md
```

`PROJECT_TREE.txt` é legacy/fallback.

## Segurança

O snapshot só lê nomes de ficheiros de routes/services.

Não lê conteúdos, não indexa segredos e não executa ações.
