# Repo Tree Explorer Scope Priority

## Decisão

O módulo **Repo Tree Explorer** será **universal** no desenho, mas com prioridade prática de implementação em:

1. **GitHub first**
2. **PC/local first**
3. servidores, containers e outras superfícies depois

## Interpretação

### Arquitetura-alvo
O sistema deve ser preparado desde início para suportar:
- GitHub repositories;
- repos locais no futuro PC;
- repos em servidores;
- repos em containers;
- outras origens estruturais no futuro.

### Prioridade real de execução
A ordem de implementação deve ser:

#### Fase 1 — GitHub first
- gerar árvore de repos GitHub;
- preview;
- exportação;
- `PROJECT_TREE.txt`;
- zoom / fit / copy no frontend.

#### Fase 2 — PC/local first
- ler repos locais no futuro PC;
- gerar árvore local;
- manter a mesma UI e os mesmos formatos;
- reutilizar o mesmo motor backend.

#### Fase 3 — universal expansion
- server repos;
- containers;
- superfícies remotas adicionais.

## Regra de design

O módulo deve nascer com interfaces que permitam múltiplos providers, como por exemplo:
- `github_tree_provider`
- `local_tree_provider`
- `server_tree_provider`
- `container_tree_provider`

Mas só os providers prioritários devem entrar primeiro.

## Resultado esperado

O Repo Tree Explorer deve ser construído de forma:
- universal no desenho;
- modular na implementação;
- GitHub-first e PC-first na prática.
