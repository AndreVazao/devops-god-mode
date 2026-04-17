# Windows Shortcut And Autostart Scripts Plan

## Branch
- `feature/windows-shortcut-autostart-scripts`

## Objetivo
Fechar a parte prática do bootstrap desktop com scripts reais de Windows para criar atalho na área de trabalho e registar autostart, mantendo o build online grátis no GitHub Actions como caminho de apoio para gerar e validar o pacote desktop.

## Meta funcional
- criar script real para atalho desktop
- criar script real para autostart no Startup folder do Windows
- preparar remoção/desativação de autostart
- alinhar os scripts com os payloads gerados em `%APPDATA%/GodModeDesktop`
- incluir estes assets no packaging online do Actions

## Blocos desta fase
### 1. Script contract
Representar:
- script_id
- script_type
- payload_source
- target_path
- execution_mode
- script_status

### 2. Desktop helper scripts
Criar scripts para:
- criar atalho `.url` no desktop
- criar launcher `.cmd` para autostart no Startup folder
- remover launcher de autostart

### 3. Actions packaging alignment
Atualizar workflow de `.exe` real para:
- incluir scripts auxiliares
- publicar pacote desktop mais completo
- continuar com upload best-effort

### 4. Scope
Esta fase não fecha ainda um instalador Windows completo.
Fecha a automação prática de shortcut e autostart com apoio do build online grátis no Actions.
