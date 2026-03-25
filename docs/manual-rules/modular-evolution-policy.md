# Modular Evolution Policy

## Princípio

O DevOps God Mode deve evoluir de forma **modular**, sem partir o que já está funcional e sem comprometer a operação principal do sistema.

## Regras-base

### 1. Núcleo estável
O núcleo operacional do sistema deve permanecer pequeno, previsível e protegido.

Inclui especialmente:
- configuração;
- autenticação de conectores;
- health/status;
- scan GitHub;
- registry;
- persistência Supabase;
- approval gates.

### 2. Novas capacidades entram como módulos
Qualquer funcionalidade nova deve entrar como módulo desacoplado.

Exemplos:
- `health_service`
- `governance_service`
- `workflow_template_service`
- `repo_tree_explorer_service`
- `pwa_mobile_shell`
- `repair_planner_service`
- `approval_popup_service`

### 3. Sem refactors destrutivos desnecessários
Não se substitui algo que já está estável apenas por preferência arquitetural.

Regra:
- melhorar por camadas;
- expandir por interfaces;
- evitar reescrita total quando uma extensão modular resolve.

### 4. Compatibilidade futura obrigatória
Cada módulo novo deve ser desenhado para poder:
- crescer depois;
- ser melhorado sem quebrar contratos já usados;
- ser desligado ou trocado com impacto mínimo.

### 5. Preview antes de escrita
Sempre que possível:
- primeiro preview;
- depois confirmação;
- só depois persistência.

### 6. UI sem comprometer o layout principal
Ferramentas utilitárias de frontend, como preview de árvore, zoom, fit e exportação, devem viver em componentes independentes e não podem partir a navegação principal.

## Aplicação imediata

As próximas evoluções do God Mode devem respeitar esta política, incluindo:
- integração de capacidades úteis vindas do `ai-devops-control-center`;
- criação do `Repo Tree Explorer`;
- PWA mobile shell;
- summaries de health/governance;
- workflow planning;
- futuras capacidades de repair.

## Repo Tree Explorer — política específica

O módulo de árvore da repo deve entrar como funcionalidade separada, contendo:
- geração de árvore completa;
- preview em box independente;
- exportação para ficheiro;
- `PROJECT_TREE.txt`;
- plain text / markdown no futuro;
- copiar árvore;
- zoom in / zoom out;
- botão `fit`;
- sem quebrar o layout principal.

## Resultado esperado

O God Mode deve crescer como plataforma modular, com evolução contínua, mas mantendo sempre:
- estabilidade do núcleo;
- continuidade operacional;
- possibilidade de expansão futura;
- zero dependência de reescritas destrutivas.
