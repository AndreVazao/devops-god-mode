# Memory Context Router

## Objetivo

A Phase 116 prepara a camada de memória extensível e contexto compacto para todos os projetos.

O God Mode passa a ter um ponto central para:

- preparar memória AndreOS/Obsidian por projeto;
- gerar contexto compacto para continuar trabalho sem se perder;
- manter português como idioma padrão;
- usar ChatGPT como IA principal de trabalho diário;
- preparar retoma quando houver limite, queda de ligação ou necessidade de trocar de IA;
- preparar projetos novos para entrarem logo na memória.

## Endpoints

- `GET/POST /api/memory-context-router/status`
- `GET/POST /api/memory-context-router/panel`
- `GET/POST /api/memory-context-router/provider-policy`
- `GET/POST /api/memory-context-router/obsidian-policy`
- `POST /api/memory-context-router/prepare-project`
- `POST /api/memory-context-router/prepare-latest-new-project`
- `POST /api/memory-context-router/prepare-priority-projects`
- `POST /api/memory-context-router/handoff-plan`
- `GET/POST /api/memory-context-router/latest`
- `GET/POST /api/memory-context-router/package`

## Política de memória

Cada projeto deve ter pasta própria em:

`memory/vault/AndreOS/02_PROJETOS/<PROJECT_ID>/`

Ficheiros esperados:

- `MEMORIA_MESTRE.md`
- `ARQUITETURA.md`
- `DECISOES.md`
- `BACKLOG.md`
- `ROADMAP.md`
- `ULTIMA_SESSAO.md`
- `HISTORICO.md`
- `ERROS.md`
- `PROMPTS.md`

## Política de IA principal

- IA principal: ChatGPT.
- Idioma padrão: português de Portugal.
- Utilização esperada: cerca de 80% do trabalho diário.
- Outras IAs são fallback para limite, indisponibilidade, contexto grande, investigação ou tarefa mais adequada.

## Retoma

Antes de pausar ou trocar de IA, o God Mode deve guardar:

- última sessão;
- próximos passos;
- histórico relevante;
- backlog atualizado.

Ao retomar, deve:

1. abrir contexto compacto do projeto;
2. confirmar última sessão;
3. confirmar próxima ação;
4. continuar na IA principal se possível;
5. usar fallback apenas quando necessário e permitido.

## Segurança

A memória não deve guardar dados sensíveis de acesso ou autenticação. O contexto enviado para outras IAs deve ser compacto, controlado e sem material privado desnecessário.

Também fica explícito que fallback não deve ser usado para contornar bloqueios de segurança. Só tarefas permitidas continuam noutro serviço.

## Projetos novos

Quando existe proposta nova em `New Project Start Intake`, o endpoint:

`POST /api/memory-context-router/prepare-latest-new-project`

cria/prepara a memória do projeto e gera o pacote compacto inicial.

## Projetos existentes

O endpoint:

`POST /api/memory-context-router/prepare-priority-projects`

prepara pacotes de contexto para os projetos prioritários já definidos pelo operador.

## Observação Home

A rota do painel está pronta em:

`/api/memory-context-router/panel`

O botão direto na Home deve ser adicionado num patch leve separado se a ferramenta bloquear alterações grandes ao ficheiro `god_mode_home_service.py`.
