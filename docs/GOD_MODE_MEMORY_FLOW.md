# God Mode Memory Flow

## Fluxo operacional

1. O operador pede uma ação no telemóvel.
2. O God Mode identifica o projeto ativo.
3. O Memory Core lê `MEMORIA_MESTRE.md`, `DECISOES.md`, `ARQUITETURA.md`, `BACKLOG.md` e `ULTIMA_SESSAO.md`.
4. O ContextAssembler gera contexto compacto para a IA.
5. A IA responde ou propõe ação.
6. A ApprovalGate bloqueia ações de risco sem aprovação.
7. A ação aprovada segue para o fluxo próprio do God Mode.
8. A decisão fica registada em `DECISOES.md`.
9. A alteração fica registada em `HISTORICO.md`.
10. O estado final fica em `ULTIMA_SESSAO.md`.

## Antes de responder sobre um projeto

Consultar a memória do projeto.

## Antes de alterar código

Consultar:

- `ARQUITETURA.md`
- `DECISOES.md`
- `BACKLOG.md`
- `ULTIMA_SESSAO.md`

## Depois de alterar código

Atualizar:

- `HISTORICO.md`
- `ULTIMA_SESSAO.md`

## Operações sensíveis

Qualquer operação sensível precisa de aprovação explícita do operador.

## Pesquisa semântica futura

A fase atual usa Markdown. O próximo salto técnico é indexar o vault com embeddings e guardar vetores numa base local ou híbrida.
