# God Mode Home Cockpit

## Cockpit

- `/app/home`
- `/app/god-mode`
- `/app/god-mode-home`

## API

- `GET /api/god-mode-home/status`
- `GET /api/god-mode-home/package`
- `GET /api/god-mode-home/dashboard`
- `GET /api/god-mode-home/driving-mode`
- `POST /api/god-mode-home/continue`
- `POST /api/god-mode-home/chat`
- `POST /api/god-mode-home/start-autopilot`
- `POST /api/god-mode-home/stop-autopilot`
- `POST /api/god-mode-home/approve-next`

## Objetivo

Criar o cockpit principal definitivo do God Mode.

A Home não substitui os módulos especializados. Ela é a porta de entrada simples para o operador usar no APK/telemóvel.

## Política

- Uma Home controla vários cockpits por baixo.
- A ordem de projetos vem do operador.
- `money_priority_enabled=false`.
- Dinheiro é consequência de arranjar, montar, validar e publicar projetos; não é o critério principal de routing.
- O backend trabalha até concluir ou precisar de aprovação/input.

## O que aparece na Home

- Chat rápido.
- Semáforo geral.
- Projeto ativo.
- Estado do PC Autopilot.
- Aprovações pendentes.
- Próxima tarefa.
- Último resultado.
- Botão Continuar.
- Botão Parar.
- Botão Aprovar próximo.
- Botão Ver problemas.

## Integrações por baixo

- Operator Priority.
- Real Work Command Pipeline.
- Operator Chat Real Work Bridge.
- Chat Autopilot Supervisor.
- PC Autopilot Loop.
- Mobile Approval Cockpit V2.
- AndreOS Memory Core.

## Fluxo principal

1. Operador abre `/app/home` no APK.
2. Vê semáforo e próxima tarefa.
3. Escreve ordem no chat rápido ou carrega em Continuar.
4. Backend resolve projeto pela prioridade do operador.
5. Backend cria job real.
6. Autopilot tenta trabalhar.
7. Se bloquear, Home mostra Aprovações/Problemas.
8. PC Autopilot pode continuar no PC com APK fechado.

## Segurança

- Não contorna aprovações.
- Não executa atalhos destrutivos.
- Não muda prioridade para dinheiro automaticamente.
- Não mistura dados sensíveis com memória operacional normal.

## Modo condução

`GET /api/god-mode-home/driving-mode` devolve frases curtas e botões seguros para contexto móvel.

## Próximo endurecimento

Depois desta fase, o próximo passo é fazer o APK abrir `/app/home` como landing principal depois do pairing, em vez de mandar o operador para cockpits técnicos.