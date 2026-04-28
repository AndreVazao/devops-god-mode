# First Real Install Launcher

## Objetivo

A Phase 95 transforma o estado `ready_to_install` num plano operacional direto para instalares e arrancares o God Mode de verdade.

Em vez de mais um módulo solto, isto fica ligado à Home através da ação rápida:

- `Instalar agora`
- `/api/first-real-install-launcher/plan`

## Endpoints

- `GET /api/first-real-install-launcher/status`
- `GET /api/first-real-install-launcher/plan`
- `POST /api/first-real-install-launcher/plan`
- `GET /api/first-real-install-launcher/package`

## O que devolve

O plano devolve:

- estado geral `ready_to_launch` ou `blocked`;
- blockers concretos;
- botão principal para APK/EXE;
- cartões de instalação para PC, APK e primeira ordem real;
- nomes dos artifacts esperados;
- ações principais da Home;
- contrato de segurança.

## Cartões principais

1. **PC: abrir GodModeDesktop.exe**
   - artifact: `godmode-windows-exe`
   - ficheiro: `GodModeDesktop.exe`

2. **Telemóvel: instalar GodModeMobile-debug.apk**
   - artifact: `godmode-android-webview-apk`
   - ficheiro: `GodModeMobile-debug.apk`

3. **Primeira ordem real**
   - abrir Home;
   - carregar em `Instalação final`;
   - correr `Teste geral`;
   - mandar primeira ordem real.

## Ligação à Home

A Home passa a incluir:

```json
{
  "id": "first_real_install_launcher",
  "label": "Instalar agora",
  "endpoint": "/api/first-real-install-launcher/plan",
  "priority": "critical"
}
```

Assim, o operador não precisa decorar endpoints técnicos.

## Segurança

- Não apaga dados.
- Não altera `.env`.
- Não altera `backend/.env`.
- Não altera `data/` ou `memory/`.
- Não substitui aprovações.
- O backend continua desenhado para só parar por fim, OK, intervenção manual ou bloqueio seguro.

## Critério de aceitação

A validação da fase deve confirmar:

- rotas `/api/first-real-install-launcher/*`;
- Home com ação `Instalar agora`;
- plano com APK e EXE corretos;
- blockers explícitos quando existirem;
- docs;
- Project Tree Autorefresh.
