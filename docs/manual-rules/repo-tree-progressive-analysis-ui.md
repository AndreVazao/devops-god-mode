# Repo Tree Progressive Analysis UI

## Decisão

O módulo **Repo Tree Explorer** deve expor a árvore real por camadas, enquanto a análise estrutural corre progressivamente no backend.

## Princípio

No telemóvel, o owner deve ver primeiro:
- a árvore real;
- nomes de pastas e ficheiros;
- navegação fluida;
- uma indicação visual de que a análise está em curso.

O processamento pesado continua no backend.

## Comportamento esperado

### Camada 1 — Estrutura imediata
O frontend mostra logo:
- raiz da repo;
- depth inicial padrão;
- expansão lazy dos nós;
- preview textual e visual.

### Camada 2 — Enriquecimento progressivo
Enquanto a árvore já está visível, o backend vai acrescentando:
- deteção de framework;
- tipo de repo;
- sinais de risco;
- hints arquiteturais;
- scoring estrutural;
- recomendações sobre o que fazer.

### Camada 3 — Assistência operacional
Depois do enriquecimento, o frontend deve conseguir mostrar:
- "o que fazer agora";
- alertas de risco;
- sugestões de limpeza/alinhamento;
- ações recomendadas com approval gate.

## UI

O preview deve incluir uma zona visual leve, adequada ao telemóvel, com:
- árvore principal visível;
- ícone/roda dentada indicando análise em curso;
- estado progressivo da análise;
- sem bloquear a navegação da árvore.

## Regra operacional

- a árvore nunca deve esperar pela análise completa para aparecer;
- a análise nunca deve bloquear o preview;
- o backend continua responsável por todo o processamento pesado;
- o frontend apenas mostra progresso, resultados e ações.

## Resultado esperado

O owner vê rapidamente a estrutura real no telemóvel e recebe, por camadas, inteligência útil sobre o que fazer a seguir, sem comprometer fluidez nem layout.
