# Local Performance Autopilot

## Objetivo

A Phase 129 junta num painel único a otimização local do PC.

O objetivo é manter o PC rápido sem partir Windows, ferramentas, memória ou modelos úteis.

## Endpoints

- `GET/POST /api/local-performance-autopilot/status`
- `GET/POST /api/local-performance-autopilot/panel`
- `GET/POST /api/local-performance-autopilot/policy`
- `POST /api/local-performance-autopilot/plan`
- `POST /api/local-performance-autopilot/run-safe`
- `GET/POST /api/local-performance-autopilot/latest`
- `GET/POST /api/local-performance-autopilot/package`

## O que agrega

- Local Tool Capability Scan
- Autonomous install decision
- Ollama Model Benchmark
- Local Cleanup Optimizer

## Modo seguro

O endpoint principal seguro é:

`POST /api/local-performance-autopilot/run-safe`

Ele pode:

1. fazer scan de ferramentas;
2. decidir instalação/configuração;
3. testar modelos Ollama se pedido;
4. criar plano de limpeza;
5. recomendar estratégia PC fraco/novo;
6. indicar próxima ação.

Não remove modelos nem altera Windows diretamente.

## PC fraco

Recomenda:

- manter só 1-2 modelos Ollama bons;
- usar GitHub Actions para builds pesados;
- instalar apenas ferramentas leves essenciais;
- evitar ferramentas que bloqueiam o PC.

## PC novo/forte

Recomenda:

- testar todos os modelos Ollama;
- manter até 5 modelos úteis;
- preparar toolchain local mais completa;
- usar mais execução local quando fizer sentido.

## Segurança

A limpeza real continua no endpoint:

`/api/local-cleanup/apply-safe`

com frase:

`OPTIMIZE LOCAL PC`

Alterações Windows ficam como revisão e não são aplicadas automaticamente.
