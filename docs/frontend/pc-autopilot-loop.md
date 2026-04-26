# PC Autopilot Loop

## Objetivo

Permitir que o backend continue a processar trabalho pendente no PC, mesmo que o APK esteja fechado ou desconectado.

Esta fase não substitui aprovações. O loop só chama o stack existente de worker/autopilot e pára quando encontra bloqueios, falhas ou falta de trabalho.

## Cockpits

- `/app/pc-autopilot`
- `/app/autopilot-loop`

## API

- `GET /api/pc-autopilot/status`
- `GET /api/pc-autopilot/package`
- `GET /api/pc-autopilot/latest`
- `GET /api/pc-autopilot/dashboard`
- `POST /api/pc-autopilot/configure`
- `POST /api/pc-autopilot/cycle`
- `POST /api/pc-autopilot/start`
- `POST /api/pc-autopilot/stop`

## Segurança

- desligado por defeito;
- não contorna aprovações;
- não executa atalhos destrutivos;
- funciona mesmo com APK desconectado;
- pára/expõe estado quando precisa do operador.

## Configuração padrão

- `enabled=false`
- `interval_seconds=30`
- `max_rounds_per_cycle=3`
- `max_jobs_per_round=4`
- `run_when_apk_disconnected=true`
- `approval_bypass=false`

## Fluxo

1. Operador dá ordem no chat.
2. Real Work Pipeline cria job.
3. Chat Autopilot processa imediatamente algumas rondas.
4. PC Autopilot Loop pode continuar a chamar ciclos no PC.
5. Se ficar bloqueado, o operador vê em Aprovações.
6. Se não houver jobs, o loop fica idle.

## Nota operacional

O loop usa thread daemon dentro do processo backend quando iniciado via API.

Para ficar permanente depois de reiniciar o PC/backend, uma fase futura deve adicionar startup hook/launcher Windows que reative o loop de forma controlada conforme settings persistidas.
