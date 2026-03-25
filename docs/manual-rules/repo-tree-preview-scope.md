# Repo Tree Preview Scope

## Decisão

O preview principal do módulo **Repo Tree Explorer** deve funcionar em modo **A — uma repo por vez**.

## Justificação

Mostrar múltiplas repos no mesmo preview tende a:
- aumentar ruído visual;
- dificultar leitura no telemóvel;
- misturar domínios diferentes;
- complicar zoom, fit e navegação.

## Regra de produto

### Preview
- uma repo por vez;
- foco visual claro;
- box isolada;
- zoom/fit sem confusão.

### Análise
O sistema pode e deve cruzar dados entre múltiplas repos **fora do preview principal**, usando:
- relações do registry;
- análise estrutural comparativa;
- diffs entre árvores;
- alertas de alinhamento de ecossistema.

## Resultado esperado

- preview limpo e utilizável;
- análise multi-repo separada e mais poderosa;
- melhor UX mobile-first;
- menos risco de confusão visual.
