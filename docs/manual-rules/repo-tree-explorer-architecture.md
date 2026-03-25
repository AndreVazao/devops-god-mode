# Repo Tree Explorer Architecture

## Decisão

O módulo **Repo Tree Explorer** do DevOps God Mode adota arquitetura **C — híbrida**.

## Princípio

- o **backend** é quem tem acesso para ler, analisar e gerar a árvore da repo;
- o **frontend** é quem apresenta o preview de forma bonita, navegável e segura no telemóvel.

## Distribuição de responsabilidades

### Backend
Responsável por:
- ler a estrutura da repo;
- gerar árvore completa;
- aplicar filtros (`node_modules`, `.git`, `.next`, `dist`, `venv`, etc.);
- gerar formatos (`PROJECT_TREE.txt`, plain text, markdown no futuro);
- preparar exportação;
- servir dados ao frontend;
- garantir que a geração da árvore não depende da UI.

### Frontend
Responsável por:
- mostrar preview visual da árvore;
- manter box isolada sem partir o layout principal;
- oferecer zoom in / zoom out;
- botão `fit` para ajustar ao ecrã;
- scroll independente;
- copiar árvore;
- disparar ação de gerar ficheiro.

## Regras

### 1. O backend é a fonte da árvore
A árvore nunca deve nascer apenas no frontend.

### 2. O frontend é só camada de visualização e ergonomia
Toda a leitura real e geração persistente deve ficar no backend.

### 3. O módulo deve ser desacoplado do núcleo
Repo Tree Explorer entra como módulo separado e não pode partir:
- scan GitHub;
- registry;
- approval flows;
- conectores já estáveis.

### 4. Exportação controlada
Gerar ficheiro na repo deve continuar a respeitar aprovação do owner quando houver escrita persistente.

## Funcionalidades mínimas

- preview da árvore completa;
- `PROJECT_TREE.txt`;
- copiar árvore;
- gerar ficheiro;
- zoom in;
- zoom out;
- `fit`;
- box isolada e visualizável no telemóvel.

## Evolução futura

Preparar desde início para suportar:
- markdown tree;
- json tree;
- comparação entre árvores;
- diff estrutural entre branches;
- templates de árvore para documentação técnica.
