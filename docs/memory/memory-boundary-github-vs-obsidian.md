# Memory Boundary: GitHub vs Obsidian

## Decisão

O God Mode deve tratar as memórias persistentes como duas camadas diferentes, com responsabilidades diferentes.

## GitHub memory

A memória persistente em GitHub, incluindo o repo externo `AndreVazao/andreos-memory`, é para programação, engenharia e gestão técnica das repos e programas.

### Serve para

- contexto técnico de cada repo;
- arquitetura dos programas;
- decisões técnicas;
- backlog de implementação;
- histórico de commits, PRs, builds e releases;
- erros técnicos recorrentes;
- prompts técnicos para enviar a IAs quando for preciso mexer em código;
- ligação entre conversa de IA, repo, branch, PR e artifact;
- auditorias técnicas por projeto;
- estado real de desenvolvimento de cada programa.

### Não deve ser usada como

- diário operacional local;
- memória de vida diária;
- notas soltas sem relação direta com programação;
- armazenamento de credenciais, tokens, passwords ou chaves API;
- substituto do Obsidian local.

## Obsidian local memory

A memória local em Obsidian é para trabalho local, operação diária e evolução contínua do sistema no PC.

### Serve para

- contexto de uso local do André;
- notas de evolução;
- prioridades de trabalho;
- decisões operacionais;
- observações de testes reais no PC/telemóvel;
- aprendizagem local do God Mode;
- tarefas em progresso;
- contexto que ainda não deve ir para GitHub;
- histórico local de interação com ferramentas, PC, APK, providers e automações.

### Pode gerar GitHub memory quando

Uma nota local passa a ser relevante para programação, repo, bug, feature, arquitetura, build, release ou auditoria técnica. Nesse caso, o God Mode deve resumir a nota e propor sincronização para a memória GitHub.

## Regra de sincronização

O God Mode é o orquestrador das duas memórias.

### Fluxo correto

1. Obsidian recebe contexto local, operativo e evolutivo.
2. GitHub memory recebe contexto técnico estável necessário para programar e manter repos.
3. Quando o God Mode pede ajuda a uma IA externa para programar, deve enviar contexto técnico vindo da GitHub memory.
4. Quando uma IA externa devolve decisão/código/correção, o God Mode deve registar o resultado técnico na GitHub memory e o resultado operacional no Obsidian.
5. Nada sensível deve ser enviado para GitHub memory sem filtragem.

## Regra para chats de IA

Sempre que o God Mode abrir ou continuar uma conversa com ChatGPT ou outro provider para mexer num projeto, o prompt deve incluir:

- nome do projeto;
- repo alvo;
- branch/PR quando existir;
- caminho da memória GitHub relevante;
- resumo técnico atual;
- objetivo da tarefa;
- restrições de segurança;
- instrução para não inventar estado não confirmado.

## Regra anti-confusão

Se existir conflito entre Obsidian e GitHub memory:

- GitHub memory vence para estado técnico de programação;
- Obsidian vence para estado local, prioridades e observações do utilizador;
- o God Mode deve criar uma nota de reconciliação antes de agir.

## Objetivo final

Evitar perda de contexto e impedir que o God Mode misture memória de programação com memória operacional local.
