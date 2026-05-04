# Cockpit Runtime UX + Execution Logs

## Objetivo

A Phase 176 adiciona uma camada runtime para o cockpit mobile-first do God Mode.

O objetivo é dar ao telemóvel e ao PC uma forma simples de:

- fazer polling do estado do cockpit;
- ver módulos/botões reais vindos da Home/App Control Surface;
- registar cliques e resultados de botões;
- mostrar histórico operacional visível;
- manter o PC como cérebro e o telemóvel como cockpit principal.

## Endpoint principal

```txt
/api/cockpit-runtime-ux/package
```

Este package agrega:

- estado da camada runtime;
- package da Home/App Control Surface;
- histórico do Operator Action Journal;
- contrato de polling;
- regras mobile-first.

## Endpoints

- `GET/POST /api/cockpit-runtime-ux/status`
- `GET/POST /api/cockpit-runtime-ux/package`
- `GET/POST /api/cockpit-runtime-ux/history`
- `GET/POST /api/cockpit-runtime-ux/quick-history-cards`
- `POST /api/cockpit-runtime-ux/log-button-event`

## Reaproveitamento nativo

A Phase 176 não cria um logger paralelo.

Ela reutiliza:

- `HomeAppControlSurfaceService` para módulos/botões;
- `OperatorActionJournalService` para logs/histórico;
- `/app/home` como cockpit visual canónico.

## Segurança

- Não executa ações privilegiadas diretamente.
- Não contorna gates server-side.
- Não guarda segredos no histórico.
- Redige termos sensíveis em logs.
- Apenas regista metadados de clique/resultado.

## Modelo de operação

```txt
Telemóvel / PC cockpit
→ /api/cockpit-runtime-ux/package
→ renderiza módulos/botões/histórico
→ clique em botão
→ endpoint real do módulo executa/preview
→ /api/cockpit-runtime-ux/log-button-event regista evento
→ histórico volta no próximo polling
```

## Próxima evolução

- Ligar esta camada diretamente ao HTML de `/app/home` com polling automático visível.
- Criar cards de execução em tempo real.
- Mostrar histórico compacto na UI mobile.
- Adicionar filtros por risco/módulo/estado.
