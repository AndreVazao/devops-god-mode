# Easy Mode Result Cards

## Objetivo

Melhorar o resultado visual do `Modo fácil` na Home.

Antes, depois de carregar num comando rápido, o operador via principalmente JSON bruto. A Phase 89 adiciona cartões de resultado legíveis para uso no telemóvel/APK.

## Integração

Frontend:

- `/app/home`
- `/app/god-mode`
- `/app/god-mode-home`

APIs usadas:

- `GET /api/home-operator-ux/panel`
- `POST /api/daily-command-router/route`

## Cartão de resultado

O cartão mostra:

- estado da ação;
- `command_id`;
- projeto;
- job;
- stop reason;
- score quando existir;
- passos quando existir;
- artifacts quando existir;
- próxima ação;
- botão para abrir próxima ação;
- botão `Ver JSON` para diagnóstico.

## Casos cobertos

- comando de chat com job;
- guia de instalação com passos;
- snapshot de saúde com score;
- artifacts com contagem de pacotes;
- erro/ação com problema.

## Segurança

- Não muda a lógica de execução.
- Não contorna aprovações.
- Só altera apresentação visual do resultado.
- JSON continua disponível para diagnóstico.
