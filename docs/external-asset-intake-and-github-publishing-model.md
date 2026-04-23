# External Asset Intake And GitHub Publishing Model

## Objetivo
Preparar o God Mode para ir além de scripts e conversas, passando também a conseguir:
- descobrir assets externos em serviços web
- registar origem e rastreabilidade desses assets
- fazer staging local antes de qualquer publicação
- planear publicação direta em repositórios GitHub
- suportar fluxos de websites, branding, ícones, imagens e ficheiros estáticos

## Regra principal
O fluxo continua local-first:
- o PC é o executor principal
- o telefone é o cockpit principal
- os assets devem ser preparados localmente primeiro
- a publicação remota deve acontecer só depois do staging e da definição do destino

## Tipos de fonte previstos
### 1. Browser web services
Usado para:
- entrar em sites e ferramentas web
- recolher imagens, snippets, scripts e material de projeto
- guardar referência da origem para auditoria interna

### 2. Drive-like storage
Usado para:
- puxar imagens e ficheiros de apoio
- preparar material para websites, apps e branding
- servir como fonte intermédia antes de publicação em repo

### 3. GitHub repositories
Usado para:
- colocar ícones, imagens, fontes e assets estáticos dentro da estrutura do repo
- iterar com download, alteração e re-upload
- fechar o ciclo entre geração local e publicação real

## Pipeline pretendido
1. Descobrir asset numa fonte externa.
2. Registar `source_type`, `source_ref` e `asset_role`.
3. Fazer staging local.
4. Associar `project_hint`, `repository_full_name` e `destination_path` quando existirem.
5. Gerar um plano de publicação GitHub.
6. Executar publicação real ou dry run controlado no repo.
7. Materializar assets staged em disco local quando o fluxo exigir ficheiros reais.
8. Transformar assets locais antes do packaging e do publish final quando necessário.
9. Recolocar assets do workspace de volta no pipeline de publish quando uma versão local ficar pronta.
10. Fazer fetch externo real para staging quando o asset ainda não existe localmente.
11. Gerar derivados locais úteis para entrega, preview e packaging quando o asset base já existir.
12. Agrupar assets e derivados em bundles locais navegáveis para preview e entrega.
13. Recolocar bundles locais completos de volta no pipeline de staging e publish.

## Base já consolidada
O sistema já passou a ter:
- `external_asset_intake_service`
- staging persistente em `data/external_asset_intake.json`
- rota `external-asset-intake`
- suporte HTTP para `content_text`, `content_base64` e `content_kind`
- plano de publicação GitHub baseado em assets staged
- helpers no `github_service` para leitura e escrita de ficheiros/asset no repo
- `external_asset_publish_execution_service`
- rota `external-asset-publish`
- execução dry run do publish plan
- `external_asset_materialization_service`
- rota `external-asset-materialization`
- materialização de ficheiros textuais do GitHub diretamente para staging local
- `local_asset_workspace_service`
- rota `local-asset-workspace`
- materialização de staged assets para disco local em `data/staged_asset_workspace`
- `local_asset_transformation_service`
- rota `local-asset-transformation`
- transformações locais de texto e duplicação no workspace
- `workspace_publish_bridge_service`
- rota `workspace-publish-bridge`
- restage e publish dry run a partir de versões locais transformadas
- `external_fetch_runtime_service`
- rota `external-fetch-runtime`
- fetch HTTP real de URL para staging
- download local em `data/external_fetch_runtime`
- inferência básica de texto/binário para staging imediato
- suporte a `auth_mode`, `auth_value`, `extra_headers` e `user_agent` no fetch externo
- manifesto `.fetch.json` por download externo
- metadados de `bytes_downloaded`, `content_kind` e contagem de headers extra
- `asset_derivative_service`
- rota `asset-derivative`
- criação de `svg wrapper` para assets textuais do workspace
- criação de sidecar metadata `.asset.json` para binários
- base para variantes locais de preview, entrega e packaging
- `preview_packaging_service`
- rota `preview-packaging`
- criação de bundles locais em `data/preview_packages`
- geração de `index.html` navegável para preview
- manifesto `bundle.manifest.json` por pacote local
- criação de `.zip` local do bundle

## Evolução desta fase
Agora o sistema também passa a ter:
- `bundle_publish_link_service`
- rota `bundle-publish-link`
- restage de bundles completos para o intake
- dry run de publish do bundle para destino remoto controlado
- base para tratar bundle como unidade de entrega e publicação

## Porque isto interessa
Esta camada fecha outro passo crítico:
- já não basta gerar bundle e archive localmente
- o sistema passa a conseguir pegar nesse bundle pronto e devolvê-lo ao pipeline normal
- isso aproxima bastante a entrega final real, com menos trabalho manual entre packaging e publicação

## Próxima evolução esperada
A seguir o sistema deve ganhar:
- publicação real controlada do bundle completo
- previews gráficos mais ricos para SVG/imagem/ícones
- packaging mais orientado a entrega final multi-target
- ligação desta camada ao browser intake e ao continuation engine
