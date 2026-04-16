# Selective Merge Policy

## Objetivo
Manter o `main` limpo e evitar merges que tragam ficheiros antigos, obsoletos ou alterações colaterais não desejadas.

## Regra principal
Para evoluções futuras do God Mode:
- criar sempre uma branch nova por fase
- mexer apenas nos ficheiros necessários para essa fase
- evitar acumular várias fases diferentes na mesma branch
- abrir PR pequena e focada
- preferir merge normal ou rebase merge quando a PR está limpa
- evitar squash quando a PR mistura demasiado histórico que dificulte rastreio

## Fluxo recomendado
1. partir sempre do `main` atual
2. criar branch com nome de fase clara
3. mexer só nos ficheiros dessa fase
4. correr smoke/tests
5. abrir PR
6. rever changed files
7. confirmar que a PR não toca em ficheiros fora do âmbito
8. só depois fazer merge

## Quando usar merge commit
Usar quando:
- a branch representa uma fase fechada
- queres manter o histórico visível
- queres evitar reescrever contexto de vários commits úteis

## Quando usar rebase merge
Usar quando:
- a branch está limpa
- os commits estão organizados
- queres histórico mais linear sem commit de merge extra

## Quando evitar squash merge
Evitar quando:
- a branch mistura várias etapas relevantes
- queres preservar a sequência real das mudanças
- existe risco de perder clareza sobre o que foi feito em cada commit

## Regra prática para este projeto
### Preferência
- branch curta por fase
- PR pequena
- rebase merge ou merge commit

### Evitar
- branch longa com muita coisa misturada
- squash merge de branch confusa
- alterações diretas no `main` para mudanças grandes

## Estratégia futura recomendada
### Branch de funcionalidade
Exemplos:
- `feature/hybrid-local-runtime-prep`
- `feature/mobile-shell-driving-mode`
- `feature/mobile-shell-assisted-mode`
- `feature/local-tunnel-prep`
- `fix/repo-tree-supabase-dns`

### Branch de limpeza
Exemplos:
- `chore/consolidate-entrypoints`
- `chore/remove-obsolete-ops-versions`
- `chore/remove-old-smoke-workflows`

## Regra de segurança
Antes de qualquer merge:
- rever separador `Files changed`
- confirmar que só entram ficheiros mexidos dessa fase
- se a PR estiver poluída, criar nova branch limpa a partir do `main` e reaplicar só os ficheiros certos
