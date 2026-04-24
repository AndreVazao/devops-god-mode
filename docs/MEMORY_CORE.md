# AndreOS Memory Core

## O que é

O AndreOS Memory Core é a camada de memória longa do God Mode. Usa ficheiros Markdown compatíveis com Obsidian para guardar contexto persistente por projeto: memória mestre, decisões, backlog, roadmap, arquitetura, histórico, prompts, erros e última sessão.

## Como o God Mode usa a memória

O fluxo correto é:

1. Identificar o projeto ativo.
2. Ler a memória desse projeto.
3. Gerar contexto compacto para IA.
4. Executar apenas ações aprovadas quando houver risco.
5. Guardar decisões em `DECISOES.md`.
6. Guardar alterações em `HISTORICO.md`.
7. Atualizar `ULTIMA_SESSAO.md` no fim da sessão.

## Estrutura principal

- `memory/config/memory.config.json`: configuração do vault e regras.
- `memory/templates/`: modelos Markdown.
- `memory/vault/AndreOS/`: vault Obsidian.
- `memory/vault/AndreOS/02_PROJETOS/`: memória por projeto.
- `memory/schemas/`: contratos JSON para eventos, projetos e decisões.

## Projetos base

- GOD_MODE
- PROVENTIL
- VERBAFORGE
- BOT_LORDS_MOBILE
- ECU_REPRO
- BUILD_CONTROL_CENTER

## Criar novo projeto

Via API:

`POST /api/memory-core/projects`

Body:

```json
{
  "project_name": "NOVO_PROJETO"
}
```

Isto cria a pasta do projeto e os ficheiros base.

## Guardar decisões

Via API:

`POST /api/memory-core/decisions`

```json
{
  "project_name": "GOD_MODE",
  "decision": "Usar Obsidian como memória externa persistente.",
  "reason": "Permite continuidade entre sessões e organização por projeto."
}
```

## Guardar histórico

Via API:

`POST /api/memory-core/history`

```json
{
  "project_name": "GOD_MODE",
  "action": "Criado AndreOS Memory Core.",
  "result": "Estrutura Markdown, API e cockpit criados."
}
```

## Gerar contexto para IA

Via API:

`GET /api/memory-core/context/GOD_MODE?max_chars=12000`

O contexto junta ficheiros prioritários definidos em `memory.config.json`.

## Segurança

O Memory Core bloqueia gravações que contenham palavras sensíveis configuradas em `blocked_secret_keywords`. O objetivo é impedir que segredos técnicos sejam escritos no Obsidian.

## Futuro

Ainda falta pesquisa semântica com embeddings ou vector database. A fase atual é file-based, simples, auditável e compatível com Obsidian.
