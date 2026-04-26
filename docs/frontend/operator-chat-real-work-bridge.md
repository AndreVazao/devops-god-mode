# Operator Chat Real Work Bridge

## Objetivo

Ligar o chat principal do APK/mobile ao pipeline real de trabalho.

O operador não deve precisar de abrir cockpit técnico para dar ordens normais.

## Cockpits

- `/app/operator-chat-sync-cards`
- `/app/chat`

## API

- `GET /api/operator-chat-real-work/status`
- `GET /api/operator-chat-real-work/package`
- `GET /api/operator-chat-real-work/latest`
- `POST /api/operator-chat-real-work/submit`

## Fluxo

1. Operador escreve uma ordem no chat.
2. Backend cria/usa uma thread de conversa.
3. Mensagem é gravada na thread.
4. Ponte chama `/api/real-work/submit` por serviço interno.
5. Real Work Pipeline resolve o projeto pela ordem do operador.
6. Request Orchestrator recebe job.
7. Worker tenta avançar.
8. Chat recebe relatório curto com projeto, intent, job e estado.
9. Se bloquear, operador abre Aprovações.

## Política

- O projeto segue a ordem definida em `/app/operator-priority`.
- Dinheiro não é critério principal.
- O backend trabalha até concluir ou precisar de aprovação/input.

## Segurança

- Sem ações destrutivas diretas.
- Escrita real deve seguir branch/PR/checks.
- Se faltar aprovação, login manual ou input do operador, o fluxo bloqueia.

## Exemplo

```text
continua o God Mode até precisares do meu OK
```

Resultado esperado:

- aparece no chat;
- cria job durável;
- worker tenta processar;
- relatório fica visível no chat;
- se precisar de OK, aparece em `/app/mobile-approval-cockpit-v2`.
