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

## Pivot arquitetural assumido
A repo nasceu em cima de uma foundation antiga com:
- Supabase
- Render
- Vercel

Essa foundation deixou de ser o rumo principal.
O rumo oficial passa a ser:
- PC como cérebro principal
- telefone como cockpit principal
- runtime local-first
- operação segura para trabalho na rua e em condução assistida

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
- serviços e rotas que reforçam runtime local, cockpit móvel e condução segura

### LEGACY FOUNDATION (não apagar já)
Tratar como foundation antiga ou placeholder ainda útil como histórico:
- `docs/android-mobile-build-plan.md`
- `docs/android-real-runtime-shell-v2-plan.md`
- `docs/android-real-runtime-shell-plan.md`
- `docs/apk-real-build-and-pc-phone-bootstrap-plan.md`
- `.github/workflows/android-mobile-build.yml`
- qualquer nota antiga ligada a Supabase, Render ou Vercel que ainda sirva só como histórico de migração

### REMOVE OR ISOLATE
Remover, isolar ou desativar à medida que for seguro:
- configs e envs cloud que já não participam no fluxo PC + telefone
- ingest e persistência cloud que já não sejam necessários para o runtime local-first
- referências a deploy Vercel ou backend Render que já não representem o produto real

### REVIEW BEFORE DELETE
Rever numa fase seguinte antes de apagar:
- contracts Android antigos que só alimentam foundations placeholder
- docs transitórios de correções de workflow já absorvidas por versões estáveis
- qualquer workflow smoke que já não dispare por caminhos do `main`
- restos cloud que ainda existam apenas por compatibilidade temporária

## Ajustes aplicados nesta fase
1. Atualização do `README.md` para refletir a arquitetura e o estado atual.
2. Registo explícito da distinção entre core atual e foundations antigas.
3. Desativação da lógica de ingest cloud do registry em favor de preview local-first.
4. Remoção de envs e dependências diretas de Supabase/Vercel do backend principal.

## Próximo alvo de consolidação
Depois desta fase, a limpeza seguinte deve focar:
- Android placeholder versus build Android real
- documentação legacy em pasta de arquivo dedicada
- revisão dos contracts Android antigos
- simplificação dos workflows que já não representam o fluxo principal
- verificação final de restos Supabase, Render e Vercel ainda espalhados pela repo
