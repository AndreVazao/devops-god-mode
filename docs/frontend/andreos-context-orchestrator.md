# AndreOS Context Orchestrator

## Objetivo

Ligar, de forma centralizada, o God Mode, Obsidian, o repo externo `AndreVazao/andreos-memory` e os chats/providers de IA.

O God Mode passa a ser o orquestrador principal do contexto:

- recebe pedido do operador;
- identifica projeto;
- consulta memória AndreOS;
- cria contexto compacto;
- prepara brief para IA/provider;
- reconcilia resposta;
- prepara delta de memória para guardar depois com gate próprio.

## Endpoints

- `GET/POST /api/andreos-context/status`
- `GET/POST /api/andreos-context/panel`
- `GET/POST /api/andreos-context/topology`
- `GET/POST /api/andreos-context/readiness`
- `GET /api/andreos-context/context/{project_id}`
- `GET /api/andreos-context/brief/{project_id}?target=chatgpt`
- `GET /api/andreos-context/sync-plan/{project_id}`
- `GET/POST /api/andreos-context/policy`
- `GET/POST /api/andreos-context/package`

## Fontes ligadas

- PC/backend God Mode
- Obsidian local
- repo privado `AndreVazao/andreos-memory`
- chats/providers de IA
- repos dos projetos

## Regra operacional

Antes de falar com uma IA externa, o God Mode deve gerar um context pack AndreOS do projeto ativo.

Depois de receber resposta útil, o God Mode deve reconciliar a resposta com o estado real do projeto e preparar um resumo/decisão para memória.

## Home / Modo Fácil

A Home passa a ter o botão:

- `Contexto AndreOS` → `/api/andreos-context/panel`

E o comando rápido:

- `open_andreos_context`

## Segurança

- Sem guardar dados sensíveis.
- Sem escrita automática nesta fase.
- Sem confiar cegamente em providers.
- Sem substituir o God Mode como fonte operacional.
- A escrita futura para memória deve usar gate próprio.

## Resultado

O God Mode deixa de tratar memória, Obsidian e chats como peças soltas. Passa a existir uma camada central que prepara contexto compacto e mantém continuidade entre sessões e providers.
