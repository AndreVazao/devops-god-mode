# Install Readiness Final Gate

## Objetivo

A fase cria o gate final de instalação para responder a uma pergunta simples:

> O God Mode está pronto para descarregar APK/EXE, instalar no PC/telemóvel e começar a receber ordens reais?

Este gate junta Home, Modo Fácil, Teste geral, memória AndreOS, ensaio real de operador, Artifacts Center e workflows canónicos de APK/EXE numa única validação de prontidão.

## Endpoints

- `GET /api/install-readiness-final/status`
- `GET /api/install-readiness-final/check`
- `POST /api/install-readiness-final/check`
- `GET /api/install-readiness-final/package`

## Ligação à Home

A Home passa a expor a ação rápida:

- `id: install_readiness_final`
- `label: Instalação final`
- `endpoint: /api/install-readiness-final/check`

Isto aparece nas ações principais geradas pelo backend, sem criar outro módulo solto.

## O que valida

1. Home responde.
2. Modo Fácil existe.
3. Botão `Teste geral` existe e o ensaio passa.
4. AndreOS Memory Audit passa.
5. Real Operator Rehearsal passa.
6. Artifacts Center aponta para APK e EXE.
7. Workflows canónicos APK/EXE existem.
8. APK esperado não parece placeholder.
9. EXE esperado não parece placeholder.
10. Project Tree Autorefresh vê os ficheiros novos.
11. Guarda de memória sensível está ativa.
12. Rotas principais existem.
13. `Teste geral` aparece no Modo Fácil.
14. Home consegue apresentar resultado em cartão visual.
15. O contrato de autonomia do backend está explícito: PC é o cérebro, APK é comando remoto, e o backend só deve parar quando termina, precisa do OK do operador, precisa de intervenção manual, ou encontra bloqueio seguro.
16. Home expõe a ação `Instalação final` ligada ao endpoint do gate.

## Resultado esperado

Quando tudo passa, o endpoint devolve:

- `status: ready_to_install`
- `ready_to_install: true`
- `score: 100`
- `operator_next` apontando para APK/EXE e Home.

Se algo falhar, devolve `failed_checks` com o primeiro ponto concreto a corrigir antes da instalação real.

## Uso prático

Fluxo recomendado para o operador:

1. Abrir `/app/home`.
2. Carregar em `Instalação final`.
3. Confirmar `ready_to_install=true`.
4. Descarregar:
   - `GodModeMobile-debug.apk`
   - `GodModeDesktop.exe`
5. Abrir primeiro o EXE no PC.
6. Abrir o APK no telemóvel e ligar ao backend do PC.
7. Dar a primeira ordem real.

## Segurança

- Não apaga dados.
- Não altera estado local crítico.
- Preserva `data/`, `memory/`, `.env` e `backend/.env`.
- Não transforma prioridade em dinheiro; a prioridade continua a vir do operador.
- Não substitui aprovações: se precisar de OK, o backend deve parar e pedir decisão.

## Critério de aceitação

A validação temporária `Install Readiness Final Gate Validation` deve passar e confirmar que o gate cobre endpoints, fluxos, artifacts, workflows, Home, Modo Fácil, Teste geral e Project Tree Autorefresh.
