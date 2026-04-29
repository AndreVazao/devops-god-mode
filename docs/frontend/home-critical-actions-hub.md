# Home Critical Actions Hub

## Objetivo

A Phase 125 cria um hub único para impedir que os módulos críticos recentes fiquem escondidos no backend.

Este hub é pensado para Home/Modo Fácil/APK, com botões grandes e próximos passos claros.

## Endpoints

- `GET/POST /api/home-critical-actions/status`
- `GET/POST /api/home-critical-actions/panel`
- `GET/POST /api/home-critical-actions/snapshot`
- `GET/POST /api/home-critical-actions/latest`
- `GET/POST /api/home-critical-actions/package`

## Módulos agregados

- Estado real %
- Setup automático PC
- Entrega automática
- Memória / providers
- Projeto novo
- Fila aprovada
- Ferramentas locais
- Backup portátil
- Restore aprovado
- Limpar chats IA
- Resolver provider

## Cartões principais

Os cartões principais são marcados como `critical`:

- Estado real %
- Setup automático PC
- Entrega automática
- Memória / providers
- Projeto novo
- Fila aprovada

## Cartões secundários

- Ferramentas locais
- Backup portátil
- Restore aprovado
- Limpar chats IA
- Resolver provider

## Regras mobile

- botões grandes;
- um ecrã principal;
- mostrar percentagem real;
- priorizar setup, memória, entrega e fila;
- parar só em login, aprovação, bloqueio ou conclusão.

## Próximo passo recomendado

Ligar `/api/home-critical-actions/panel` diretamente à Home/Modo Fácil como botão:

`Ações críticas`

endpoint:

`/api/home-critical-actions/panel`
