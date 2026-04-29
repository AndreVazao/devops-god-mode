# External AI Session Plan

## Objetivo

A Phase 106 cria a base segura para sessões com IAs externas.

Ela ainda não automatiza browser/scroll/prompt final. O objetivo desta fase é preparar o contrato certo antes da automação real:

- registo de IAs externas;
- plano de sessão;
- pedido de login manual por popup;
- checkpoints sem segredos;
- retoma após falha de internet/backend;
- política de não guardar credenciais.

## Endpoints

- `GET/POST /api/external-ai-session/status`
- `GET/POST /api/external-ai-session/providers`
- `GET/POST /api/external-ai-session/policy`
- `GET/POST /api/external-ai-session/resume-contract`
- `POST /api/external-ai-session/plan`
- `POST /api/external-ai-session/login-popup`
- `POST /api/external-ai-session/checkpoint`
- `GET/POST /api/external-ai-session/resume`
- `GET/POST /api/external-ai-session/latest`
- `GET/POST /api/external-ai-session/package`

## Ligação à Home

A Home passa a expor:

- `Sessões IA`
- `/api/external-ai-session/package`

## Provedores iniciais

- ChatGPT
- Claude
- Gemini
- Perplexity
- Ollama local

## Login manual/popup

Quando o backend tentar abrir uma IA externa e precisar de login, o fluxo correto é:

1. backend cria `login-popup`;
2. operador recebe popup/ação na Home/APK;
3. operador abre browser e faz login manualmente;
4. God Mode recebe apenas confirmação de que o login foi feito;
5. God Mode não guarda password, token, cookie, código 2FA, bearer, authorization ou API key.

## Retoma após falha de internet/backend

A Phase 106 define contrato de retoma:

- se cair antes de enviar prompt: retoma do último checkpoint seguro;
- se cair depois de enviar prompt e antes da resposta: volta à conversa e lê mensagens recentes antes de reenviar;
- se o browser fechar: reabre URL, reconfirma login e conversa;
- se o backend reiniciar: carrega último checkpoint sem credenciais;
- se houver incerteza: pede intervenção do operador;
- evita duplicar prompt quando não tem certeza.

## Checkpoints

Os checkpoints guardam apenas estado seguro, como:

- sessão;
- provedor;
- passo atual;
- URL/conversa;
- resumo curto;
- flags de login/manual;
- estado de retoma.

Não guardam segredos.

## Segurança

- Não guardar credenciais.
- Não guardar cookies/tokens.
- Não enviar prompts sensíveis sem gate.
- Não duplicar prompts após falha de rede.
- Retomar alguns passos atrás quando necessário.

## Próximo passo

A próxima fase lógica é implementar a camada real de browser/session worker:

- abrir browser controlado;
- detetar login;
- pedir popup se necessário;
- ler mensagens visíveis;
- fazer scroll seguro;
- preparar envio de prompt;
- guardar checkpoints durante o processo.
