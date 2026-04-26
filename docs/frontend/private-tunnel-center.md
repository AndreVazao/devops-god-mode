# Private Tunnel Center

## Cockpit

- `/app/private-tunnel`
- `/app/street-mode`

## API

- `GET /api/private-tunnel/status`
- `GET /api/private-tunnel/package`
- `GET /api/private-tunnel/report`
- `GET /api/private-tunnel/dashboard`

## Objetivo

Permitir ligação APK → PC quando o operador está fora da rede local.

O caminho recomendado é uma rede privada tipo Tailscale, instalada manualmente no PC e no telemóvel.

## Regra de segurança

O God Mode não guarda:

- tokens;
- passwords;
- cookies;
- auth keys;
- API keys;
- secrets.

Login e configuração do provider são manuais.

## Provider recomendado

### Tailscale

Motivo:

- cria rede privada entre PC e telemóvel;
- evita expor o backend diretamente na internet;
- tem plano gratuito para uso pessoal;
- funciona bem para cenário rua → PC.

Fluxo:

1. Instalar Tailscale no PC.
2. Entrar manualmente.
3. Instalar Tailscale no telemóvel.
4. Entrar na mesma rede.
5. O God Mode tenta detetar `tailscale ip -4`.
6. O APK usa `http://TAILSCALE_IP:8000`.
7. O APK testa `/health` e abre `/app/apk-start`.

## Alternativas

### Cloudflare Tunnel

Pode ser útil, mas não é o default porque pode criar URL público se for mal configurado.

### ngrok/localtunnel

Útil só como fallback temporário. Não recomendado para operação normal sem controlos de autenticação.

## Integração com APK

Dentro da rede local:

- usar Auto Discovery;
- se falhar, usar `/app/pairing`.

Na rua:

- usar Tailscale no PC e no telemóvel;
- abrir APK;
- usar Auto se possível;
- se falhar, colar o URL Tailscale recomendado.

## Limites

Pode falhar se:

- PC estiver desligado;
- backend não estiver a correr;
- firewall bloquear porta 8000;
- Tailscale não estiver ligado;
- telemóvel e PC não estiverem na mesma rede privada Tailscale.
