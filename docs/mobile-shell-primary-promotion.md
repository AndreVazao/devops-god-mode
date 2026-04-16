# Mobile Shell Primary Promotion

## Objetivo
Promover a linha híbrida para a shell principal do God Mode.

## Substituições previstas
- `frontend/mobile-shell/index.html` passa a seguir a estrutura híbrida
- `frontend/mobile-shell/app.js` passa a seguir a lógica híbrida
- `frontend/mobile-shell/styles.css` passa a seguir o visual híbrido

## Fonte de referência
- `frontend/mobile-shell/index.hybrid.html`
- `frontend/mobile-shell/app.hybrid.js`
- `frontend/mobile-shell/styles.hybrid.css`

## Estratégia
Como o conector falhou nos updates diretos, esta fase consolida a promoção numa branch curta e documentada.

## Checklist
- manter smoke verde
- changed files limpo
- rebase merge
- só depois considerar remover os ficheiros `*.hybrid.*`
