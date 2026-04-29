# Spectacular Upgrade Advisor

## Objetivo

A Phase 130 adiciona um conselheiro sénior interno para responder à pergunta:

> O que falta para o God Mode passar de muito bom a espetacular?

O objetivo é evitar módulos soltos e priorizar as próximas fases com maior impacto real.

## Endpoints

- `GET/POST /api/spectacular-upgrade-advisor/status`
- `GET/POST /api/spectacular-upgrade-advisor/panel`
- `GET/POST /api/spectacular-upgrade-advisor/report`
- `GET/POST /api/spectacular-upgrade-advisor/phase-plan`
- `GET/POST /api/spectacular-upgrade-advisor/latest`
- `GET/POST /api/spectacular-upgrade-advisor/package`

## O que avalia

- percentagem real atual;
- prontidão em ambiente real;
- autonomia operacional;
- lacunas de execução real;
- lacunas de UX mobile;
- lacunas de reliability;
- próximos upgrades com impacto, esforço e risco.

## Top upgrades recomendados

O catálogo inicial inclui:

- Executor real de browser/providers;
- Executor real de ficheiros/repos com preview, patch, PR e rollback;
- Wizard APK ↔ PC de primeiro arranque;
- Motor de jobs retomáveis com checkpoints;
- Smoke test real pós-instalação APK/EXE;
- Gate de projeto concluído + arquivo/limpeza;
- Modo voz/condutor;
- Centro de downloads APK/EXE v2;
- Auto-diagnóstico e auto-correção;
- Guardião de qualidade da memória/conhecimento.

## Conselho sénior fixado

- Não adicionar mais dashboards soltos.
- Priorizar execução real controlada.
- Browser/provider executor e repo patch executor são os dois maiores saltos.
- Tudo novo deve aparecer na Home/Modo Fácil ou no Hub de Ações Críticas.

## Uso

Usar:

`/api/spectacular-upgrade-advisor/panel`

para ver a próxima fase mais importante.
