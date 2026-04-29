# Home Critical Actions Button

## Objetivo

A Phase 126 liga o hub de ações críticas ao Modo Fácil.

O objetivo é evitar que módulos recentes fiquem escondidos e garantir que o operador tem botões grandes para chegar rapidamente ao estado real e aos próximos passos.

## Alterações

Atualizado:

- `backend/app/services/home_operator_ux_service.py`

## Botões adicionados ao Modo Fácil

### Ações críticas

Endpoint:

`/api/home-critical-actions/panel`

Mostra o hub com:

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

### Estado real %

Endpoint:

`/api/god-mode-completion/panel`

Mostra o scorecard real do God Mode até 100%.

## Campo novo

O painel do Modo Fácil passa a expor:

`critical_actions_endpoint`

com valor:

`/api/home-critical-actions/panel`

## Comando rápido novo

Adicionado quick command:

`show_critical_actions`

Mensagem:

`mostra o painel de ações críticas do God Mode e diz o próximo passo mais importante`

## Segurança

Esta fase não executa ações destrutivas.

Só adiciona atalhos visuais e endpoints ao painel do operador.
