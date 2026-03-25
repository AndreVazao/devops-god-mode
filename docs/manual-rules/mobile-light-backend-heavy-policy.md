# Mobile Light / Backend Heavy Policy

## Decisão

No DevOps God Mode, o telemóvel deve servir principalmente para:
- ver a árvore;
- navegar no preview;
- receber recomendações do sistema sobre o que fazer;
- aprovar ou rejeitar ações.

## Regra operacional

O trabalho pesado deve acontecer no backend, incluindo:
- leitura estrutural completa da repo;
- lazy loading;
- detecção de tamanho real e peso estrutural;
- scoring e inteligência arquitetural;
- geração de ficheiros de árvore;
- comparação, diffs e análise profunda.

## Resultado esperado

O frontend mobile-first permanece leve, rápido e legível, enquanto o backend assume o custo de processamento e análise.
