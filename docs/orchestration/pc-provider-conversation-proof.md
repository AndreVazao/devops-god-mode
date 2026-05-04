# PC Runner + Provider Conversation Proof

## Objetivo

A Phase 180 transforma a parte `partial` de conversas IA externas numa missão verificável no PC real.

O God Mode passa a ter:

- ferramenta local de prova no PC;
- comandos seguros para provider escolhido;
- importação de proof JSON para o inventário de conversas;
- ligação ao Global State;
- critério claro de sucesso mínimo e sucesso forte.

## Ferramenta local

```txt
tools/pc_provider_conversation_probe.py
```

Exemplo:

```bash
python tools/pc_provider_conversation_probe.py --provider chatgpt --wait-login-seconds 90
```

A ferramenta:

- abre browser local via Playwright;
- aguarda login manual;
- tenta detetar readiness do provider;
- tenta ler mensagens visíveis;
- tenta listar links candidatos de conversas;
- grava proof JSON em `data/provider_proofs`;
- não exporta cookies/tokens/passwords.

## Endpoints

- `GET/POST /api/pc-provider-conversation-proof/status`
- `GET/POST /api/pc-provider-conversation-proof/install-plan`
- `POST /api/pc-provider-conversation-proof/command`
- `GET/POST /api/pc-provider-conversation-proof/proofs`
- `POST /api/pc-provider-conversation-proof/import-proof`
- `POST /api/pc-provider-conversation-proof/import-latest`
- `GET/POST /api/pc-provider-conversation-proof/package`

## Fluxo real no PC

1. Instalar/abrir o God Mode no PC.
2. Abrir `/app/home`.
3. Ver `/api/pc-provider-conversation-proof/package`.
4. Instalar Playwright se necessário:

```bash
python -m pip install playwright
python -m playwright install chromium
```

5. Executar o comando do provider.
6. Fazer login manual no browser aberto.
7. Aguardar o proof JSON.
8. Importar via `/api/pc-provider-conversation-proof/import-latest`.
9. Confirmar o inventário em `/api/multi-ai-conversation-inventory/package`.

## Sucesso mínimo

- provider abre;
- login manual possível;
- readiness marker detetado ou conversa staged manualmente;
- sem guardar credenciais.

## Sucesso forte

- mensagens visíveis lidas;
- links candidatos de conversas listados;
- proof importado para inventário;
- projeto/conversa fica mapeado para posterior tree/repo work.

## Segurança

- login é manual;
- não exporta cookies;
- não exporta tokens;
- não grava passwords;
- conteúdo com termos sensíveis é redigido;
- qualquer ação de envio/delete/cleanup continua fora deste proof e exige gates próprios.
