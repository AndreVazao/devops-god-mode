# APK PC Pairing Wizard

## Objetivo

A Phase 133 cria o wizard de primeiro arranque para ligar o APK ao backend no PC sem o operador ter de descobrir IPs/portas manualmente.

## Endpoints

- `GET/POST /api/apk-pc-pairing/status`
- `GET/POST /api/apk-pc-pairing/panel`
- `GET/POST /api/apk-pc-pairing/guide`
- `POST /api/apk-pc-pairing/start`
- `POST /api/apk-pc-pairing/confirm`
- `POST /api/apk-pc-pairing/heartbeat`
- `GET/POST /api/apk-pc-pairing/latest`
- `GET/POST /api/apk-pc-pairing/package`

## Fluxo

1. Abrir God Mode no PC.
2. Clicar em `Emparelhar APK`.
3. O backend gera sessão curta com:
   - IPs locais;
   - URLs base;
   - código de pairing;
   - payload QR;
   - token temporário.
4. O APK lê QR ou usa URL/código manual.
5. O APK chama `/confirm`.
6. O APK chama `/heartbeat` para confirmar ligação viva.
7. O APK abre Modo Fácil/Home.

## Segurança

- O token é devolvido uma vez para QR/manual pairing.
- O backend guarda apenas hash do token.
- O token expira.
- Não guarda passwords, cookies, bearer tokens, authorization headers ou API keys.
- Login de providers continua manual no browser quando necessário.

## Fallbacks

- Se QR falhar, usar URL manual.
- Se IP não abrir, confirmar mesma rede Wi-Fi.
- Se firewall bloquear, permitir backend no Windows.
- Se APK fechar, backend continua e heartbeat retoma depois.

## Próximo passo

Ligar este endpoint à Home/Modo Fácil como botão:

`Emparelhar APK`

endpoint:

`/api/apk-pc-pairing/panel`
