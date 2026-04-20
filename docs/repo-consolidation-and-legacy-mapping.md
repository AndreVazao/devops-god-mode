# Repo Consolidation And Legacy Mapping

## Objetivo
Consolidar o estado real da repo, distinguir o que é core ativo do que já funciona como foundation antiga ou histórico documental, e reduzir drift entre arquitetura atual e documentação pública.

## Estado real consolidado
O `main` já representa um sistema muito mais avançado do que o bootstrap inicial:
- backend FastAPI com múltiplas rotas operacionais
- packaging desktop Windows real
- handoff PC + telemóvel
- inventário, extração, reaproveitamento e adaptação de scripts
- organização de conversas
- intake operacional de chats
- browser control assistido
- cockpit móvel
- driving mode seguro
- camada de orquestração contextual

## Matriz operacional
### KEEP (core ativo)
Manter como parte principal da repo:
- tudo o que está ligado em `backend/main.py`
- `desktop/godmode_desktop_launcher.py`
- `desktop/GodModeDesktop.spec`
- `desktop/windows_shortcut_bootstrap.ps1`
- `desktop/windows_autostart_bootstrap.ps1`
- `desktop/windows_autostart_remove.ps1`
- `windows-exe-real-build.yml`
- workflows smoke das fases já integradas no `main`

### LEGACY FOUNDATION (não apagar já)
Tratar como foundation antiga ou placeholder ainda útil como histórico:
- `docs/android-mobile-build-plan.md`
- `docs/android-real-runtime-shell-v2-plan.md`
- `docs/android-real-runtime-shell-plan.md`
- `docs/apk-real-build-and-pc-phone-bootstrap-plan.md`
- `.github/workflows/android-mobile-build.yml`

### REVIEW BEFORE DELETE
Rever numa fase seguinte antes de apagar:
- contracts Android antigos que só alimentam foundations placeholder
- docs transitórios de correções de workflow já absorvidas por versões estáveis
- qualquer workflow smoke que já não dispare por caminhos do `main`

## Ajustes aplicados nesta fase
1. Atualização do `README.md` para refletir a arquitetura e o estado atual.
2. Atualização do workflow `android-mobile-build.yml` para deixar de apontar só para uma feature branch antiga.
3. Registo explícito da distinção entre core atual e foundations antigas.

## Próximo alvo de consolidação
Depois desta fase, a limpeza seguinte deve focar:
- Android placeholder versus build Android real
- documentação legacy em pasta de arquivo dedicada
- revisão dos contracts Android antigos
- simplificação dos workflows que já não representam o fluxo principal
