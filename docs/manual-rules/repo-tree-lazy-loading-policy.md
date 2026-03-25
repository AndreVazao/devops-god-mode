# Repo Tree Lazy Loading Policy

## Decisão

O módulo **Repo Tree Explorer** adota **lazy loading sempre** como estratégia principal de leitura e expansão da árvore.

## Justificação

Usar lazy loading apenas para repos grandes e full scan para repos pequenas criaria:
- comportamento inconsistente;
- lógica mais difícil de manter;
- UX imprevisível;
- maior risco de bugs no frontend e no backend.

## Regra

O motor deve:
- carregar a raiz primeiro;
- expandir nós por pedido;
- permitir enriquecimento progressivo;
- manter o mesmo contrato para repos pequenas e grandes.

## Benefícios

- arquitetura determinística;
- melhor escalabilidade;
- compatibilidade futura com PC/local;
- base correta para diffs, cache, scoring e IA estrutural.

## Resultado esperado

- repos pequenas parecem instantâneas;
- repos grandes continuam utilizáveis;
- o frontend mantém zoom, fit e navegação sem confusão;
- o backend fica pronto para providers GitHub, local, server e container.
