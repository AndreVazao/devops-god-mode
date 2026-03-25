# Repo Tree Explorer Overwrite and Seed Policy

## Decisão

O módulo **Repo Tree Explorer** adota um comportamento híbrido por origem e por contexto:

- **GitHub repos**: provider preferencial = API first
- **PC/local repos**: provider preferencial = filesystem/clone first
- o sistema deve poder usar abordagem híbrida automaticamente quando necessário

## Regras por origem

### 1. GitHub first
Quando a origem for uma repo GitHub, o sistema deve preferir:
- leitura via GitHub API;
- geração de árvore sem clone quando suficiente;
- fallback para clone temporário apenas quando necessário para recursos futuros mais profundos.

### 2. PC/local first
Quando a origem for repo local no futuro PC, o sistema deve preferir:
- leitura direta do filesystem;
- geração local completa;
- exportação local e preview usando o mesmo contrato de saída.

## Regra de overwrite

Se a repo já tiver um ficheiro de árvore existente, por exemplo:
- `PROJECT_TREE.txt`
- `PROJECT_TREE.md`
- ficheiro equivalente configurado pelo owner

então o God Mode deve:
- substituir pela árvore nova gerada;
- respeitar approval gate antes da escrita persistente;
- mostrar preview do diff sempre que possível.

## Regra para repos vazias

Se a repo estiver vazia ou quase vazia, o owner deve poder:
- colar uma árvore manual;
- usar essa árvore como diretriz estrutural;
- pedir ao God Mode para interpretar a árvore;
- depois colar/despejar ficheiros conforme essa estrutura.

## Interpretação da árvore manual

Quando o owner colar uma árvore manual, o sistema deve:
- parsear a estrutura;
- identificar pastas e ficheiros esperados;
- usá-la como plano estrutural inicial;
- ajudar a colocar os ficheiros corretos nos caminhos certos;
- manter essa árvore como referência arquitetural do bootstrap.

## Approval gate

As seguintes ações exigem aprovação explícita do owner:
- substituir ficheiro de árvore existente;
- criar ficheiro novo de árvore na repo;
- usar árvore manual como blueprint persistente;
- gerar estrutura inicial numa repo vazia.

## Resultado esperado

O Repo Tree Explorer deve suportar:
- geração automática híbrida por origem;
- overwrite controlado de árvore existente;
- bootstrap de repos vazias a partir de árvore manual;
- visualização e exportação sem comprometer o núcleo do sistema.
