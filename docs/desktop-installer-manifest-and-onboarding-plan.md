# Desktop Installer Manifest And Onboarding Plan

## Branch
- `feature/desktop-installer-manifest-and-onboarding`

## Objetivo
Preparar a camada seguinte para o Windows: manifesto do instalador desktop, pacote de onboarding do primeiro uso e alinhamento do build online do Actions com um bundle cada vez mais pronto para instalar e usar.

## Meta funcional
- definir manifesto do instalador desktop
- definir sequência de onboarding do primeiro uso
- alinhar bundle desktop com bootstrap, shortcut, autostart e pairing
- aproximar o pacote do modo `abrir e trabalhar`

## Blocos desta fase
### 1. Installer manifest contract
Representar:
- installer_id
- package_name
- primary_executable
- support_scripts
- onboarding_assets
- install_mode
- installer_status

### 2. Onboarding contract
Representar:
- onboarding_id
- runtime_mode
- steps
- desktop_assets
- mobile_assets
- pairing_required
- onboarding_status

### 3. Services and routes
Criar backend para:
- devolver manifesto do instalador
- devolver pacote de onboarding
- listar sequência recomendada de instalação e primeiro uso

### 4. Build alignment
Atualizar o build Windows real para incluir:
- manifest.json do pacote desktop
- onboarding.json
- bundle mais claro para instalação local
