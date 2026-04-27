# Easy Mode Command Buttons

## Objetivo

Transformar o `Modo fácil` da Home em botões clicáveis para uso diário no APK.

Antes, o botão `Modo fácil` mostrava JSON do painel. Agora mostra um painel com:

- headline curta;
- projeto ativo;
- botões seguros;
- comandos rápidos acionáveis;
- regras de operador.

## Integração

Frontend:

- `/app/home`
- `/app/god-mode`
- `/app/god-mode-home`

APIs usadas:

- `GET /api/home-operator-ux/panel`
- `POST /api/daily-command-router/route`

## Comandos rápidos clicáveis

Cada comando rápido chama:

```json
{
  "command_id": "continue_active_project",
  "tenant_id": "owner-andre",
  "requested_project": "GOD_MODE"
}
```

Comandos principais:

- `continue_active_project`
- `fix_blockers`
- `prepare_install`
- `summarize_next`

## Botões seguros

O painel também suporta botões com:

- `payload.command_id` → chama Daily Command Router;
- `route` → navega para cockpit;
- `endpoint` → chama endpoint seguro.

## Valor

O operador pode usar o God Mode no telemóvel sem decorar comandos técnicos:

1. Abrir APK.
2. Entrar na Home.
3. Carregar em `Modo fácil`.
4. Carregar num botão de comando.
5. Backend encaminha para o fluxo certo.
6. Operador só decide quando aparecer pedido de OK.

## Segurança

- Não contorna aprovações.
- Não envia tokens, passwords, cookies ou API keys.
- Usa o projeto ativo quando não é escrito outro projeto.
- Mantém `Parar` e `Aprovar próximo` como ações explícitas.
