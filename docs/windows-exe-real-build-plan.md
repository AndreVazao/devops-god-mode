# Windows EXE Real Build Plan

## Branch
- `feature/windows-exe-real-build`

## Objetivo
Dar o passo seguinte ao packaging desktop: sair do `.exe` placeholder e gerar um executável Windows mais real para o God Mode Desktop, com arranque simples, configuração automática inicial e abertura do cockpit local.

## Meta funcional
- criar launcher desktop real para Windows
- definir config local automática no primeiro arranque
- abrir cockpit local no browser por default
- deixar o `.exe` preparado para uso simples a partir da área de trabalho
- manter o PC como runtime principal e o telemóvel como cockpit remoto complementar

## Blocos desta fase
### 1. Desktop launcher
Criar um launcher Python real para Windows que:
- inicializa config local
- grava defaults zero-touch
- prepara backend_url e shell_url locais
- abre o cockpit no browser

### 2. PyInstaller spec
Criar `.spec` para build onefile/windowed.

### 3. Windows build workflow
Atualizar workflow para:
- instalar PyInstaller
- buildar o launcher real
- gerar `GodModeDesktop.exe`
- publicar artifact em modo best-effort

### 4. Scope
Esta fase ainda não fecha o instalador completo do PC.
Fecha a base do `.exe` real e do launcher desktop.
