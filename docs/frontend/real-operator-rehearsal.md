# Real Operator Rehearsal

## Objetivo

Ensaiar o uso real do God Mode antes de instalar no PC/APK.

A fase valida a cadeia interna:

1. Home responde.
2. Daily Command Router recebe uma ordem.
3. Chat bridge transforma a ordem em trabalho real.
4. Real Work Pipeline cria job.
5. Autopilot corre até bloquear, terminar ou ficar idle.
6. Feedback volta com job, projeto, stop reason e próxima ação.
7. Aprovações são consultáveis.
8. AndreOS Memory passa auditoria.
9. Artifacts Center aponta para APK/EXE.
10. Workflows de build não parecem placeholders.

## API

- `GET /api/real-operator-rehearsal/status`
- `GET /api/real-operator-rehearsal/package`
- `POST /api/real-operator-rehearsal/run`

## Payload

```json
{
  "tenant_id": "owner-andre",
  "requested_project": "GOD_MODE"
}
```

## Limite honesto

Este ensaio não abre o EXE no teu PC físico nem instala o APK no telemóvel. Isso só dá para testar no teu ambiente real.

Mas valida a cadeia backend que o APK vai chamar:

`Home → Modo Fácil → Daily Command Router → Chat Bridge → Real Work Pipeline → Autopilot → Feedback → Aprovações/Memória/Artifacts`.

## Artifacts

A validação temporária também verifica que:

- o workflow de APK existe;
- o workflow de EXE existe;
- ambos usam `upload-artifact`;
- não parecem placeholders/dummy;
- quando o CI produz ficheiros de build, verifica tamanho e extensão esperada.

## Segurança

- Não grava secrets.
- Não mexe em `.env`.
- Não apaga `data/` nem `memory/`.
- Não contorna aprovações.
- Não faz automação externa de login/provider.
