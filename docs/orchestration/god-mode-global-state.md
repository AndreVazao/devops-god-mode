# God Mode Global State + Operating Model

## Objetivo

A Phase 175 consolida o estado global do God Mode para reduzir perda de contexto entre conversas, commits e fases.

Ela adiciona um snapshot runtime em:

```txt
/api/god-mode-global-state/package
```

Esse package responde:

- fases implementadas;
- modelo operacional PC/telemóvel;
- modelo de memória GitHub/Obsidian/runtime;
- política de vault;
- modelo de auto-atualização;
- backlog técnico atualizado.

## Modelo operacional fixado

### PC de casa

O PC é o cérebro principal.

Responsabilidades:

- backend FastAPI;
- browser/providers/ferramentas locais;
- GitHub patches/PRs;
- builds Windows/Android;
- memória local;
- RAG local;
- futuro vault cifrado;
- staging de auto-update.

### Telemóvel

O telemóvel é o cockpit principal.

Responsabilidades:

- comandos;
- aprovações;
- monitorização;
- intervenção mínima em estrada/trabalho;
- credenciais temporárias quando inevitável;
- uso de `/app/home` como cockpit visual.

### PC como cockpit secundário

Quando o operador está em casa, o PC também usa `/app/home`.

## Memória

### GitHub AndreOS memory

Usada para memória técnica estável:

- decisões;
- arquitetura;
- histórico;
- backlog;
- última sessão;
- prompts.

Nunca guardar segredos.

### Obsidian/local

Usado como oficina viva local:

- rascunhos;
- notas locais;
- trabalho real local;
- contexto privado que não deve depender da cloud.

### Runtime do God Mode

Usado para estado vivo operacional:

- pipelines;
- fila de ações;
- outcomes;
- logs;
- índices locais.

## Vault

O vault ainda não está implementado como armazenamento cifrado completo.

Contrato definido:

- o PC terá vault local cifrado;
- GitHub só guarda referências/labels;
- telemóvel aprova desbloqueio/uso;
- logs só mostram IDs redigidos;
- providers externos não recebem segredos.

## Auto-update

O God Mode deve conseguir evoluir-se a si próprio.

Já existe:

- GitHub Approved Actions Executor;
- GitHub Actions como validação;
- Windows/Android artifacts;
- desktop update helper no bundle;
- Memory Sync Runtime.

Falta:

- self-update orchestrator;
- update channel manifest;
- staged update local;
- rollback;
- aprovação mobile antes de aplicar.

## Endpoints

- `GET/POST /api/god-mode-global-state/status`
- `GET/POST /api/god-mode-global-state/phases`
- `GET/POST /api/god-mode-global-state/operating-model`
- `GET/POST /api/god-mode-global-state/memory-model`
- `GET/POST /api/god-mode-global-state/vault-policy`
- `GET/POST /api/god-mode-global-state/self-update-model`
- `GET/POST /api/god-mode-global-state/backlog`
- `GET/POST /api/god-mode-global-state/package`

## Próximas fases recomendadas

1. Cockpit Runtime UX: polling, logs por botão, histórico visível.
2. Local Encrypted Vault Contract: storage cifrado e unlock por aprovação.
3. Self-Update Orchestrator: staged update + rollback + mobile approval.
