# Self Update Manager

## Objetivo

A Phase 137 define como o God Mode se atualiza a si próprio sem exigir reinstalação manual sempre.

A regra é:

1. criar plano;
2. validar artifact/manifest;
3. criar backup;
4. preservar `data/`, `memory/`, `.env`, `backend/.env`;
5. pedir aprovação quando necessário;
6. aplicar update pelo executor apropriado;
7. rodar smoke test;
8. confirmar ou fazer rollback.

## Endpoints

- `GET/POST /api/self-update/status`
- `GET/POST /api/self-update/panel`
- `GET/POST /api/self-update/policy`
- `POST /api/self-update/plan`
- `POST /api/self-update/backup`
- `POST /api/self-update/approve`
- `POST /api/self-update/record-run`
- `POST /api/self-update/rollback`
- `GET/POST /api/self-update/latest`
- `GET/POST /api/self-update/package`

## Frases

Aprovar update:

`UPDATE GOD MODE`

Rollback:

`ROLLBACK GOD MODE`

## Caminhos preservados

- `data/`
- `memory/`
- `.env`
- `backend/.env`

## APK vs EXE

### EXE / PC

Atualizações do EXE/launcher/backend devem:

- criar backup;
- substituir binários/bundle;
- reiniciar backend;
- correr smoke test;
- rollback se falhar.

### APK

Se mudar só backend/frontend servido pelo PC, normalmente não é preciso reinstalar APK.

Se mudar a WebView shell, permissões ou código Android, é preciso instalar novo APK.

## Segurança

Esta fase não troca ficheiros sozinha.

Ela cria o contrato seguro para o executor de update aplicar depois com backup, aprovação e rollback.
