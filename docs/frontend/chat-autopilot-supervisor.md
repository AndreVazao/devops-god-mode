# Chat Autopilot Supervisor

## Objetivo

Depois de uma ordem no chat, o backend não deve ficar limitado a um único tick curto.

O Chat Autopilot Supervisor dá várias oportunidades controladas ao worker para continuar o trabalho até uma destas condições:

- sem jobs para processar;
- bloqueado à espera do operador;
- falha a rever;
- orçamento de rondas atingido.

## API

- `GET /api/chat-autopilot/status`
- `GET /api/chat-autopilot/package`
- `GET /api/chat-autopilot/latest`
- `POST /api/chat-autopilot/run`

## Integração com o chat

O `/api/operator-chat-real-work/submit` passa a:

1. receber mensagem do operador;
2. gravar a mensagem na thread;
3. submeter trabalho ao Real Work Pipeline;
4. criar job no Request Orchestrator;
5. chamar o Chat Autopilot Supervisor;
6. correr várias rondas do worker;
7. devolver relatório ao chat.

## Política

- não contorna aprovações;
- não faz ações destrutivas por atalhos;
- respeita a ordem de projetos definida pelo operador;
- dinheiro não é critério de escolha;
- pára quando precisa de aprovação/input.

## Defaults

- `max_rounds_default=6`
- `max_jobs_per_round_default=4`

## Estados finais

- `idle_no_jobs_processed`
- `blocked_waiting_operator`
- `failed_needs_review`
- `budget_exhausted`

## O que o chat mostra

Depois de enviar uma ordem, o chat mostra:

- projeto resolvido;
- intent;
- job criado;
- número de rondas autopilot;
- motivo de paragem;
- total processado;
- se precisa do operador.

## Próximo passo

Depois desta fase, o próximo endurecimento deve ser um loop local real no PC/EXE que chame o autopilot periodicamente enquanto houver trabalho pendente, mesmo que o APK esteja fechado.
