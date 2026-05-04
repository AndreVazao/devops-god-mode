# Project Tree Autorefresh

## Objetivo

A Phase 177 corrige o problema de depender de árvore manual enviada pelo operador.

A partir desta fase, o God Mode passa a ter um gerador próprio de tree com nome explícito do projeto:

```txt
GOD_MODE
```

O ficheiro oficial fica em:

```txt
docs/project-tree/GOD_MODE_TREE.md
```

Isto evita descarregar ou partilhar uma tree genérica chamada `PROJECT_TREE.txt` sem saber de que projeto veio.

## Script

```txt
scripts/generate_project_tree.py
```

Exemplo:

```bash
python scripts/generate_project_tree.py --project-name GOD_MODE --output docs/project-tree/GOD_MODE_TREE.md
```

## Workflow automático

```txt
.github/workflows/project-tree-autorefresh.yml
```

O workflow corre em `push` para `main` e também manualmente por `workflow_dispatch`.

Quando a tree muda, faz commit automático:

```txt
docs(tree): refresh GOD_MODE tree [skip ci]
```

## Proteção contra loop infinito

O workflow ignora alterações nos ficheiros:

```txt
docs/project-tree/GOD_MODE_TREE.md
PROJECT_TREE.txt
data/**
```

Também não corre quando o ator é `github-actions[bot]`.

## Backend

O serviço existente foi atualizado:

```txt
backend/app/services/project_tree_autorefresh_service.py
backend/app/routes/project_tree_autorefresh.py
```

Endpoints:

- `GET /api/project-tree-autorefresh/status`
- `GET /api/project-tree-autorefresh/package`
- `GET /api/project-tree-autorefresh/dashboard`
- `GET /api/project-tree-autorefresh/current`
- `GET /api/project-tree-autorefresh/generated`
- `GET /api/project-tree-autorefresh/compare`
- `POST /api/project-tree-autorefresh/write`

## Segurança

A tree não deve incluir:

- `.env`;
- chaves SSH;
- caches;
- builds;
- artifacts binários;
- `data/**` runtime;
- segredos.

## Regra operacional

Sempre que o `main` avançar, o God Mode deve considerar a tree oficial do projeto como:

```txt
docs/project-tree/GOD_MODE_TREE.md
```

A tree manual enviada pelo André passa a ser fallback, não processo principal.
