# DevOps God Mode

Centro de controlo DevOps privado, local-first, com **PC como cérebro poderoso** e **telemóvel como cockpit principal**.

O God Mode existe para o André conseguir trabalhar e comandar projetos mesmo estando na rua: o PC de casa executa, valida, constrói, automatiza e mantém o contexto; o telemóvel dá ordens, aprova ações, acompanha progresso e fornece credenciais temporárias quando inevitável.

## Estado real atual

O projeto já não está em bootstrap inicial.

O `main` já contém fases operacionais até à **Phase 174**:

- Ecosystem Map operacional;
- Ruflo/Praison como laboratórios de pesquisa, não dependências centrais;
- Goal Planner;
- AI Handoff Security Guard;
- Agent Roles Registry;
- AI Provider Router;
- MCP Compatibility Map;
- Real Orchestration Pipeline;
- Orchestration Playbooks;
- Pipeline Persistence + Low-Risk Executor;
- Execution Modes Engine;
- Playbook Templates Library;
- GitHub Approved Actions Executor;
- Memory Sync Runtime;
- Local Knowledge/RAG Decision v1;
- Provider Outcome Learning;
- Home/App Control Surface;
- Home Visual Shell;
- Launcher/App Default Home Route.

A rota canónica do cockpit é:

```text
/app/home
```

Manifesto oficial de entrypoint:

```text
/api/app-entrypoint/manifest
```

Package principal da Home/App:

```text
/api/home-control-surface/package
```

## Modelo operacional

### PC em casa = cérebro principal

Responsável por:

- correr o backend FastAPI;
- manter o runtime local;
- controlar browser/provedores/ferramentas quando aprovado;
- preparar branches, commits e PRs;
- validar com GitHub Actions;
- gerar builds Windows/Android;
- manter memória local e índices locais;
- futuramente guardar o vault local cifrado de credenciais.

### Telemóvel = cockpit principal

Responsável por:

- enviar ordens ao PC;
- aprovar/rejeitar ações com gates;
- acompanhar o que o PC está a fazer;
- operar em modo rua/condução/trabalho;
- fornecer credenciais temporárias quando não houver alternativa;
- abrir a Home Visual Shell via `/app/home`.

### PC também tem cockpit

Quando o André está em casa, o mesmo cockpit visual abre no browser/launcher do PC:

```text
http://127.0.0.1:8000/app/home
```

## Cockpit visual

A Home Visual Shell é servida pelo backend e consome dados reais do God Mode.

Endpoints principais:

```text
GET /app/home
GET /api/home-visual-shell/package
GET /api/home-control-surface/package
GET /api/app-entrypoint/manifest
```

Aliases de compatibilidade apontam para `/app/home`:

```text
/app
/desktop
/mobile
/home
/app/mobile
/app/apk-start
```

## GitHub Approved Actions

O God Mode consegue preparar alterações em repos com aprovação explícita.

Endpoint base:

```text
/api/github-approved-actions/*
```

Frase de aprovação para aplicar patch aprovado:

```text
APPLY REPO PATCH
```

Regras duras:

- não faz merge automático;
- não faz release automático;
- não faz delete/force-push;
- não altera pagamentos/licenças/credenciais;
- merge só depois de GitHub Actions verdes e aprovação explícita do Oner.

## Memória persistente

Existem duas memórias com funções diferentes.

```text
AndreOS GitHub Memory
└── repo privado AndreVazao/andreos-memory
    ├── decisões técnicas
    ├── arquitetura
    ├── histórico de fases
    ├── backlog
    ├── última sessão
    └── prompts técnicos
```

```text
Obsidian/local/PC
└── oficina viva local
    ├── rascunhos
    ├── notas locais
    ├── trabalho em progresso
    ├── memória operacional do PC
    └── contexto que não deve depender da cloud
```

Nunca guardar em GitHub/README/docs/memória técnica:

- tokens;
- passwords;
- cookies;
- API keys;
- chaves privadas;
- segredos de clientes;
- credenciais pessoais.

Endpoint de memória técnica/runtime:

```text
/api/memory-sync-runtime/*
/api/github-memory-sync/*
```

## Vault de credenciais

O vault ainda é fase futura de alta prioridade.

Política definida:

- credenciais reais devem ficar num vault local cifrado no PC;
- GitHub/AndreOS só pode guardar referências/labels, nunca valores;
- o telemóvel pode aprovar uso/desbloqueio;
- logs devem mostrar IDs/redações, nunca segredos;
- providers externos não devem receber segredos no contexto.

Endpoint de política global:

```text
/api/god-mode-global-state/vault-policy
```

## Auto-atualização

Objetivo estratégico: o God Mode conseguir melhorar-se a si próprio.

O que já existe:

- executor aprovado consegue criar branch/ficheiros/PR;
- GitHub Actions validam Universal, Android, Windows e smokes;
- artifacts Windows/Android são gerados;
- helper de update desktop já entra no bundle;
- Memory Sync Runtime regista fases merged.

O que ainda falta:

- self-update orchestrator;
- manifest de canal de update;
- update staging no PC;
- rollback local;
- aprovação mobile antes de aplicar update;
- fluxo de release/update seguro.

Regra: auto-update pode preparar, validar e propor; aplicar update final continua com gate do Oner.

## APIs de estado global

A Phase 175 introduz um snapshot runtime para evitar perda de contexto.

```text
GET /api/god-mode-global-state/status
GET /api/god-mode-global-state/phases
GET /api/god-mode-global-state/operating-model
GET /api/god-mode-global-state/memory-model
GET /api/god-mode-global-state/vault-policy
GET /api/god-mode-global-state/self-update-model
GET /api/god-mode-global-state/backlog
GET /api/god-mode-global-state/package
```

## Validação

Antes de merges relevantes, validar com GitHub Actions:

- Universal Total Test;
- Android APK Build;
- Windows EXE Build com boot smoke desktop backend;
- smokes das fases relevantes;
- Artifact Download Shortcuts Validation.

## Legado

Supabase, Render e Vercel são legado arquitetural/histórico. Podem existir referências antigas, mas não são o caminho principal.

O caminho atual é:

```text
PC local-first brain + mobile cockpit + GitHub technical memory + controlled cloud/build pipelines
```
