# God Mode Memory Flow

## Fluxo operacional

1. O operador pede uma ação no telemóvel.
2. O Operator Command Intake identifica o projeto ativo.
3. O Memory Core inicializa a estrutura, cria o projeto se faltar e lê `MEMORIA_MESTRE.md`, `DECISOES.md`, `ARQUITETURA.md`, `BACKLOG.md` e `ULTIMA_SESSAO.md`.
4. O ContextAssembler gera contexto compacto e anexa um preview seguro ao comando.
5. O plano de execução passa a incluir `load-andreos-project-memory` antes de qualquer auditoria ou ação.
6. A IA responde ou propõe ação usando a memória do projeto.
7. A ApprovalGate e o Mobile Approval Cockpit bloqueiam ações sensíveis sem aprovação.
8. Quando o operador aprova/rejeita um cartão, a decisão fica registada em `DECISOES.md`.
9. O histórico da decisão fica registado em `HISTORICO.md`.
10. No fim da sessão, `ULTIMA_SESSAO.md` deve ser atualizado.

## Integração já ativa

- `operator_command_intake_service.py` consulta o AndreOS Memory Core ao receber comandos.
- Cada comando passa a carregar `memory_core.memory_project`, `context_chars`, `context_preview` e link Obsidian.
- O plano de execução inclui leitura de memória e persistência de sessão.
- `mobile_approval_cockpit_v2_service.py` grava decisões aprovadas/rejeitadas em `DECISOES.md` e `HISTORICO.md`.

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
