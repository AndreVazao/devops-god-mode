# Local Bootstrap Backup

## Objetivo

A Phase 119 prepara duas capacidades importantes para o God Mode:

1. Plano de instalação/configuração das ferramentas locais que faltam.
2. Backup portátil para migrar memória, dados permitidos e configuração para outro PC.

## Endpoints

- `GET/POST /api/local-bootstrap-backup/status`
- `GET/POST /api/local-bootstrap-backup/panel`
- `GET/POST /api/local-bootstrap-backup/requirements`
- `GET/POST /api/local-bootstrap-backup/plan`
- `POST /api/local-bootstrap-backup/install-script`
- `POST /api/local-bootstrap-backup/create-backup`
- `POST /api/local-bootstrap-backup/restore-preview`
- `GET/POST /api/local-bootstrap-backup/latest`
- `GET/POST /api/local-bootstrap-backup/package`

## Ferramentas planeadas

- Git
- Python
- VS Code
- Node.js LTS
- Obsidian
- Chrome ou Edge
- Android SDK / ADB
- Ollama / IA local opcional

## Instalação/configuração

O God Mode não instala silenciosamente.

Ele gera:

- plano de instalação;
- lista de ferramentas disponíveis;
- lista de ferramentas em falta;
- lista de ferramentas a saltar em PC fraco;
- script PowerShell para o operador rever e executar se aprovar.

## PC antigo vs PC novo

Em PC antigo/fraco:

- instala apenas ferramentas leves quando possível;
- evita forçar Android/IA local pesada;
- prefere GitHub Actions para builds pesados;
- marca ferramentas quebradas como parciais.

Em PC novo/forte:

- pode preparar mais ferramentas locais;
- pode usar Android SDK/ADB local;
- pode usar IA local opcional;
- continua a depender de aprovação antes de ações reais.

## Backup portátil

O backup cria um ZIP em `data/backups/` ou no caminho indicado pelo operador.

Inclui por defeito:

- `memory/`
- `data/`
- `docs/`
- configurações públicas do mobile shell;
- scripts Windows;
- README;
- PROJECT_TREE.

## Segurança do backup

O backup exclui por nome caminhos sensíveis como ficheiros de ambiente, segredos, credenciais, tokens e chaves.

Também inclui:

- `BACKUP_MANIFEST.json`
- `RESTORE_README.txt`

## Restore

O endpoint `restore-preview` apenas lê o ZIP e mostra o que seria restaurado.

Não sobrescreve nada sem uma fase futura de restore aprovado.

## Próximo passo recomendado

Phase 120 deve criar o `restore-approved-runner`, para restaurar memória e configurações no PC novo com preview, aprovação, backup antes de sobrescrever e rollback.
