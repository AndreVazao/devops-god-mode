# Home Button Self-Test

## Objetivo

A Phase 103 adiciona um teste operacional dos botões da Home.

Depois da Phase 102 ter criado aliases `POST` para painéis de leitura, esta fase cria um painel que verifica se as ações rápidas da Home têm rotas válidas e métodos compatíveis com APK/WebView.

## Endpoints

- `GET /api/home-button-selftest/status`
- `POST /api/home-button-selftest/status`
- `GET /api/home-button-selftest/report`
- `POST /api/home-button-selftest/report`
- `GET /api/home-button-selftest/package`
- `POST /api/home-button-selftest/package`

## Ligação à Home

A Home passa a expor:

- `Testar botões`
- `/api/home-button-selftest/report`

## O que valida

O self-test lê `quick_actions` da Home e confirma:

- se cada ação tem `endpoint` ou `route`;
- se as routes frontend começam por `/app/`;
- se endpoints existem no FastAPI;
- se painéis de leitura têm `POST` quando esperado;
- se ações stateful são marcadas como tal;
- se há falhas concretas para corrigir.

## Segurança

O teste não executa ações perigosas. Ele inspeciona rotas/métodos registados no FastAPI e classifica compatibilidade.

## Benefício

Antes de usar o APK, o operador pode carregar em `Testar botões` e saber se os botões críticos da Home estão prontos para o cliente mobile/WebView.
