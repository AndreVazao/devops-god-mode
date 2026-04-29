# Real Install Smoke Test

## Objetivo

A Phase 135 cria smoke tests de instalação real em dois níveis.

## Nível A — CI seguro

Endpoint:

`GET/POST /api/real-install-smoke-test/ci-safe`

Este teste pode correr em workflow/CI sem instalar nada no PC do operador.

Valida:

- serviços críticos importam e respondem;
- Home/Modo Fácil existe;
- Ações críticas existe;
- Estado real % existe;
- Pairing APK ↔ PC existe;
- Jobs retomáveis existem;
- Browser/provider execution hub existe;
- Repo/file patch hub existe;
- workflows APK/EXE existem e não parecem placeholders;
- contrato local de instalação está definido.

## Nível B — Contrato local

Endpoint:

`GET/POST /api/real-install-smoke-test/local-contract`

Este contrato só é usado quando o operador decidir instalar EXE/APK reais.

Passos previstos:

1. Abrir `GodModeDesktop.exe`.
2. Criar sessão de pairing.
3. Confirmar APK.
4. Enviar heartbeat.
5. Abrir Home/Modo Fácil.
6. Abrir Ações críticas.
7. Criar job teste.
8. Criar checkpoint teste.
9. Completar job teste.

## Endpoints

- `GET/POST /api/real-install-smoke-test/status`
- `GET/POST /api/real-install-smoke-test/panel`
- `GET/POST /api/real-install-smoke-test/ci-safe`
- `GET/POST /api/real-install-smoke-test/local-contract`
- `GET/POST /api/real-install-smoke-test/latest`
- `GET/POST /api/real-install-smoke-test/package`

## Segurança

O CI safe:

- não instala nada;
- não mexe no PC do operador;
- não mexe em projetos reais;
- não pede secrets;
- só valida contratos/serviços/workflows.

O contrato local:

- não deve alterar projetos reais;
- deve criar apenas job/checkpoint de teste;
- se falhar, regista erro e mostra próxima ação;
- não reinstala automaticamente sem OK.

## Resultado esperado

Antes de instalar no PC/telemóvel, o operador consegue saber se a build está pronta para um teste real controlado.
