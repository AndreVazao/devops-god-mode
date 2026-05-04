# Memory Sync Runtime

## Objetivo

A Phase 169 adiciona uma camada runtime para sincronizar memória técnica estável do God Mode depois de fases merged.

A camada separa claramente:

```txt
Evento técnico maduro
→ pacote estável de memória
→ AndreOS GitHub memory
→ nota Obsidian/local opcional
```

## Superfícies de memória

### GitHub memory

Destino: `AndreVazao/andreos-memory`.

Usar apenas para:

- histórico técnico de fases;
- PRs e merge commits;
- decisões técnicas estáveis;
- arquitetura/backlog técnico;
- última sessão de programação.

Não usar para:

- runtime vivo do PC;
- dados privados de clientes;
- tokens;
- passwords;
- cookies;
- API keys;
- private keys;
- dumps locais.

### Obsidian/local

Usar como oficina local:

- rascunhos;
- notas de continuação;
- trabalho real local;
- contexto operacional vivo do PC.

Programas cloud não dependem do Obsidian.

## Endpoints

- `GET/POST /api/memory-sync-runtime/status`
- `GET/POST /api/memory-sync-runtime/panel`
- `GET/POST /api/memory-sync-runtime/policy`
- `GET/POST /api/memory-sync-runtime/rules`
- `POST /api/memory-sync-runtime/register-merged-phase`
- `POST /api/memory-sync-runtime/build-package`
- `POST /api/memory-sync-runtime/prepare-obsidian-note`
- `POST /api/memory-sync-runtime/sync-stable`
- `POST /api/memory-sync-runtime/preview-merged-phase`
- `GET/POST /api/memory-sync-runtime/latest`
- `GET/POST /api/memory-sync-runtime/package`

## Fluxo v1

1. Registar evento `merged_phase`.
2. Sanitizar conteúdo.
3. Construir pacote estável para GitHub memory.
4. Preparar nota local/Obsidian opcional.
5. Executar sync em `dry_run` por defeito.
6. Quando permitido, escrever na memória local e acionar `github_memory_sync_service`.

## Segurança

O serviço bloqueia conteúdo com keywords sensíveis, incluindo:

- `password`
- `senha`
- `token`
- `api_key`
- `secret`
- `private_key`
- `cookie`
- `authorization`
- `bearer`
- `access_token`
- `refresh_token`

## Regra importante

Esta fase não substitui a memória local viva. Ela só promove informação técnica madura para memória GitHub e prepara notas locais quando útil.
