# Operator Priority + Real Work Command Pipeline

## Objetivo

O God Mode deve obedecer à ordem de projetos definida pelo operador.

A prioridade não é dinheiro. Dinheiro é consequência dos programas que o operador manda arranjar, montar, validar e publicar.

## Cockpits

- `/app/operator-priority`
- `/app/project-priority`
- `/app/real-work`
- `/app/work-command`

## APIs

### Operator Priority

- `GET /api/operator-priority/status`
- `GET /api/operator-priority/package`
- `GET /api/operator-priority/priorities`
- `GET /api/operator-priority/resolve`
- `POST /api/operator-priority/order`
- `POST /api/operator-priority/active`

### Real Work Command Pipeline

- `GET /api/real-work/status`
- `GET /api/real-work/package`
- `GET /api/real-work/latest`
- `POST /api/real-work/submit`

## Política

- `operator_order_first_money_is_consequence`
- `money_priority_enabled=false`
- projeto explícito no comando vence;
- se não houver projeto explícito, usa projeto ativo;
- se não houver ativo válido, usa o primeiro projeto enabled pela ordem do operador.

## Fluxo operacional

1. Operador define ordem dos projetos em `/app/operator-priority`.
2. Operador dá ordem em `/app/real-work` ou pelo chat.
3. Backend resolve projeto pela prioridade do operador.
4. Backend classifica intenção:
   - continuar projeto;
   - auditoria profunda;
   - correção/repair;
   - build/artifacts;
   - trabalho GitHub/PR;
   - execução geral.
5. Backend cria pacote executável.
6. Backend submete pedido ao Request Orchestrator.
7. Worker tenta continuar.
8. Se precisar de aprovação, login manual ou input do operador, bloqueia e vai para o cockpit de aprovação.

## Estado persistente

Ficheiros em `data/`:

- `data/operator_project_priorities.json`
- `data/real_work_command_pipeline.json`

## Segurança

- Não executa ações destrutivas diretamente.
- Branch/PR/checks devem ser o caminho padrão para escrita real.
- Pára quando precisa de aprovação ou dados externos manuais.
- Não mistura dados sensíveis com memória operacional normal.

## Exemplo de ordem

```text
continua o God Mode até precisares do meu OK
```

Resultado esperado:

- resolve `GOD_MODE` se for o projeto ativo;
- cria job no orquestrador;
- worker tenta avançar;
- relatório indica job/status/próximo passo.

## Próximo endurecimento

A próxima fase deve ligar o chat principal diretamente a `/api/real-work/submit`, para que uma mensagem normal no APK entre neste pipeline sem o operador abrir cockpit técnico.
