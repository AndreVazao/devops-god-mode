# Guided Provider Setup Wizard + Browser Assist Contract

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
/api/guided-provider-setup/browser-assist-contract
/api/guided-provider-setup/capture-result
/api/guided-provider-setup/dashboard
/api/guided-provider-setup/package
```

## Modo Deus controlado

O God Mode pode operar como copiloto local:

```txt
abre página oficial do provider
→ mantém página oficial local/visível ou em segundo plano
→ mostra popup limpo com só os campos necessários
→ Oner preenche no popup God Mode
→ campos sensíveis entram no Vault local encriptado
→ God Mode cria Browser Assist Contract
→ pede gate no Mobile Permission Relay
→ depois do gate, pode preencher a página oficial localmente
→ pausa em MFA/captcha/device approval/consentimento/plano/billing
→ captura endpoint/config final
→ cria remote profile
```

## O que pode fazer

- abrir a página oficial;
- mostrar passos e campos necessários;
- criar popup limpo God Mode;
- guardar campos sensíveis no Vault local;
- preencher formulário oficial a partir de vault_reference depois do gate;
- clicar em controlos seguros de próximo/continuar dentro do fluxo do provider;
- pausar quando aparece etapa humana/risco;
- capturar resultado final aprovado: IP Tailscale, MagicDNS, URL HTTPS, tunnel label;
- criar remote profile.

## Hard stops obrigatórios

O God Mode deve pausar e pedir input/approval quando aparecer:

- MFA;
- captcha;
- device approval;
- billing/plano pago;
- provider terms/consentimento;
- página inesperada;
- security warning.

## O que não pode fazer

- contornar MFA/captcha;
- aceitar plano pago sem aprovação;
- mudar DNS/deploy/túnel pago sem aprovação;
- guardar segredos no repo/memória normal;
- devolver valores raw do Vault na resposta;
- continuar em página inesperada sem gate.

## Tailscale

Uso recomendado para hoje.

Fluxo:

```txt
1. Abrir setup guiado.
2. Escolher Tailscale.
3. Abrir página oficial.
4. Preencher popup limpo God Mode.
5. Criar browser-assist-contract.
6. Aprovar no telemóvel.
7. God Mode preenche/avança localmente até hard stop.
8. Instalar Tailscale no PC e Android se necessário.
9. Aprovar ambos na mesma tailnet.
10. Copiar/capturar IP Tailscale ou MagicDNS do PC.
11. God Mode cria remote profile.
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

O Browser Assist é local, gated e auditável. O God Mode guarda campos sensíveis no Vault local encriptado e trabalha por referência. MFA/captcha/consentimento continuam humanos.
