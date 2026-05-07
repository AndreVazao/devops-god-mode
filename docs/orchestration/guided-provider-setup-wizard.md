# Guided Provider Setup Wizard

## Objetivo

A Phase 212 cria um assistente guiado para configurar providers externos necessários ao acesso remoto do God Mode.

Providers suportados:

- Tailscale;
- Cloudflare Tunnel;
- Ngrok;
- Manual HTTPS URL.

## Página visual

```txt
/app/guided-provider-setup
/app/setup-remote-access
```

## API

```txt
/api/guided-provider-setup/status
/api/guided-provider-setup/providers
/api/guided-provider-setup/start
/api/guided-provider-setup/capture-result
/api/guided-provider-setup/dashboard
/api/guided-provider-setup/package
```

## Regra segura

O God Mode pode:

- abrir a página oficial;
- mostrar passos e campos necessários;
- guiar o Oner no setup;
- mostrar iframe quando o provider permitir;
- abrir nova aba quando iframe for bloqueado;
- capturar apenas resultado final aprovado: IP Tailscale, MagicDNS, URL HTTPS, tunnel label;
- guardar remote profile;
- guardar material sensível no Vault apenas se explicitamente pedido.

O God Mode não pode:

- escrever password automaticamente;
- contornar MFA;
- fazer scrape de páginas privadas da conta;
- guardar password da conta provider;
- mudar DNS/deploy/túnel pago sem aprovação.

## Tailscale

Uso recomendado para hoje.

Fluxo:

```txt
1. Abrir setup guiado.
2. Escolher Tailscale.
3. Abrir página oficial.
4. Criar/login manualmente.
5. Instalar Tailscale no PC e Android.
6. Aprovar ambos na mesma tailnet.
7. Copiar IP Tailscale ou MagicDNS do PC.
8. Colar no God Mode.
9. God Mode cria remote profile.
```

## Cloudflare Tunnel

Melhor para domínio/HTTPS estável no futuro.

## Ngrok

Bom para teste temporário.

## Manual HTTPS

Quando já existe URL HTTPS segura a apontar para o God Mode PC.

## Resultado final

O resultado alimenta:

```txt
/api/mobile-pc-pairing/create-remote-access-plan
/api/mobile-pc-pairing/connection-manifest
/app/connect-phone
```

## Segurança

O login é sempre feito no browser/app oficial do provider.
O God Mode guarda apenas o endpoint final ou referência do Vault aprovada.
