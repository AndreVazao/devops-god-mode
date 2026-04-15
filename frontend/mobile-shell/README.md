# God Mode Mobile Shell

## Objetivo
Casca mobile-first leve para consumir o backend consolidado do DevOps God Mode.

## Capacidades atuais
- validar estado do backend
- enviar pedido para `/ops/mobile-cockpit`
- enviar pedido para `/ops/execution-pipeline`
- mostrar cards compactos
- mostrar JSON integral da resposta

## Estrutura
- `index.html` — interface principal
- `app.js` — lógica cliente
- `styles.css` — estilos
- `manifest.json` — base PWA

## Deploy estático
Pode ser servido como site estático em Vercel, GitHub Pages ou outro hosting simples.

## Artifact
O workflow `mobile-shell-artifact.yml` gera um artifact chamado `god-mode-mobile-shell`.
