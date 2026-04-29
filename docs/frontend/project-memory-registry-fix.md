# Project Memory Registry Fix

## Objetivo

A Phase 136 cria uma fonte canónica de projetos principais para o God Mode não se esquecer de projetos importantes.

Esta fase corrige a falta de projetos como:

- God Mode
- Bot Factory
- Persona Forge
- Vox
- VerbaForge
- Baribudos Studio
- ProVentil
- Lords Mobile Bot / Farm
- ECU Repro / Diagnóstico
- GCode / CNC Converter
- AndreOS / Obsidian Memory

## Endpoints

- `GET/POST /api/project-memory-registry/status`
- `GET/POST /api/project-memory-registry/panel`
- `GET/POST /api/project-memory-registry/projects`
- `POST /api/project-memory-registry/seed`
- `POST /api/project-memory-registry/upsert`
- `GET/POST /api/project-memory-registry/audit`
- `POST /api/project-memory-registry/sync-memory`
- `GET/POST /api/project-memory-registry/latest`
- `GET/POST /api/project-memory-registry/package`

## Campos por projeto

Cada projeto contém:

- `project_id`
- `display_name`
- `status`
- `priority`
- `category`
- `description`
- `expected_memory_path`
- `repo_hints`
- `conversation_hints`
- `next_actions`

## Funções

### Seed

Garante que os projetos base existem.

### Audit

Confirma se todos os projetos obrigatórios existem e têm caminho de memória.

### Sync memory

Chama o `memory_context_router` para preparar contexto/memória para cada projeto.

### Upsert

Permite adicionar projetos novos no futuro sem mexer manualmente no código.

## Regra

O God Mode deve usar este registry como lista base de projetos reais e manter a memória AndreOS/Obsidian atualizada conforme surgirem decisões, conversas e alterações.
