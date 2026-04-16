# Promote Handsfree Primary — Plan

## Branch
- `feature/promote-handsfree-primary`

## Objetivo
Promover a linha `handsfree` para a shell principal do God Mode.

## Substituições pretendidas
- `frontend/mobile-shell/index.html` deve passar a refletir a UX handsfree
- `frontend/mobile-shell/app.js` deve passar a usar presets de backend e resumo rápido
- `frontend/mobile-shell/styles.css` deve passar a suportar o layout handsfree

## Fonte de referência
- `frontend/mobile-shell/index.handsfree.html`
- `frontend/mobile-shell/app.handsfree.js`
- `frontend/mobile-shell/styles.handsfree.css`
- `frontend/mobile-shell/backend-presets.example.json`

## Notas operacionais
O conector permitiu criar protótipos e workflows, mas os updates diretos dos ficheiros principais podem ter de ser feitos manualmente no GitHub web se o conector voltar a falhar.

## Resultado esperado
- shell principal pronta para Render, PC local, túnel e manual
- driving mode mais limpo
- assisted mode mais completo
- workflow unificado de validação disponível
