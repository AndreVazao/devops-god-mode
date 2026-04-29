# Mobile Result Normalizer

## Objetivo

A Phase 104 cria um contrato visual estável para o APK/WebView mostrar resultados dos botões da Home.

Antes, cada endpoint podia devolver JSON com formatos diferentes. Agora o backend consegue transformar respostas em cartões mobile com campos consistentes.

## Endpoints

- `GET /api/mobile-result/status`
- `POST /api/mobile-result/status`
- `GET /api/mobile-result/contract`
- `POST /api/mobile-result/contract`
- `GET /api/mobile-result/catalog`
- `POST /api/mobile-result/catalog`
- `GET /api/mobile-result/home`
- `POST /api/mobile-result/home`
- `POST /api/mobile-result/normalize`
- `GET /api/mobile-result/package`
- `POST /api/mobile-result/package`

## Ligação à Home

A Home passa a expor:

- `Cartão mobile`
- `/api/mobile-result/home`

## Contrato do cartão

Cada resultado normalizado devolve:

- `title`
- `status`
- `color`
- `summary`
- `badges`
- `metrics`
- `primary_action`
- `secondary_actions`
- `show_json_available`

## Benefício

O APK pode mostrar resultados de forma clara sem interpretar todos os JSONs específicos de cada serviço.

## Pré-visualizações

`/api/mobile-result/catalog` devolve exemplos normalizados para:

- Home;
- Começar agora;
- Score profissional;
- Testar botões.

## Segurança

O normalizador não executa ações. Ele só transforma payloads em estrutura visual para o cliente mobile.
