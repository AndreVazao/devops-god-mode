# Home Command Wizard

## Objetivo

A Phase 97 adiciona um assistente simples para escolher a próxima ordem a partir da Home.

A Home passa a expor:

- `Próxima ordem`
- `/api/home-command-wizard/panel`

## Endpoints

- `GET /api/home-command-wizard/status`
- `GET /api/home-command-wizard/panel`
- `POST /api/home-command-wizard/panel`
- `POST /api/home-command-wizard/run`
- `GET /api/home-command-wizard/package`

## Comandos principais

O painel sugere comandos como:

- `continue_active_project`
- `fix_blockers`
- `summarize_next`
- `show_artifacts`
- `install_readiness_final` quando o gate final precisa correr.

## Uso móvel

1. Abrir `/app/home`.
2. Carregar em `Próxima ordem`.
3. Escolher um botão claro.
4. O backend encaminha pelo Daily Command Router ou pelo gate final.
5. O resultado volta em formato de cartão/JSON.

## Critério de aceitação

A validação confirma:

- rotas do wizard;
- Home com ação `Próxima ordem`;
- painel com comandos;
- execução de comando via wizard;
- documentação;
- Project Tree Autorefresh.
