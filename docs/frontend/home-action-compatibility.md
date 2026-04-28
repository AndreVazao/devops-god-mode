# Home Action Compatibility

## Objetivo

A Phase 102 melhora a compatibilidade dos botões da Home.

O frontend da Home tem ações genéricas que podem chamar endpoints por `POST`. Muitos painéis eram apenas `GET`, o que podia causar erro quando o operador carregava em botões como `IA local`, `Score profissional`, `Ligar ao PC`, `APK/EXE`, `Saúde`, `Modo fácil` e outros.

Esta fase adiciona aliases `POST` seguros para endpoints de leitura/painel.

## Rotas cobertas

### IA local

- `POST /api/local-ai/status`
- `POST /api/local-ai/panel`
- `POST /api/local-ai/models`
- `POST /api/local-ai/package`

### Score profissional

- `POST /api/professional-scorecard/status`
- `POST /api/professional-scorecard/scorecard`
- `POST /api/professional-scorecard/package`

### Operador Pro

- `POST /api/pro-operator/status`
- `POST /api/pro-operator/panel`
- `POST /api/pro-operator/package`

### Ligar ao PC

- `POST /api/pc-link-helper/status`
- `POST /api/pc-link-helper/panel`
- `POST /api/pc-link-helper/package`

### APK/EXE

- `POST /api/artifacts-center/status`
- `POST /api/artifacts-center/dashboard`
- `POST /api/artifacts-center/package`

### Saúde

- `POST /api/home-system-health/status`
- `POST /api/home-system-health/snapshot`
- `POST /api/home-system-health/package`

### Guia de instalação

- `POST /api/install-first-run/status`
- `POST /api/install-first-run/guide`
- `POST /api/install-first-run/package`

### Ready to Use

- `POST /api/ready-to-use/status`
- `POST /api/ready-to-use/checklist`
- `POST /api/ready-to-use/package`

### Modo Fácil

- `POST /api/home-operator-ux/status`
- `POST /api/home-operator-ux/panel`
- `POST /api/home-operator-ux/package`

## Segurança

Estes aliases apenas devolvem painéis/status/dashboards já existentes. Não criam ações destrutivas novas.

## Benefício

A Home fica mais tolerante ao método HTTP usado pelo frontend, WebView ou APK. O operador pode carregar nos botões sem se preocupar se o endpoint original era `GET` ou `POST`.
