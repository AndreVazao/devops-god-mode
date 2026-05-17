# DevOps God Mode

Centro de controlo DevOps privado, local-first, com **PC como cérebro poderoso** e **telemóvel como cockpit principal**.

O God Mode existe para o André conseguir trabalhar e comandar projetos mesmo estando na rua: o PC de casa executa, valida, constrói, automatiza e mantém o contexto; o telemóvel dá ordens, aprova ações, acompanha progresso e fornece credenciais temporárias quando inevitável.

## Estado real atual

O projeto já não está em bootstrap inicial.

O `main` já contém fases operacionais até à **Phase 234**:

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


## Conetividade Resiliente (Tailscale)

Para garantir que o telemóvel e o PC estão sempre ligados, mesmo fora de casa, recomenda-se o uso do Tailscale:

- **IP do PC:**
- **IP do Telemóvel:**

Configure o seu  ou as definições do cockpit para usar o IP fixo do Tailscale em vez de IPs locais .

SHELL=/bin/bash
NVM_INC=/home/jules/.nvm/versions/node/v22.22.1/include/node
SUDO_GID=1001
TERM_PROGRAM_VERSION=3.4
TMUX=/tmp/tmux-1001/default,4136,0
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
DOTNET_ROOT=/usr/lib/dotnet
SUDO_COMMAND=/usr/bin/bash -c echo "${BASHPID}"
tmux new-session -d -s 'default' -c /app -e JULES_SESSION_ID=3528708876710451215 -e GIT_TERMINAL_PROMPT=0 && tmux set-option remain-on-exit on
SUDO_USER=jules
FLUTTER_HOME=/opt/flutter
PWD=/app
LOGNAME=jules
JULES_SESSION_ID=3528708876710451215
HOME=/home/jules
LANG=C.UTF-8
LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:
DOTNET_BUNDLE_EXTRACT_BASE_DIR=/home/jules/.cache/dotnet_bundle_extract
NVM_DIR=/home/jules/.nvm
LESSCLOSE=/usr/bin/lesspipe %s %s
ANDROID_HOME=/opt/android-sdk
TERM=tmux-256color
LESSOPEN=| /usr/bin/lesspipe %s
USER=jules
TMUX_PANE=%0
SHLVL=2
NVM_CD_FLAGS=
CHROME_EXECUTABLE=/usr/bin/google-chrome
DEBUGINFOD_URLS=https://debuginfod.ubuntu.com
BUN_INSTALL=/usr/local/bun
PATH=/home/jules/.nvm/versions/node/v22.22.1/bin:/home/jules/.pyenv/shims:/home/jules/.pyenv/bin:/home/jules/.local/bin:/opt/flutter/bin:/usr/lib/dotnet:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:/go/bin:/usr/local/go/bin:/usr/share/gradle/bin:/usr/share/maven/bin:/home/jules/.local/bin:/home/jules/.cargo/bin:/usr/local/bun/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin:/home/jules/.dotnet/tools
SUDO_UID=1001
NVM_BIN=/home/jules/.nvm/versions/node/v22.22.1/bin
MAIL=/var/mail/jules
GIT_TERMINAL_PROMPT=0
TERM_PROGRAM=tmux
OLDPWD=/app
_=/usr/bin/env

## Instalação Profissional (Windows)

O God Mode agora inclui um instalador profissional e um launcher blindado:

1. **Launcher Blindado ():** Monitoriza o backend e reinicia-o automaticamente em caso de crash.
2. **Setup Wizard ():** Instalador que configura pastas, atalhos e dependências automaticamente.

Para instalar, descarregue o  dos artifacts do GitHub Actions e siga as instruções no ecrã.

## Conetividade Resiliente (Tailscale)

Para garantir que o telemóvel e o PC estão sempre ligados, mesmo fora de casa, recomenda-se o uso do Tailscale:

- **IP do PC:** `100.69.225.48`
- **IP do Telemóvel:** `100.109.173.115`

Configure o seu `.env` ou as definições do cockpit para usar o IP fixo do Tailscale em vez de IPs locais `192.168.*`.

```env
BACKEND_URL=http://100.69.225.48:8000
```

## Instalação Profissional (Windows)

O God Mode agora inclui um instalador profissional e um launcher blindado:

1. **Launcher Blindado (`launcher.exe`):** Monitoriza o backend e reinicia-o automaticamente em caso de crash.
2. **Setup Wizard (`GodModeSetup.exe`):** Instalador que configura pastas, atalhos e dependências automaticamente.

Para instalar, descarregue o `GodModeSetup.exe` dos artifacts do GitHub Actions e siga as instruções no ecrã.
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
