# Home Operator UX

## Objetivo

Simplificar a Home para uso diário no telemóvel.

A Phase 86 adiciona uma camada de operador por cima dos diagnósticos existentes. Em vez de expor só módulos técnicos, a Home passa a ter um painel simples com:

- headline curta;
- ação principal;
- botões seguros;
- comandos rápidos;
- regras de uso em contexto móvel;
- estado do PC Autopilot, saúde e prioridade.

## API

- `GET /api/home-operator-ux/status`
- `GET /api/home-operator-ux/package`
- `GET /api/home-operator-ux/panel`

## Integração com Home

A Home passa a incluir:

- botão `Modo fácil`;
- chamada para `/api/home-operator-ux/panel`;
- painel JSON com ação principal e frases rápidas.

## Regras

- A prioridade vem do operador.
- `money_priority_enabled=false` deve continuar respeitado.
- Não contorna aprovações.
- Não inicia ações destrutivas.
- Não pede dados sensíveis no chat.

## Comandos rápidos

Exemplos gerados pelo painel:

- continuar projeto ativo;
- corrigir blockers;
- preparar instalação;
- resumo curto.

## Uso diário

Fluxo esperado:

1. Abrir APK.
2. Cair em `/app/home`.
3. Carregar em `Modo fácil` quando quiser orientação curta.
4. Carregar na ação principal ou copiar um comando rápido.
5. Deixar o backend trabalhar até bloquear ou pedir OK.
