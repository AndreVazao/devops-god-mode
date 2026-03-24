# Baribudos Ecosystem Governance

## Objetivo

Definir a governação manual inicial do ecossistema Baribudos dentro do DevOps God Mode, preservando:

- produto lógico único;
- infra separada;
- comando administrativo unificado;
- publicação segura entre Studio e Website.

## Produto Lógico

- **Product Key:** `baribudos-ecosystem`
- **Display Name:** `Baribudos Ecosystem`
- **Mode:** `single_product_view`

## Repositórios Membro

### 1. Studio
- **Repo:** `AndreVazao/baribudos-studio`
- **Role:** `private_editorial_brain`
- **Runtime:** `private_local`
- **Responsabilidades principais:**
  - produção editorial;
  - geração de ebooks/audiobooks/assets;
  - frontoffice privado;
  - operação familiar;
  - comando administrativo central.

### 2. Website
- **Repo:** `AndreVazao/baribudos-studio-website`
- **Role:** `public_commerce_runtime`
- **Runtime:** `public_cloud`
- **Responsabilidades principais:**
  - catálogo público;
  - venda;
  - biblioteca do cliente;
  - checkout;
  - auth pública;
  - distribuição comercial.

## Relações Oficiais

### Relações de produto
- `baribudos-studio` -> `publishes_to` -> `baribudos-studio-website`
- `baribudos-studio-website` -> `consumes_catalog_from` -> `baribudos-studio`
- `baribudos-studio` <-> `shares_contract_with` <-> `baribudos-studio-website`
- `baribudos-studio` <-> `shared_admin_governance` <-> `baribudos-studio-website`

### Relação de comando
- `baribudos-studio` -> `controls_admin_plane_of` -> `baribudos-studio-website`

## Regras de Governação

### Regra 1 — Produto único lógico
As duas repos pertencem ao mesmo produto lógico e devem aparecer no painel como um único ecossistema.

### Regra 2 — Infra obrigatoriamente separada
O Website não pode depender da disponibilidade do PC de casa para ficar online.

### Regra 3 — Studio como cérebro editorial
O Studio é a fonte principal de verdade editorial, produtiva e operacional privada.

### Regra 4 — Website como runtime comercial público
O Website é a camada pública/comercial do que foi publicado, sincronizado e autorizado.

### Regra 5 — Fusão de comando, não de hosting
A "fusão" entre estas duas repos é feita ao nível de:
- painéis;
- permissões;
- governação;
- catálogo lógico;
- workflows administrativos;
- visão operacional.

Não é feita ao nível de:
- hosting;
- runtime;
- dependência pública ao PC privado;
- exposição do cérebro privado.

### Regra 6 — Super Admin transversal
O mesmo Super Admin do ecossistema deve conseguir, a partir do Studio:
- publicar e despublicar produtos no Website;
- atualizar catálogo, preços e estado de publicação;
- gerir admins e painéis do Website;
- consultar estado comercial e operacional;
- disparar sync e reprocessamentos.

### Regra 7 — Admin Bridge obrigatória
A ligação Studio -> Website deve existir através de uma camada segura de administração e sincronização.

## Admin Bridge — Capacidades mínimas

A ponte administrativa entre Studio e Website deve suportar, no mínimo:

- `publish_publication`
- `unpublish_publication`
- `sync_catalog`
- `upsert_variant`
- `upsert_assets`
- `set_product_visibility`
- `set_product_price`
- `feature_product`
- `list_sales_summary`
- `list_customers_summary`
- `rotate_admin_key`
- `reprocess_publication`

## Contrato Partilhado

### Fonte editorial base
Deve nascer no Studio:
- IP;
- série;
- volume;
- publicationId;
- variantId;
- slugs editoriais;
- títulos;
- descrição editorial;
- assets principais;
- idioma;
- formato;
- estado editorial.

### Camada comercial pública
Deve viver no Website:
- preço final publicado;
- destaque;
- disponibilidade comercial;
- checkout;
- biblioteca;
- auth cliente;
- promoções;
- distribuição ao cliente.

## Restrições Críticas

- `must_remain_separate_infrastructure = true`
- `studio_is_editorial_source_of_truth = true`
- `website_is_public_commercial_runtime = true`
- `website_must_not_depend_on_home_pc_availability = true`
- `shared_super_admin = true`
- `shared_admin_governance = true`
- `studio_controls_website_via_admin_bridge = true`

## Estratégia de Alinhamento

### Deve alinhar sempre
- schema de publicação;
- IDs globais;
- variant IDs;
- slugs;
- assets publicados;
- preço/moeda publicados;
- estados de publicação;
- payload de sincronização.

### Não deve ser acoplado diretamente
- runtime do Website ao runtime do Studio;
- segredos internos do Studio ao Website;
- pipelines privados completos dentro da app pública.

## Interpretação pelo God Mode

O DevOps God Mode deve interpretar este ecossistema como:

- **1 produto lógico**;
- **2 execution planes**;
- **1 control plane administrativo**;
- **1 contrato partilhado de publicação**;
- **1 política forte de infra separada com comando unificado**.

## Estado-Alvo

Do futuro PC de casa, entrando no Studio, o owner/super admin deve conseguir operar:

- produção privada;
- catálogo lógico;
- publicação pública;
- administração do Website;
- visão comercial resumida;
- sincronização e correção do ecossistema.
