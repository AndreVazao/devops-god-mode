# Desktop Bootstrap Shortcut Autostart Plan

## Branch
- `feature/desktop-bootstrap-shortcut-autostart`

## Objetivo
Deixar o God Mode Desktop mais perto do modo `abrir e trabalhar`: bootstrap de primeira execução, atalho de área de trabalho, autostart opcional e defaults zero-touch para o PC principal.

## Meta funcional
- representar perfil de bootstrap desktop
- guardar preferências de first run
- modelar atalho desktop e autostart
- preparar geração automática de ficheiros de bootstrap local
- manter UI intuitiva e configuração mínima

## Blocos desta fase
### 1. Desktop bootstrap contract
Representar:
- bootstrap_id
- runtime_mode
- desktop_shortcut
- autostart
- first_run_actions
- local_backend_url
- local_shell_url
- bootstrap_status

### 2. Desktop bootstrap service
Criar serviço para:
- devolver defaults zero-touch
- gerar payload de first run
- listar perfis de bootstrap desktop
- ativar/desativar autostart lógico

### 3. Desktop bootstrap routes
Endpoints para:
- status
- listar perfis
- gerar first-run payload
- ativar autostart
- desativar autostart

### 4. Future runtime direction
Preparar a fase seguinte para:
- script local de criação do atalho
- script local de registo de autostart
- integração do launcher desktop com first-run bootstrap
