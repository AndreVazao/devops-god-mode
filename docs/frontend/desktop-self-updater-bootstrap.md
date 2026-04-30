# Desktop Self Updater Bootstrap

## Objetivo

Criar a base para o God Mode atualizar o EXE/backend por pacote, sem obrigar a reinstalar tudo a cada correção pequena.

## Verdade operacional

O EXE antigo que não tinha updater não consegue atualizar-se sozinho. Por isso, a primeira instalação com updater ainda precisa ser manual.

Depois de instalada esta versão, o God Mode passa a ter infraestrutura para updates futuros por pacote.

## O que entra

- Serviço `desktop_self_update_service.py`
- Rota `desktop_self_update.py`
- Helper `desktop/godmode_update_helper.py`
- Botão `Atualizações` na Home/Modo Fácil
- Inclusão do helper no artifact Windows

## Endpoints

- `GET/POST /api/desktop-self-update/status`
- `GET/POST /api/desktop-self-update/panel`
- `GET/POST /api/desktop-self-update/policy`
- `GET/POST /api/desktop-self-update/manifest`
- `POST /api/desktop-self-update/compare`
- `POST /api/desktop-self-update/prepare-local-package`
- `POST /api/desktop-self-update/clear-pending`
- `GET/POST /api/desktop-self-update/package`

## Home / Modo Fácil

Novo botão:

- `Atualizações` → `/api/desktop-self-update/panel`

Novo comando rápido:

- `open_desktop_self_update`

## Como deve funcionar no futuro

1. God Mode abre.
2. Consulta versão atual local.
3. Consulta manifesto remoto ou pacote disponível.
4. Se houver update, avisa o operador.
5. Baixa/prepara pacote.
6. Fecha runtime com segurança.
7. Faz backup do EXE anterior.
8. Substitui o EXE/ficheiros necessários.
9. Reabre o God Mode.
10. Mantém dados em `%APPDATA%/GodModeDesktop`.

## O que esta fase já permite

- Declarar versão local.
- Gerar manifesto local.
- Preparar update por pacote local `.zip`.
- Guardar update pendente.
- Incluir helper de atualização no bundle Windows.
- Fazer backup básico antes de substituir EXE.

## Limitação atual

Atualização automática a partir de GitHub Actions artifacts privados ainda precisa de camada de autenticação/distribuição própria, porque artifacts de repo privado não são links públicos diretos.

## Segurança

- Não apaga memória.
- Não apaga APPDATA.
- Não guarda tokens.
- Não executa pacote inexistente.
- Só prepara update local se o ficheiro existir.
- Mantém backup do EXE anterior.
