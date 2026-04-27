# Home General Test Button

## Objetivo

Adicionar um botão `Teste geral` ao Modo Fácil para o operador validar rapidamente se o God Mode está operacional antes de mandar trabalho sério.

## Fluxo

1. Abrir `/app/home`.
2. Carregar em `Modo fácil`.
3. Carregar em `Teste geral`.
4. A Home chama `POST /api/real-operator-rehearsal/run`.
5. O resultado aparece em cartão no próprio Modo Fácil.

## API usada

- `GET /api/home-operator-ux/panel`
- `POST /api/real-operator-rehearsal/run`

## Payload padrão

```json
{
  "tenant_id": "owner-andre",
  "requested_project": "GOD_MODE"
}
```

Quando o campo de projeto da Home estiver preenchido, esse projeto é usado como `requested_project`.

## Validação visual

O cartão de resultado mostra:

- modo/status;
- projeto;
- job quando existir;
- stop reason quando existir;
- score;
- artifacts;
- botão `Ver JSON`.

## Critério de aceitação

A validação da fase deve confirmar que o botão existe no Modo Fácil, chama `/api/real-operator-rehearsal/run`, devolve score pronto e mostra o resultado em cartão.

## Segurança

- Não contorna aprovações.
- Não apaga dados.
- Não escreve secrets.
- Não faz login externo.
- Só corre o ensaio interno validado pela Phase 91.
