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

## Base já consolidada
O sistema já passou a ter:
- `external_asset_intake_service`
- staging persistente em `data/external_asset_intake.json`
- rota `external-asset-intake`
- plano de publicação GitHub baseado em assets staged
- helpers no `github_service` para leitura e escrita de ficheiros/asset no repo
- `external_asset_publish_execution_service`
- rota `external-asset-publish`
- execução dry run do publish plan
- suporte inicial a conteúdo inline staged para texto ou binário base64
- `external_asset_materialization_service`
- rota `external-asset-materialization`
- materialização de ficheiros textuais do GitHub diretamente para staging local

## Evolução desta fase
Agora o sistema também passa a ter:
- `local_asset_workspace_service`
- rota `local-asset-workspace`
- materialização de staged assets para disco local em `data/staged_asset_workspace`
- criação de manifestos por asset materializado
- materialização por asset individual ou por projeto inteiro (`project_hint`)

## Porque isto interessa
Esta camada aproxima o God Mode de um fluxo real de produção:
- staged asset deixa de ser apenas estado lógico
- passa a existir como ficheiro real no disco local
- isso prepara edição, transformação, preview, packaging e publicação posterior

## Próxima evolução esperada
A seguir o sistema deve ganhar:
- execução real de fetch/download externo fora do GitHub
- staging binário local de imagens e ficheiros vindos de serviços externos
- transformação de assets no workspace local antes de publicar
- ligação desta camada ao browser intake e ao continuation engine
- distinção mais forte entre assets de referência, assets materializados e assets prontos para publish real
