# God Mode Home

## Cockpit

- `/app/god-mode-home`
- `/app/home`

## API

- `GET /api/god-mode-home/status`
- `GET /api/god-mode-home/package`
- `GET /api/god-mode-home/dashboard`
- `GET /api/god-mode-home/driving-mode`
- `POST /api/god-mode-home/one-tap`
- `POST /api/god-mode-home/chat`

## Objetivo

Criar uma entrada principal simples para o God Mode, pensada para telemóvel e APK.

O operador não deve ter de decorar cockpits, comandos ou rotas técnicas. A Home responde:

> O que carrego agora?

## Regra principal para o APK

O APK trabalha em modo de conversa corrida tipo ChatGPT.

Por isso, a Home não substitui o chat. Ela funciona como:

- entrada rápida;
- resumo de estado;
- decisão da próxima ação;
- fallback com botões grandes;
- ponte para `/app/operator-chat-sync`.

## Chat-first contract

A resposta de `/api/god-mode-home/dashboard` inclui `chat_contract` com estas regras:

- conversas corridas são a superfície principal no APK;
- botões devem aparecer como ações sugeridas dentro do chat;
- aprovações, inputs seguros e replay devem aparecer inline na conversa;
- não guardar segredos em memória AndreOS.

## One-tap actions

A Home suporta ações de um toque:

- `one-tap-money`: cria cartão de aprovação para sprint de dinheiro;
- `one-tap-continue-god-mode`: continua God Mode por comando guiado;
- `one-tap-review-memory`: revê memória do projeto ativo.

## Chat endpoint

`POST /api/god-mode-home/chat` permite ao APK enviar mensagens como:

- “continua”;
- “quero ganhar dinheiro”;
- “revê memória”;
- “tenho aprovações?”;
- “avança para próxima fase”.

O serviço responde com:

- `reply`;
- `suggested_next_steps`;
- `thread_id`;
- thread atualizada no sistema de conversa contínua.

## Segurança

A Home bloqueia mensagens que pareçam conter:

- token;
- password;
- bearer;
- authorization;
- cookie;
- api key;
- secrets.

Essas mensagens não entram como conteúdo normal no chat e não são escritas na memória AndreOS.

## Modo condução

`GET /api/god-mode-home/driving-mode` devolve frases curtas e botões seguros para uso em contexto móvel, evitando escrita longa.

## Integrações

- Operator Chat Runtime Snapshot;
- Operator Conversation Thread;
- Money Command Center;
- Mobile Approval Cockpit;
- Mission Control;
- Guided Command Center;
- Project Portfolio;
- Self Update;
- AndreOS Memory Core.
