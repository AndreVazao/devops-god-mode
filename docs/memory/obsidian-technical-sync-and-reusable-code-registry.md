# Obsidian Technical Sync + Reusable Code Registry

## Objetivo

Usar o Obsidian como oficina técnica local e o GitHub memory como arquivo técnico estável.

O God Mode deve conseguir:

1. organizar localmente no Obsidian;
2. classificar notas técnicas;
3. promover para GitHub memory quando a nota virar requisito técnico;
4. manter um catálogo de código reutilizável;
5. pesquisar código existente antes de pedir código novo a uma IA.

## Fluxo correto

### 1. Obsidian primeiro

O God Mode usa o Obsidian para:

- notas em bruto;
- testes locais;
- prompts em preparação;
- decisões ainda instáveis;
- observações reais do PC/APK;
- organização diária;
- evolução local do sistema.

### 2. GitHub memory depois

Quando uma nota Obsidian fica madura e técnica, o God Mode prepara um `technical_delta` para GitHub memory.

Vai para GitHub memory quando vira:

- bug;
- feature;
- decisão técnica;
- arquitetura;
- componente reutilizável;
- PR;
- build;
- release;
- documentação técnica de repo.

### 3. Código reutilizável

Sempre que for criado código com um propósito claro, o God Mode deve registar:

- propósito;
- repo;
- projeto;
- ficheiros;
- tags;
- aliases;
- estado;
- notas;
- histórico de reutilização.

Exemplos:

- OCR/ACR visual recognition pipeline;
- ADB Android automation;
- FastAPI service+route pattern;
- Windows EXE boot smoke test;
- GitHub artifact downloader;
- Obsidian to GitHub memory sync.

## Regra anti-reinventar

Antes de pedir código novo a ChatGPT, Gemini, DeepSeek, Grok ou outro provider, o God Mode deve pesquisar:

`/api/reusable-code-registry/search`

Se existir componente compatível, deve adaptar/reutilizar em vez de pedir tudo do zero.

## Endpoints Obsidian Technical Sync

- `GET/POST /api/obsidian-technical-sync/status`
- `GET/POST /api/obsidian-technical-sync/panel`
- `GET/POST /api/obsidian-technical-sync/rules`
- `POST /api/obsidian-technical-sync/classify`
- `GET /api/obsidian-technical-sync/template`
- `POST /api/obsidian-technical-sync/prepare-sync`
- `GET/POST /api/obsidian-technical-sync/package`

## Endpoints Reusable Code Registry

- `GET/POST /api/reusable-code-registry/status`
- `GET/POST /api/reusable-code-registry/panel`
- `GET /api/reusable-code-registry/assets`
- `POST /api/reusable-code-registry/register`
- `POST /api/reusable-code-registry/search`
- `POST /api/reusable-code-registry/mark-reused`
- `POST /api/reusable-code-registry/seed`
- `GET /api/reusable-code-registry/markdown`
- `GET/POST /api/reusable-code-registry/package`

## Home / Modo Fácil

Novos botões:

- `Sync Obsidian`
- `Código Reutilizável`

Novos comandos rápidos:

- `open_obsidian_technical_sync`
- `open_reusable_code_registry`

## Machine learning / aprendizagem

Nesta fase, não é treino real de modelo. É aprendizagem operacional persistente:

- catalogar o que já foi feito;
- associar propósito a ficheiros/repos;
- contar reutilizações;
- criar aliases e tags;
- sugerir reaproveitamento antes de gerar novo código.

Isto é a base prática para uma camada futura de machine learning/recomendação.

## Segurança

- Não guardar tokens/passwords/chaves API.
- Filtrar segredos antes de sync GitHub.
- Não promover notas especulativas para GitHub.
- Validar componentes antes de reutilizar.
- O God Mode continua a decidir e auditar antes de aplicar código.
