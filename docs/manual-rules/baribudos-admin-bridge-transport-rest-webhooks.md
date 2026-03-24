# Baribudos Admin Bridge Transport — REST + Webhooks

## Decisão

O ecossistema **Baribudos** adota **REST + Webhooks** como transporte oficial da ponte administrativa entre:

- `AndreVazao/baribudos-studio`
- `AndreVazao/baribudos-studio-website`

## Justificação

Este modelo permite:

- controlo administrativo direto do Studio sobre o Website;
- resposta imediata para operações curtas;
- notificações assíncronas para estado, falha e sincronização;
- separação de infraestrutura;
- baixo acoplamento de runtime;
- evolução futura sem reescrever a arquitetura.

## Princípio arquitetural

### Studio
- command plane primário;
- inicia comandos;
- publica conteúdos;
- gere admins;
- consulta estado do Website.

### Website
- execution plane público;
- executa catálogo e vendas;
- responde a comandos REST;
- dispara webhooks para devolver eventos operacionais.

### God Mode
- observador;
- reparador;
- auditor;
- alinhador de ecossistema.

## Distribuição de responsabilidades

### REST
Usado para pedidos iniciados pelo Studio que exigem resposta imediata.

### Webhooks
Usados pelo Website para devolver:
- confirmação de processamento;
- falha;
- sync concluído;
- reprocessamento;
- eventos comerciais resumidos;
- estado assíncrono de jobs.

## REST endpoints mínimos no Website

### Saúde e estado
- `GET /admin/health`
- `GET /admin/catalog/summary`
- `GET /admin/sales/summary`
- `GET /admin/customers/summary`
- `GET /admin/sync/jobs/:jobId`

### Publicação e catálogo
- `POST /admin/publications/publish`
- `POST /admin/publications/unpublish`
- `POST /admin/variants/upsert`
- `POST /admin/assets/upsert`
- `POST /admin/catalog/sync`

### Produto/comercial
- `POST /admin/products/set-price`
- `POST /admin/products/set-visibility`
- `POST /admin/products/feature`

### Administração
- `POST /admin/admins/upsert`
- `POST /admin/admins/deactivate`
- `POST /admin/keys/rotate`

### Reprocessamento
- `POST /admin/publications/reprocess`

## Webhooks mínimos disparados pelo Website

### Processamento e sync
- `publication.publish.accepted`
- `publication.publish.completed`
- `publication.publish.failed`
- `publication.unpublish.completed`
- `catalog.sync.completed`
- `catalog.sync.failed`
- `publication.reprocess.completed`
- `publication.reprocess.failed`

### Produto/comercial
- `product.price.updated`
- `product.visibility.updated`
- `product.featured.updated`

### Administração
- `admin.user.upserted`
- `admin.user.deactivated`
- `admin.key.rotated`

## Regras de segurança

### REST
Cada pedido do Studio para o Website deve incluir:
- chave de administração dedicada;
- timestamp;
- nonce;
- assinatura HMAC para payloads críticos.

### Webhooks
Cada webhook do Website para o Studio deve incluir:
- assinatura HMAC própria do Website;
- event id único;
- timestamp;
- retry seguro sem duplicação lógica.

## Regras de idempotência

As seguintes operações devem ser idempotentes:
- `publish`
- `unpublish`
- `upsert variant`
- `upsert assets`
- `set price`
- `set visibility`
- `feature product`
- `reprocess publication`

## Contrato de payload mínimo

### Publication publish command
```json
{
  "publicationId": "pub_001",
  "projectId": "baribudos_story_001",
  "projectSlug": "a-floresta-dos-baribudos",
  "channel": "website",
  "language": "pt-PT",
  "sourceSystem": "baribudos-studio",
  "status": "ready",
  "variants": [],
  "assets": []
}
```

### Webhook event envelope
```json
{
  "eventId": "evt_001",
  "eventType": "publication.publish.completed",
  "sourceSystem": "baribudos-studio-website",
  "occurredAt": "2026-03-24T00:00:00Z",
  "payload": {}
}
```

## Regras operacionais

### REST deve ser usado para
- ações curtas;
- leitura resumida;
- controlo administrativo direto;
- trigger explícito de sync e publicação.

### Webhooks devem ser usados para
- devolução de estado;
- processamento concluído;
- falhas;
- confirmações assíncronas;
- observabilidade do ecossistema.

## Restrições oficiais

- `admin_bridge_transport = REST_PLUS_WEBHOOKS`
- `studio_calls_website_directly = true`
- `website_reports_back_to_studio_via_webhooks = true`
- `god_mode_does_not_sit_in_the_runtime_command_path = true`
- `shared_admin_governance = true`
- `separate_runtime_infrastructure = true`

## Resultado-alvo

Do futuro PC em casa, ao entrar no Studio, o owner/super admin deve conseguir:
- controlar o Website;
- receber resposta imediata para operações administrativas curtas;
- receber notificações assíncronas de sucesso/falha;
- operar o ecossistema como um produto lógico único com runtime separado.
