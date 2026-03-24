# Baribudos Admin Bridge B Architecture

## Decisão

O ecossistema Baribudos adota o modelo **B — API + eventos**.

Isto significa:
- comando administrativo síncrono por API;
- sincronização robusta por eventos;
- infra separada entre Studio e Website;
- comando unificado a partir do Studio.

## Objetivo

Permitir que o **Baribudos Studio** controle o **Baribudos Website** sem fundir hosting, runtime ou disponibilidade.

## Execution Planes

### Studio
- repo: `AndreVazao/baribudos-studio`
- natureza: privada/local
- papel: cérebro editorial, produtivo e administrativo

### Website
- repo: `AndreVazao/baribudos-studio-website`
- natureza: pública/cloud
- papel: runtime comercial, catálogo, checkout, biblioteca, auth cliente

## Control Plane

O Studio é o control plane principal do ecossistema.

O owner/super admin deve conseguir, a partir do Studio:
- publicar e despublicar;
- atualizar catálogo;
- gerir preços e visibilidade;
- gerir admins do website;
- consultar estado comercial resumido;
- disparar sincronizações;
- reprocessar publicações com falha.

## Modelo B

### Camada 1 — Admin API (síncrona)
Usada para ações que precisam de resposta imediata.

#### Ações síncronas mínimas
- `GET /admin/health`
- `GET /admin/catalog/summary`
- `GET /admin/sales/summary`
- `GET /admin/customers/summary`
- `POST /admin/publications/publish`
- `POST /admin/publications/unpublish`
- `POST /admin/products/set-price`
- `POST /admin/products/set-visibility`
- `POST /admin/products/feature`
- `POST /admin/admins/upsert`
- `POST /admin/sync/trigger`

### Camada 2 — Event Bus lógico (assíncrona)
Usada para jobs longos, tolerância a falhas e retry.

#### Eventos mínimos
- `publication.created`
- `publication.updated`
- `publication.unpublished`
- `variant.upserted`
- `asset.upserted`
- `catalog.sync.requested`
- `catalog.sync.completed`
- `catalog.sync.failed`
- `product.repriced`
- `product.visibility.changed`
- `admin.role.updated`
- `publication.reprocess.requested`
- `publication.reprocess.completed`
- `publication.reprocess.failed`

## Estratégia de implementação

### Fase 1 — API-first preparada para eventos
Implementar primeiro:
- Admin API segura no Website;
- contrato de payload versionado;
- tabela de eventos/outbox;
- tabela de jobs/sync status;
- logs de sincronização.

### Fase 2 — Event flow completo
Ativar:
- outbox no Studio;
- consumer no Website;
- retry automático;
- dead-letter lógico;
- histórico de jobs;
- observabilidade resumida.

## Contratos partilhados

### Fonte de verdade editorial (Studio)
- IP
- série
- volume
- publicationId
- variantId
- slugs editoriais
- títulos
- descrições editoriais
- assets base
- idioma
- formato
- estado editorial

### Fonte de verdade comercial publicada (Website)
- preço final publicado
- destaque
- disponibilidade comercial
- auth cliente
- checkout
- biblioteca
- promoções
- distribuição final ao cliente

## Segurança

### Regras obrigatórias
- o Website não depende do PC de casa para continuar online;
- o Website não recebe acesso total ao cérebro privado do Studio;
- o Studio usa chave própria de admin bridge;
- rotação de chaves deve ser suportada;
- todas as operações sensíveis devem ser auditáveis.

### Autenticação mínima
- `STUDIO_PUBLISH_API_KEY`
- assinatura HMAC opcional para payloads críticos
- timestamp/nonce para evitar replay

## Persistência operacional recomendada

### No Website
- `admin_sync_jobs`
- `admin_sync_events`
- `admin_audit_logs`
- `publication_ingest_state`

### No Studio
- `publish_outbox`
- `publish_attempts`
- `ecosystem_admin_actions`

## Regras de comportamento

### Síncrono por API
Usar API quando for necessário:
- resposta imediata;
- validação instantânea;
- ação administrativa curta;
- consulta resumida.

### Assíncrono por eventos
Usar eventos quando houver:
- publicação pesada;
- assets múltiplos;
- rebuild de catálogo;
- reprocessamento;
- retry;
- tolerância a falhas;
- desacoplamento entre execução local e cloud.

## Resultado-alvo

Do futuro PC em casa, entrando no Studio, o super admin deve conseguir:
- mandar no Website;
- ver o resumo operacional do Website;
- publicar sem entrar no runtime público;
- manter o Website autónomo e online;
- operar o ecossistema como um produto único com infra separada.

## Interpretação pelo God Mode

O God Mode deve ler este caso como:
- `admin_bridge_mode = B_API_PLUS_EVENTS`
- `shared_admin_governance = true`
- `shared_super_admin = true`
- `separate_runtime_infrastructure = true`
- `studio_is_primary_control_plane = true`
- `website_is_public_execution_plane = true`
