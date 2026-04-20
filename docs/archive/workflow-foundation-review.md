# Workflow Foundation Review

## Objetivo
Mapear os workflows que hoje pertencem ao fluxo principal e os que continuam na repo sobretudo por cobertura histórica ou foundation placeholder.

## Core workflows atuais
### Keep as active
- `.github/workflows/windows-exe-real-build.yml`
- smoke workflows das fases já integradas no `main`

Estes workflows acompanham o estado real do backend, packaging desktop e camadas operacionais atuais.

## Legacy / foundation workflows
### Historical placeholder coverage
- `.github/workflows/android-mobile-build.yml`

Status atual:
- continua útil para gerar assets foundation e payloads mobile mínimos
- não representa o build Android final
- deve ser tratado como cobertura histórica/foundation

## Regra de leitura
Quando houver conflito entre um workflow foundation antigo e a arquitetura atual, considerar como fonte principal:
- `README.md`
- `docs/repo-consolidation-and-legacy-mapping.md`
- `docs/archive/legacy-foundations-index.md`
- rotas e services ligados em `backend/main.py`

## Próximo passo sugerido
Quando existir o pipeline Android real:
1. substituir `.github/workflows/android-mobile-build.yml`
2. arquivar ou remover o foundation placeholder
3. alinhar contracts Android reais com o novo pipeline
