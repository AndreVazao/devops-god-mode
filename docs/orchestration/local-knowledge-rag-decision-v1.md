# Local Knowledge/RAG Decision v1

## Objetivo

A Phase 170 adiciona uma camada local-first para o God Mode pesquisar memória, documentação e código existente antes de criar código novo.

O objetivo é evitar recriar módulos que já existem e dar ao orquestrador uma decisão objetiva:

```txt
pedido/objetivo
→ índice local seguro
→ pesquisa AndreOS/Obsidian/docs/código
→ candidatos de reutilização
→ decisão reuse-first
→ só criar novo se não houver candidato suficiente
```

## Fontes v1

- `memory/vault/AndreOS` — memória/Obsidian local quando existir.
- `docs` — documentação técnica do repo.
- `backend` — serviços/rotas Python/FastAPI.
- `desktop` — launcher e componentes Windows/desktop.
- `android` — APK/WebView/mobile.
- `data/conversation_repo_materializations` — código gerado/reutilizável local.

## Segurança

O índice não deve guardar nem expor:

- `.env`
- credenciais
- passwords/senhas
- cookies
- authorization/bearer headers
- API keys
- private keys
- node_modules
- builds/caches

Snippets são sanitizados. Conteúdo com sinais sensíveis é marcado em `contains_sensitive_terms` e redigido quando aplicável.

## Endpoints

- `GET/POST /api/local-knowledge-rag/status`
- `GET/POST /api/local-knowledge-rag/panel`
- `GET/POST /api/local-knowledge-rag/policy`
- `GET/POST /api/local-knowledge-rag/rules`
- `POST /api/local-knowledge-rag/build-index`
- `POST /api/local-knowledge-rag/search`
- `POST /api/local-knowledge-rag/reuse-check`
- `POST /api/local-knowledge-rag/decision`
- `GET/POST /api/local-knowledge-rag/latest`
- `GET/POST /api/local-knowledge-rag/package`

## Decisão reuse-first

A resposta de decisão inclui:

- `decision_status`
- `recommendation`
- `top_results`
- `reuse_candidates`
- `context_pack_id`
- `safe_for_external_ai=false` por defeito
- próximos passos seguros

## Ligação a serviços existentes

A Phase 170 reutiliza:

- `CapabilityReuseService` para encontrar capacidades existentes no código;
- `MemoryContextRouterService` para preparar contexto AndreOS/Obsidian;
- `MemoryCoreService` para manter projeto/memória local.

## Futuro

V1 é lexical e local-first. Fases futuras podem adicionar:

- embeddings locais;
- vector store;
- índice de símbolos por linguagem;
- índice de frontmatter Obsidian;
- ranking por histórico de sucesso.
