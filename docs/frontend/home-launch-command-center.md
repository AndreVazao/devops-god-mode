# Home Launch Command Center

## Objetivo

A Phase 141 liga o caminho final de instalação/download diretamente ao Modo Fácil/Home.

O objetivo é não deixar o operador perdido em endpoints técnicos quando chegar a hora de instalar e usar de verdade.

## Endpoints

- `GET/POST /api/home-launch/status`
- `GET/POST /api/home-launch/panel`
- `GET/POST /api/home-launch/latest`
- `GET/POST /api/home-launch/package`

## O que agrega

- Final Install Readiness v2
- Download Install Center v2
- APK ↔ PC Pairing Wizard
- Real Install Smoke Test
- Self Update Manager
- Mobile APK Update Orchestrator
- Project Memory Registry
- File intake/transfer

## Botões adicionados ao Modo Fácil

- `Instalar / Baixar` → `/api/home-launch/panel`
- `Pronto para instalar?` → `/api/final-install-readiness-v2/check`
- `Baixar APK/EXE` → `/api/download-install-center-v2/panel`

## Campos novos no Modo Fácil

- `launch_center_endpoint`
- `download_install_endpoint`
- `final_readiness_endpoint`

## Quick command novo

- `open_launch_center`

Mensagem:

`abre o centro de instalação, download, pairing e primeiro teste real`

## Caminho de instalação exposto

1. Verificar pronto para instalar.
2. Baixar EXE/APK.
3. Abrir EXE no PC.
4. Emparelhar telemóvel.
5. Abrir Modo Fácil.
6. Fazer primeiro comando real.

## Regra

Tudo que aproxima a instalação real deve aparecer na Home/Modo Fácil, não ficar escondido em rotas técnicas.
