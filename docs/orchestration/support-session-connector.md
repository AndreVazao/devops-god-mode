# Temporary Assisted Support Session Connector

## Objetivo

A Phase 211 cria um conector temporário de suporte/teste para o God Mode instalado no PC.

Modo aceite: **Nível 3 — Assisted Action Mode**.

O assistente pode analisar diagnóstico redigido e propor ações, mas qualquer ação sensível precisa de aprovação explícita do Oner no telemóvel via Mobile Permission Relay.

## Endpoints

```txt
/api/support-session/status
/api/support-session/policy
/api/support-session/create
/api/support-session/diagnostics
/api/support-session/propose-action
/api/support-session/record-action-result
/api/support-session/revoke
/api/support-session/dashboard
/api/support-session/package
```

## Página visual

```txt
/app/support-session
/app/temporary-support
```

## Propriedades obrigatórias

- Sessão temporária com TTL.
- Código one-time de aprovação.
- Read-only por defeito.
- Diagnóstico redigido.
- Sem segredos raw.
- Sem Vault raw values.
- Sem valores brutos de ambiente.
- Ações assistidas com Mobile Permission Relay.
- Audit log local.
- Revogação manual.

## Modos

```txt
diagnostic
read_only
assisted_action
```

## Ações seguras iniciais

- `read_diagnostics`
- `export_redacted_bundle`
- `create_github_issue_plan`
- `prepare_pr_plan`
- `request_screenshot`
- `run_safe_check_request`

## Ações bloqueadas por defeito

- `write_file`
- `apply_patch`
- `run_command`
- `change_vault`
- `deploy`
- `release`
- `merge`
- `browser_automation`
- `read_raw_secret`

## Fluxo

```txt
Oner abre /app/support-session
→ cria sessão temporária
→ God Mode gera diagnóstico redigido
→ Oner partilha diagnóstico/ID comigo
→ eu proponho ação
→ God Mode cria popup mobile
→ Oner aprova ou recusa
→ God Mode regista resultado/audit log
→ Oner pode revogar sessão
```

## Limites reais

Este conector não dá acesso remoto livre/permanente ao PC.

Ele cria uma camada segura e auditável para debugging assistido. O transporte remoto pode ser LAN, Tailscale, Cloudflare Tunnel, Ngrok ou diagnóstico exportado, mas o acesso fica sempre gated.

## Segurança

- Não abrir portas do router automaticamente.
- Não publicar painel admin público permanente.
- Não expor segredos.
- Não executar comandos sem gate.
- Não alterar Vault sem gate.
- Não fazer merge/release/deploy sem aprovação.

## Estado final esperado

Após esta fase, quando o God Mode estiver instalado no PC, o Oner pode criar uma sessão temporária de suporte para debug real sem expor segredos nem dar acesso permanente.
