# Professional Local AI Pack

## Objetivo

A Phase 100 junta duas melhorias maiores:

1. IA local opcional para PCs com Ollama/modelos pequenos.
2. Score profissional para medir se o God Mode está pronto para trabalhar como assistente operacional sério.

## IA local opcional

Endpoints:

- `GET /api/local-ai/status`
- `GET /api/local-ai/panel`
- `GET /api/local-ai/models`
- `POST /api/local-ai/classify`
- `POST /api/local-ai/generate-short`
- `GET /api/local-ai/package`

Uso recomendado:

- resumos curtos;
- classificação de ordens;
- explicação curta de erros;
- apoio offline/local.

Modelo default:

- `gemma2:2b`

O adapter tenta usar Ollama em:

- `http://127.0.0.1:11434`

Variáveis opcionais:

- `GODMODE_LOCAL_AI_URL`
- `GODMODE_LOCAL_AI_MODEL`

Se a IA local não estiver disponível, o God Mode continua a funcionar com fallback determinístico.

## Score profissional

Endpoints:

- `GET /api/professional-scorecard/status`
- `GET /api/professional-scorecard/scorecard`
- `GET /api/professional-scorecard/package`

Categorias medidas:

1. Home e UX móvel.
2. Instalação e arranque real.
3. Fluxo de execução.
4. Segurança operacional.
5. IA local opcional.

## Ligação à Home

A Home passa a expor:

- `Score profissional`
- `/api/professional-scorecard/scorecard`

E também:

- `IA local`
- `/api/local-ai/panel`

## Benefício prático

O PC antigo com modelo pequeno pode ser útil como ajudante local leve. Não substitui uma IA forte para código complexo, mas ajuda a classificar comandos, resumir estados e explicar erros sem depender sempre da cloud.

## Critério de aceitação

A PR deve confirmar:

- rotas da IA local;
- rotas do score profissional;
- Home com botões novos;
- fallback quando IA local está offline;
- documentação.
