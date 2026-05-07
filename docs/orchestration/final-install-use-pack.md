# Final Install & Use Pack + APK Auto Endpoint Contract

## Objetivo

A Phase 210 fecha o pacote mínimo para primeiro uso real do God Mode:

- instalar/abrir Windows EXE;
- instalar APK;
- ligar APK ao PC por LAN sweep ou remoto;
- confirmar readiness;
- abrir Vault se necessário;
- iniciar Autopilot.

## Endpoint principal

```txt
/api/final-install-use/package
```

## Página visual

```txt
/app/install-use-now
/app/final-ready
```

## Endpoints

- `/api/final-install-use/status`
- `/api/final-install-use/readiness`
- `/api/final-install-use/apk-endpoint-contract`
- `/api/final-install-use/install-steps`
- `/api/final-install-use/start-now`
- `/api/final-install-use/package`

## Contrato APK

O APK deve:

1. tentar `last_working_endpoint` se existir;
2. se falhar, usar `/api/mobile-pc-pairing/connection-manifest`;
3. tentar LAN primeiro;
4. varrer `192.168.1.61` até `192.168.1.101`, com prioridade no `192.168.1.81`;
5. se LAN falhar, tentar endpoint remoto configurado;
6. guardar o primeiro endpoint funcional;
7. abrir `/app/mobile-permission-relay` por defeito.

## Rotas finais úteis

```txt
/app/install-use-now
/app/final-ready
/app/home
/app/connect-phone
/app/mobile-permission-relay
/app/today-ready
/app/god-mode-vault
/app/ia-operator-bridge
```

## Uso imediato

PC:

```txt
1. Download Windows EXE artifact.
2. Extrair ZIP.
3. Abrir GodModeDesktop.exe.
4. Ir a http://127.0.0.1:8000/app/install-use-now.
5. Confirmar readiness.
6. Ligar telemóvel em /app/connect-phone.
7. Start Now.
```

Telemóvel:

```txt
1. Instalar APK artifact.
2. Tentar http://192.168.1.81:8000/app/mobile-permission-relay.
3. Se falhar, usar sweep 192.168.1.61-101.
4. Para rua, usar Tailscale/Cloudflare/Ngrok/HTTPS remoto.
```

## Segurança

- Não abre portas do router automaticamente.
- Não publica HTTP inseguro na internet.
- Não guarda dados sensíveis em repo.
- Segredos ficam no Vault local.
- Merge/release/deploy continuam com aprovação.

## Estado final

Com esta fase merged e builds verdes, o God Mode fica pronto para instalar e usar no PC/telemóvel.
