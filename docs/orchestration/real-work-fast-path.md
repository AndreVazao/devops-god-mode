# Real Work Intake Map + First PC Fast Path

## Objetivo

A Phase 193 torna o God Mode mais prático para uso real imediato no PC e no telemóvel.

Ela junta duas coisas críticas:

1. **First PC Fast Path** — caminho rápido para instalar/testar no PC.
2. **Real Work Map** — mapa de projetos, repos, conversas e frentes do mesmo produto.

## Endpoint principal

```txt
/api/real-work-fast-path/package
```

## Página visual

```txt
/app/real-work-fast-path
/app/real-work-map
```

## Endpoints

- `/api/real-work-fast-path/status`
- `/api/real-work-fast-path/policy`
- `/api/real-work-fast-path/seed-defaults`
- `/api/real-work-fast-path/add-project-group`
- `/api/real-work-fast-path/link-repo`
- `/api/real-work-fast-path/link-conversation`
- `/api/real-work-fast-path/classify-text`
- `/api/real-work-fast-path/create-work-run`
- `/api/real-work-fast-path/first-pc-fast-path`
- `/api/real-work-fast-path/dashboard`
- `/api/real-work-fast-path/package`

## Grupos default

- `god_mode`
- `baribudos_platform`
- `proventil`

## Decisão Baribudos

`website` e `studio` são tratados como frentes relacionadas do mesmo produto/ecossistema enquanto o Oner não mandar separar.

Aliases reconhecidos incluem variações ditadas/faladas:

- baribudos;
- barbudo;
- baribudos website;
- baribudos studio;
- very beach;
- beybus;
- barbudo studio.

## O que isto permite

- Ligar repos a grupos/produtos.
- Ligar conversas a grupos/produtos.
- Classificar texto em grupo + frente.
- Criar work run real a partir de uma ordem do Oner.
- Criar broadcast plan ligado ao ledger.
- Gerar checklist de primeiro teste no PC.

## Regra de realidade

Nada fica como fantasia:

- repo/conversa tem grupo;
- repo/conversa tem frente;
- repo/conversa tem evidência;
- incerteza vai para revisão do operador;
- respostas das IAs continuam a não ser decisão final.

## Segurança

- Não guarda segredos.
- Não faz ações destrutivas.
- Não junta repos sem evidência/revisão.
- Não transforma resposta de IA em decisão.

## Primeiro teste real recomendado

1. Abrir `GodModeDesktop.exe` no PC.
2. Confirmar `/app/home`.
3. Abrir `/app/real-work-fast-path`.
4. Ligar uma repo ao grupo correto.
5. Ligar uma conversa ao grupo correto.
6. Criar um work run.
7. Abrir Broadcast IA.
8. Colar/importar uma resposta.
9. Rever no ledger.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 192 deve ser apagado. Fica só:

- `.github/workflows/phase193-real-work-fast-path-smoke.yml`

Além dos workflows globais/builds.
