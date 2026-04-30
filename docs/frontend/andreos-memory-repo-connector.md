# AndreOS Memory Repo Connector

## Objetivo

Ligar o God Mode ao repositório privado `AndreVazao/andreos-memory` como memória externa AndreOS/Obsidian.

Esta fase cria uma ponte para leitura, auditoria e handoff de contexto.

## Repositório externo

- Repo: `AndreVazao/andreos-memory`
- Visibilidade esperada: privado
- Vault: `AndreOS/`

## Endpoints

- `GET/POST /api/andreos-memory-repo/status`
- `GET/POST /api/andreos-memory-repo/panel`
- `GET/POST /api/andreos-memory-repo/structure`
- `GET/POST /api/andreos-memory-repo/audit`
- `GET/POST /api/andreos-memory-repo/seed-plan`
- `GET /api/andreos-memory-repo/project/{project_id}`
- `GET /api/andreos-memory-repo/handoff-prompt/{project_id}`
- `GET/POST /api/andreos-memory-repo/package`

## Projetos reconhecidos

- GOD_MODE
- PROVENTIL
- VERBAFORGE
- BOT_LORDS_MOBILE
- ECU_REPRO
- BUILD_CONTROL_CENTER
- PERSONA_FORGE
- VOX
- BOT_FACTORY

## Comportamento

- Lê a estrutura esperada.
- Audita ficheiros globais e por projeto.
- Lê ficheiros do projeto pedido.
- Gera prompt de handoff para outros chats/providers.
- Gera plano para seed dos projetos que ainda faltam.

## Segurança

- Não guarda credenciais no código.
- Usa a configuração GitHub existente do backend.
- Bloqueia caminhos fora de `AndreOS/` e `README.md`.
- Não lê nem escreve ficheiros de ambiente ou segredos.
- A escrita real fica para uma fase posterior com aprovação explícita.

## Resultado

O God Mode passa a reconhecer o repo AndreOS externo como fonte de memória persistente e consegue verificar se a memória está pronta para ser usada antes de responder ou executar tarefas.
