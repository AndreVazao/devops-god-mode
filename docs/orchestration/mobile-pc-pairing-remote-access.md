# Mobile APK to PC Pairing + Remote Access Contract

## Objetivo

A Phase 208 permite ligar o APK/telemóvel ao God Mode no PC:

- dentro de casa por LAN/IP local;
- da rua por URL HTTPS remoto aprovado;
- com material remoto guardado apenas no Vault local;
- com retry order para o APK tentar primeiro casa e depois remoto.

## Endpoint principal

```txt
/api/mobile-pc-pairing/package
```

## Página visual

```txt
/app/mobile-pc-pairing
/app/connect-phone
```

## Endpoints

- `/api/mobile-pc-pairing/status`
- `/api/mobile-pc-pairing/create-pairing-session`
- `/api/mobile-pc-pairing/create-remote-access-plan`
- `/api/mobile-pc-pairing/store-remote-material`
- `/api/mobile-pc-pairing/connection-manifest`
- `/api/mobile-pc-pairing/dashboard`
- `/api/mobile-pc-pairing/package`

## Casa / LAN

O PC gera uma pairing session com:

- hostname;
- IPs locais;
- porta 8000;
- URLs locais para o APK tentar;
- pairing_code;
- qr_payload;
- rotas recomendadas.

Exemplo:

```txt
http://192.168.x.x:8000/app/mobile-permission-relay
```

## Rua / acesso remoto

Da rua, o APK não chega ao PC por `127.0.0.1` nem por IP local.

É obrigatório um canal remoto aprovado:

- Cloudflare Tunnel;
- Tailscale;
- Ngrok;
- URL pública HTTPS manual.

O God Mode cria um `remote_access_plan` e, se faltar URL/material, cria um pedido no Mobile Permission Relay.

## Segurança

- Não abre portas do router às cegas.
- Não publica HTTP inseguro na internet.
- Não guarda material remoto no repo.
- Não inicia túnel pago sem aprovação.
- Material remoto fica no Vault local.

## Fluxo prático

```txt
PC: /app/mobile-pc-pairing
→ criar pairing local
→ APK tenta URLs LAN
→ se estiver fora de casa: criar plano remoto
→ fornecer URL HTTPS/túnel aprovado
→ God Mode guarda material no Vault
→ APK tenta URL remoto
```

## Próxima fase provável

A próxima camada deve fazer o APK consumir automaticamente o `connection-manifest`, guardar o último endpoint funcional e alternar casa/rua sem pedir IP manual.

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 207 deve ser apagado. Fica só:

- `.github/workflows/phase208-mobile-pc-pairing-remote-access-smoke.yml`

Além dos workflows globais/builds.
