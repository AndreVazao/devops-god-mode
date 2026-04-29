# Ollama Model Benchmark

## Objetivo

A Phase 128 testa modelos Ollama instalados no PC e recomenda quais devem ficar.

Isto resolve dois cenários:

- PC antigo/fraco: manter poucos modelos leves que respondem sem bloquear.
- PC novo/forte: testar todos e deixar ficar os melhores que funcionam bem.

## Endpoints

- `GET/POST /api/ollama-model-benchmark/status`
- `GET/POST /api/ollama-model-benchmark/panel`
- `GET/POST /api/ollama-model-benchmark/policy`
- `GET/POST /api/ollama-model-benchmark/models`
- `POST /api/ollama-model-benchmark/run`
- `POST /api/ollama-model-benchmark/cleanup-plan`
- `GET/POST /api/ollama-model-benchmark/latest`
- `GET/POST /api/ollama-model-benchmark/package`

## Como testa

O serviço usa:

`ollama run <modelo> <prompt curto>`

com timeout configurável.

Por defeito:

- PC fraco/auto: 45 segundos por modelo.
- PC forte/novo: 90 segundos por modelo.

## Scoring

Cada modelo recebe score de 0 a 100 com base em:

- se respondeu;
- tempo de resposta;
- tamanho mínimo da resposta;
- erros no stderr;
- relevância básica ao prompt.

## Classificações

- `keep_best`: modelo bom e rápido.
- `keep_usable`: modelo utilizável.
- `remove_or_skip_failed`: falhou.
- `remove_or_skip_too_slow`: demasiado lento.
- `remove_or_skip_error`: erro ao executar.
- `review_low_score`: precisa revisão.

## Recomendação

Em PC fraco:

- mantém no máximo 2 modelos bons.

Em PC forte:

- mantém até 5 modelos bons.

O resto vai para:

- remover se falhou/foi lento;
- rever se ficou no meio.

## Ligação à limpeza

Depois do benchmark, o endpoint:

`POST /api/ollama-model-benchmark/cleanup-plan`

cria automaticamente um plano para `/api/local-cleanup/plan`, usando:

- `keep_ollama_models`
- `broken_ollama_models`

A remoção real continua protegida pela Phase 127 e exige frase:

`OPTIMIZE LOCAL PC`

## Segurança

- não remove modelos sozinho;
- não usa wildcards;
- só recomenda remoção por nome exato;
- timeout impede modelos lentos de bloquear indefinidamente;
- PC fraco mantém poucos modelos para não ficar lento.
