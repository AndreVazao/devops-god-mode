# PC Link Helper

## Objetivo

A Phase 98 adiciona um painel simples para ligar o APK/WebView ao backend no PC.

A Home passa a expor:

- `Ligar ao PC`
- `/api/pc-link-helper/panel`

## Endpoints

- `GET /api/pc-link-helper/status`
- `GET /api/pc-link-helper/panel`
- `GET /api/pc-link-helper/package`

## O que mostra

O painel devolve:

- URL principal para abrir a Home;
- URLs candidatas com IPs locais;
- URLs `/health` para teste;
- passos curtos de ligação;
- troubleshooting básico;
- botões para Home, Health, Instalação final e Instalar agora.

## Fluxo móvel

1. Abrir o God Mode no PC.
2. Abrir `/api/pc-link-helper/panel` ou carregar em `Ligar ao PC` na Home.
3. No telemóvel, testar um URL candidato.
4. Confirmar que `/app/home` abre.
5. Correr `Instalação final` antes da primeira ordem longa.

## Segurança

- Não altera ficheiros locais.
- Não grava dados sensíveis.
- Apenas mostra URLs e passos de ligação local.
