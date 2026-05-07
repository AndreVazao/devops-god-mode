# First PC Autopilot Install/Run Cockpit + Today Ready Flow

## Objetivo

A Phase 207 junta numa única página o caminho rápido para instalar/abrir o God Mode no PC e iniciar o primeiro loop autónomo seguro.

## Endpoint principal

```txt
/api/first-pc-autopilot-ready/package
```

## Página visual

```txt
/app/first-pc-autopilot-ready
/app/today-ready
```

## Endpoints

- `/api/first-pc-autopilot-ready/status`
- `/api/first-pc-autopilot-ready/readiness`
- `/api/first-pc-autopilot-ready/operator-steps`
- `/api/first-pc-autopilot-ready/launch-contract`
- `/api/first-pc-autopilot-ready/start-today-autopilot`
- `/api/first-pc-autopilot-ready/package`

## Contrato de uso hoje

```txt
1. Abrir artifacts.
2. Obter Windows EXE mais recente.
3. Abrir GodModeDesktop.exe no PC.
4. Confirmar http://127.0.0.1:8000/app/home.
5. Abrir /app/first-pc-autopilot-ready.
6. Se necessário, usar /app/god-mode-vault para colar .env/chaves/URLs.
7. Abrir /app/mobile-permission-relay no telemóvel.
8. Carregar Start Autopilot.
9. O God Mode arranca o primeiro loop autónomo seguro.
```

## Readiness checks

A página verifica:

- global state;
- first PC install ready pack;
- runtime verification;
- artifacts center;
- local vault;
- mobile permission relay;
- IA operator bridge.

## Segurança

- Não faz login privado automático.
- Não guarda dados sensíveis fora do Vault local.
- Não aplica patches sem PR.
- Não faz merge/release/deploy sem aprovação do Oner.
- Só inicia o loop quando readiness estiver acima do limiar.

## Próximo passo

Depois desta fase, o God Mode já deve estar pronto para o primeiro uso real no PC.

Próxima camada natural:

```txt
Bridge task → PR planning generator → branch/PR proposal → checks → approval
```

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 206 deve ser apagado. Fica só:

- `.github/workflows/phase207-first-pc-autopilot-ready-flow-smoke.yml`

Além dos workflows globais/builds.
