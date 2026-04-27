# AndreOS Memory Audit

## Objetivo

Validar se o AndreOS Memory Core / Obsidian está pronto para uso real do God Mode sem perder contexto.

A auditoria confirma:

- estrutura `memory/vault/AndreOS`;
- projetos principais;
- ficheiros obrigatórios por projeto;
- links `obsidian://`;
- contexto compacto para IA;
- bloqueio de termos sensíveis;
- ensaio real seguro de decisão, histórico, backlog e última sessão.

## API

- `GET /api/andreos-memory-audit/status`
- `GET /api/andreos-memory-audit/package`
- `GET /api/andreos-memory-audit/audit?run_rehearsal=true`

## Projetos auditados

- `GOD_MODE`
- `PROVENTIL`
- `VERBAFORGE`
- `BOT_LORDS_MOBILE`
- `ECU_REPRO`
- `BUILD_CONTROL_CENTER`
- `BARIBUDOS_STUDIO`
- `BARIBUDOS_STUDIO_WEBSITE`
- `BOT_FACTORY`

## Ficheiros obrigatórios por projeto

- `MEMORIA_MESTRE.md`
- `DECISOES.md`
- `BACKLOG.md`
- `ROADMAP.md`
- `ARQUITETURA.md`
- `HISTORICO.md`
- `PROMPTS.md`
- `ERROS.md`
- `ULTIMA_SESSAO.md`

## Ensaio real seguro

Quando `run_rehearsal=true`, a auditoria escreve apenas conteúdo operacional seguro em `GOD_MODE`:

- decisão;
- histórico;
- backlog;
- última sessão;
- contexto compacto.

Também tenta escrever um texto com termos sensíveis falsos para confirmar que o filtro bloqueia esse tipo de conteúdo.

## Segurança

- Não grava passwords, tokens, cookies, bearer ou API keys.
- Não altera `.env`.
- Não apaga `data/` nem `memory/`.
- Não faz ações destrutivas.
- Só valida e escreve memória operacional segura.

## Critério de pronto

Estado `ready` significa que:

- todos os projetos principais têm estrutura;
- todos os ficheiros obrigatórios existem;
- filtro de segredos está ativo;
- contexto compacto funciona;
- links Obsidian são gerados;
- ensaio seguro passou.
