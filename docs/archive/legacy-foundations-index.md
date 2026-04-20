# Legacy Foundations Index

## Objetivo
Separar explicitamente foundations históricas e placeholders do fluxo principal atual do God Mode.

## Status
Os itens abaixo continuam na repo como referência histórica, foundation intermédia ou placeholder técnico. Não representam o fluxo principal atual do `main`.

## Android foundations marcadas como legacy
- `docs/android-mobile-build-plan.md`
- `docs/android-real-runtime-shell-v2-plan.md`
- `docs/apk-real-build-and-pc-phone-bootstrap-plan.md`
- `.github/workflows/android-mobile-build.yml`

## Como interpretar
### Legacy foundation
- ajuda a perceber a evolução do produto
- pode continuar a dar cobertura mínima a assets e payloads
- não deve ser tomada como arquitetura final

### Core atual
Tomar como fonte principal de verdade:
- `README.md`
- `docs/repo-consolidation-and-legacy-mapping.md`
- `backend/main.py`
- PRs merged mais recentes das camadas operacionais

## Próximo passo sugerido
Quando a camada Android real existir, estes itens devem ser:
- movidos para arquivo definitivo
- ou removidos se já não tiverem utilidade operacional nem histórica relevante
