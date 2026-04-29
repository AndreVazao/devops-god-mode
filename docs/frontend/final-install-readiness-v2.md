# Final Install Readiness v2

## Objetivo

A Phase 139 cria o gate final antes de o operador instalar o God Mode no PC e no telefone.

Este gate responde diretamente:

> Posso instalar agora para primeiro teste real?

## Endpoints

- `GET/POST /api/final-install-readiness-v2/status`
- `GET/POST /api/final-install-readiness-v2/panel`
- `GET/POST /api/final-install-readiness-v2/check`
- `GET/POST /api/final-install-readiness-v2/install-contract`
- `GET/POST /api/final-install-readiness-v2/latest`
- `GET/POST /api/final-install-readiness-v2/package`

## O que valida

- APK workflow
- EXE workflow
- Home / Modo Fácil
- Ações críticas
- Smoke test CI seguro
- APK ↔ PC pairing
- Jobs retomáveis
- Self-update
- Mobile APK update
- Project Memory Registry
- Browser/provider execution
- Repo/file patch hub
- Completion scorecard
- Artifacts Center
- Install First Run Guide

## Decisão

O gate gera:

- `score_percent`
- `ready_to_install_real`
- blockers críticos
- warnings
- próxima ação

## Regras

Não instalar se:

- há blockers críticos;
- APK/EXE workflows falham;
- smoke CI falha;
- pairing não existe;
- project registry falha;
- artifacts center falha.

## Contrato de instalação

O contrato inclui:

1. baixar EXE;
2. baixar APK;
3. executar EXE;
4. abrir pairing;
5. instalar/abrir APK;
6. confirmar heartbeat;
7. abrir Modo Fácil;
8. rodar smoke local;
9. validar self-update/mobile update.

## Resultado esperado

Quando este gate estiver verde, o operador pode instalar para primeiro teste real controlado.
