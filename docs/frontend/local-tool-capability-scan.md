# Local Tool Capability Scan

## Objetivo

A Phase 118 adiciona um check-up local de ferramentas instaladas no PC.

No primeiro arranque, o God Mode deve perceber que ferramentas já existem e que partes pode aproveitar localmente antes de depender apenas de browser, cloud ou GitHub Actions.

## Endpoints

- `GET/POST /api/local-tool-capability/status`
- `GET/POST /api/local-tool-capability/panel`
- `GET/POST /api/local-tool-capability/scan`
- `GET/POST /api/local-tool-capability/plan`
- `GET/POST /api/local-tool-capability/latest`
- `GET/POST /api/local-tool-capability/package`

## Ferramentas avaliadas

- Obsidian
- Visual Studio Code
- Git
- Python
- Node.js / npm / npx
- Android Studio
- Android SDK / ADB
- PowerShell
- Chrome / Edge
- Codex CLI
- Claude CLI
- Ollama / Local LLM

## Estados possíveis

- `available`: ferramenta encontrada e útil.
- `partial_or_broken`: ferramenta encontrada mas incompleta ou com dependência essencial em falta.
- `not_found`: não encontrada.

## Lanes geradas

### Memória e contexto

Usa Obsidian/AndreOS se existir. Se não existir, usa ficheiros Markdown locais.

### Edição local de código

Usa VS Code, Git, Python e Node quando disponíveis para preparar patches, diffs e validações antes de PR/upload.

### Android/APK

Usa Android SDK/ADB local se existir. Se Android Studio estiver instalado mas incompleto, prefere GitHub Actions para builds.

### Providers e IA local

Usa Codex CLI, Claude CLI, Ollama ou browser como apoio, sem substituir a política principal de memória e aprovação.

### Automação Windows

Usa PowerShell para atalhos, arranque local e tarefas aprovadas.

## Segurança

O scan é read-only.

Não executa instalações, não altera ficheiros, não cria repos e não faz upload sozinho.

## Resultado esperado

O God Mode consegue escolher automaticamente:

- trabalhar localmente quando as ferramentas são fiáveis;
- preparar ficheiros localmente e depois abrir PR/upload;
- usar GitHub Actions quando o PC antigo não aguenta builds;
- não insistir em ferramenta quebrada;
- aproveitar Obsidian, VS Code, Git, Python, browser e IA local quando fizer sentido.
