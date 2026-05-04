# Home/App Control Surface

## Objetivo

A Phase 172 cria uma superfície única para PC/APK renderizarem o cockpit do God Mode com botões reais.

A Home/App deixa de depender de hardcode local e passa a poder chamar:

```txt
/api/home-control-surface/package
```

Esse pacote inclui:

- estado geral;
- política de risco;
- módulos;
- botões;
- manifesto para APK/WebView;
- manifesto para desktop launcher.

## Módulos expostos

- Playbook Templates;
- Pipeline Store + Low-Risk Executor;
- Memory Sync Runtime;
- GitHub Approved Actions;
- Local Knowledge/RAG;
- Provider Outcome Learning;
- Histórico/Auditoria.

## Segurança

A Home/App não executa ações destrutivas diretamente.

Não expõe botões para:

- merge direto;
- release direto;
- delete direto;
- alterações de credenciais;
- alterações de pagamentos;
- alterações de licenças.

Ações de maior risco continuam dependentes dos gates próprios:

- Approved GitHub Actions exige plano aprovado e frase de aprovação;
- Memory Sync real mantém dry-run por defeito;
- Low-Risk Executor só executa passos classificados como seguros;
- Provider Learning é advisory;
- Local RAG é local-first e não envia contexto externo por defeito.

## Endpoints

- `GET/POST /api/home-control-surface/status`
- `GET/POST /api/home-control-surface/panel`
- `GET/POST /api/home-control-surface/policy`
- `GET/POST /api/home-control-surface/rules`
- `GET/POST /api/home-control-surface/modules`
- `GET/POST /api/home-control-surface/buttons`
- `GET/POST /api/home-control-surface/quick-start`
- `GET/POST /api/home-control-surface/mobile-shell`
- `GET/POST /api/home-control-surface/desktop-shell`
- `GET/POST /api/home-control-surface/latest`
- `GET/POST /api/home-control-surface/package`

## Contrato de botão

Cada botão contém:

- `id`
- `label`
- `description`
- `method`
- `endpoint`
- `risk`
- `requires_confirmation`
- `default_payload`

## Contrato visual

Cada módulo devolve:

- `id`
- `label`
- `description`
- `panel_endpoint`
- `traffic_light`
- `status`
- `buttons`

O PC/APK deve renderizar módulos como cards e botões como ações contextuais.

## Próxima evolução

Depois desta fase, o próximo passo é ligar estes manifests diretamente ao ecrã Home do frontend/desktop/APK e criar componentes visuais reais com status verde/amarelo/vermelho.
