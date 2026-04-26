# Android WebView Shell

## Objetivo

Criar o primeiro APK Android real para o God Mode.

Este APK é um WebView shell simples e controlado que abre o backend local do PC na rota:

- `/app/apk-start`

## Projeto Android

Localização:

- `android-app/`

Ficheiros principais:

- `android-app/settings.gradle`
- `android-app/build.gradle`
- `android-app/app/build.gradle`
- `android-app/app/src/main/AndroidManifest.xml`
- `android-app/app/src/main/java/pt/andrevazao/godmode/MainActivity.java`
- `android-app/app/src/main/res/values/styles.xml`

## Workflow

- `.github/workflows/android-real-build-progressive.yml`

Artifact:

- `godmode-android-webview-apk`

Ficheiro APK:

- `GodModeMobile-debug.apk`

## Comportamento

O APK mostra:

- campo para URL base do PC;
- botão “Abrir”;
- botão “Teste” para testar `/health`;
- botões rápidos para Start, First Use, Chat, Readiness e Drill;
- WebView que carrega `base_url + rota`.

Valor por defeito:

- `http://127.0.0.1:8000`

Num telemóvel físico, deve ser alterado para o IP do PC, por exemplo:

- `http://192.168.1.50:8000`

## Diagnóstico de ligação

O botão “Teste” faz um pedido HTTP a:

- `base_url + /health`

Se o backend responder, o APK abre automaticamente:

- `/app/apk-start`

Se falhar, mostra uma mensagem para verificar:

- IP do PC;
- firewall;
- porta 8000;
- se o backend está aberto.

## Persistência local

O último URL base introduzido é guardado nas preferências Android.

Assim, o operador não precisa de escrever o IP do PC sempre que abrir o APK.

## Segurança

- `usesCleartextTraffic=true` é usado para permitir backend local HTTP durante teste controlado.
- Este APK é debug/primeiro teste, não release assinado final.
- Não introduzir tokens, passwords, cookies ou API keys no chat.

## Próximos passos futuros

- QR pairing para descobrir o PC automaticamente;
- diagnóstico de ligação mais profundo;
- assinatura release;
- pipeline release APK/AAB;
- ícone e branding final;
- modo kiosk/overlay no futuro, se necessário.
