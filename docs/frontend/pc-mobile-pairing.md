# PC Mobile Pairing Center

## Cockpit

- `/app/pc-mobile-pairing`
- `/app/pairing`

## API

- `GET /api/pc-mobile-pairing/status`
- `GET /api/pc-mobile-pairing/package`
- `GET /api/pc-mobile-pairing/pairing`
- `GET /api/pc-mobile-pairing/dashboard`

## Objetivo

Facilitar a ligação APK → PC.

O APK deve tentar descobrir o PC automaticamente. Se a rede/firewall impedir a descoberta, o operador abre este cockpit no PC e copia o URL recomendado para o APK.

## O que mostra

- IPs candidatos do PC;
- URL base recomendado;
- URL `/health`;
- URL `/app/apk-start`;
- URL `/app/first-use`;
- URL do chat com cartões.

## Fluxo recomendado

1. Abrir o APK.
2. Carregar em `Auto`.
3. Se encontrar o PC, entra sozinho em `/app/apk-start`.
4. Se falhar, abrir `/app/pairing` no PC.
5. Copiar o URL recomendado.
6. Colar no APK e carregar em `Teste`.

## Segurança

Não introduzir tokens, passwords, cookies ou API keys no pairing, no chat ou em qualquer campo do God Mode.

Este pairing não guarda credenciais, tokens, cookies ou API keys.

Ele só mostra URLs locais do backend para facilitar a ligação do APK ao PC.

## Limites

Pode falhar se:

- firewall bloquear a porta 8000;
- PC e telemóvel estiverem em redes diferentes;
- o router isolar dispositivos;
- o backend não estiver a correr;
- a porta configurada não for 8000.
