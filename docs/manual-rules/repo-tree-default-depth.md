# Repo Tree Default Depth

## Decisão

O módulo **Repo Tree Explorer** usa profundidade inicial padrão **2**.

## Interpretação

Quando uma repo é aberta no preview de árvore:
- a raiz é carregada;
- os dois primeiros níveis são preparados para visualização inicial;
- níveis adicionais são carregados sob pedido via lazy expansion.

## Justificação

A profundidade 2 oferece o melhor equilíbrio para uso mobile-first:
- mostra visão geral suficiente;
- evita poluição visual;
- reduz carga inicial;
- mantém zoom/fit utilizáveis.

## Regra futura

A profundidade inicial pode tornar-se configurável depois, mas o default oficial do sistema permanece 2 até nova decisão arquitetural.
