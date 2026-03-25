# Repo Tree Explorer — GOD Mode Choice

## Decisão

O módulo **Repo Tree Explorer** entra em modo **C — versão GOD desde o início**.

## Significado

Isto significa que o módulo não será apenas um preview simples de árvore.

Ele deve nascer já preparado para:
- geração de árvore estrutural completa;
- providers híbridos por origem;
- overwrite controlado de ficheiros de árvore existentes;
- bootstrap de repos vazias por árvore manual colada pelo owner;
- preview visual avançado;
- zoom in / zoom out / fit;
- exportação;
- evolução futura para diff estrutural, comparação entre branches e documentação técnica.

## Prioridade funcional

### Backend
- provider GitHub API first;
- provider local/PC first no futuro;
- fallback híbrido automático;
- geração de `PROJECT_TREE.txt`;
- parsing de árvore manual colada pelo owner;
- capacidade de usar árvore como blueprint estrutural.

### Frontend
- preview visual isolado;
- scroll independente;
- zoom in;
- zoom out;
- botão `fit`;
- copiar árvore;
- UX mobile-first.

## Regras de segurança e aprovação

- escrita persistente continua sujeita a approval gate;
- overwrite de ficheiros existentes exige preview e aprovação;
- seed/blueprint numa repo vazia exige aprovação.

## Resultado esperado

O Repo Tree Explorer deve nascer como um módulo de engenharia estrutural do God Mode, e não apenas como utilitário visual.
