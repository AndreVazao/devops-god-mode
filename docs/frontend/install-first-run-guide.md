# Install First Run Guide

## Objetivo

Dar ao operador um caminho simples para primeira instalação e primeiro uso do God Mode, sem decorar comandos técnicos.

## API

- `GET /api/install-first-run/status`
- `GET /api/install-first-run/package`
- `GET /api/install-first-run/guide`

## Integração com Home

A Home passa a incluir:

- bloco `install_first_run` no dashboard;
- botão `Instalar/1º arranque`;
- ação rápida `Instalar/1º arranque`;
- modo condução com contagem de passos prontos.

## Passos guiados

1. Confirmar builds.
2. Instalar/abrir backend no PC.
3. Abrir APK.
4. Ligar APK ao PC.
5. Confirmar Home.
6. Ligar PC Autopilot.
7. Dar primeiro comando.
8. Responder aprovações.

## Regras seguras

- Não escrever dados sensíveis no chat.
- Usar Aprovações quando o God Mode pedir OK.
- Preservar `data/`, `memory/`, `.env` e `backend/.env`.
- Preferir `/app/home` como entrada principal.

## Valor

Em vez de explicar instalação em texto solto, o backend devolve um guia estruturado, com estado por passo e próxima ação visível na Home.