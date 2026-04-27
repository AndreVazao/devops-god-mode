# Android WebView Shell

## Objetivo

Criar o APK Android real do God Mode.

O APK é um WebView shell simples e controlado que abre o backend local do PC na Home principal:

- `/app/home`

`/app/apk-start` fica como fallback legado.

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
- botão “Auto” para procurar o backend automaticamente;
- botão “Home” para abrir `/app/home`;
- botão “Teste” para testar `/health`;
- botões rápidos para Home, Chat, OK/Aprovações, PC Autopilot, Start legado e First Use;
- WebView que carrega `base_url + rota`.

## Entrada principal

A Phase 81 muda a rota principal do APK para:

- `/app/home`

Assim, depois de pairing, auto discovery ou teste `/health`, o operador cai no God Mode Home Cockpit em vez de cockpits técnicos.

## Pairing por deep link

O APK recebe deep link:

- `godmode://pair?payload=...`

O Manifest tem intent filter para:

- scheme `godmode`;
- host `pair`;
- categorias `DEFAULT` e `BROWSABLE`.

Quando o APK recebe o deep link:

1. lê o parâmetro `payload`;
2. descodifica Base64 URL-safe;
3. interpreta JSON;
4. exige `type=god_mode_mobile_pairing`;
5. exige `contains_secret=false`;
6. valida que `base_url` começa por `http://` ou `https://`;
7. rejeita URL com marcadores sensíveis como `token=`, `password=`, `cookie=`, `api_key=`, `authorization=` ou `bearer`;
8. guarda `base_url` nas preferências Android;
9. testa `/health`;
10. se responder, abre `/app/home`.

## Auto discovery

Ao abrir, o APK tenta encontrar o backend automaticamente.

Ordem de tentativa:

1. último URL guardado;
2. `http://127.0.0.1:8000`;
3. `http://10.0.2.2:8000` para emulador;
4. gateway Wi-Fi;
5. IPs prováveis na subnet do Wi-Fi.

Cada candidato é validado com:

- `/health`

Se encontrar o backend:

- guarda o URL;
- preenche o campo;
- abre `/app/home`.

Se não encontrar:

- mostra mensagem clara;
- mantém fallback manual por URL.

## Valor por defeito

- `http://127.0.0.1:8000`

Num telemóvel físico, caso a descoberta automática falhe, deve ser usado o IP do PC, por exemplo:

- `http://192.168.1.50:8000`

## Diagnóstico de ligação

O botão “Teste” faz um pedido HTTP a:

- `base_url + /health`

Se o backend responder, o APK abre automaticamente:

- `/app/home`

Se falhar, mostra uma mensagem para verificar:

- IP do PC;
- firewall;
- porta 8000;
- se o backend está aberto.

## Persistência local

O último URL base encontrado, introduzido ou recebido por deep link é guardado nas preferências Android.

Assim, o operador não precisa de escrever o IP do PC sempre que abrir o APK.

## Segurança

- `usesCleartextTraffic=true` é usado para permitir backend local HTTP durante teste controlado.
- `ACCESS_WIFI_STATE` é usado para inferir gateway/subnet local.
- Deep link só aceita payload `contains_secret=false`.
- URLs com marcadores sensíveis são recusados.
- Este APK é debug/primeiro teste, não release assinado final.
- Não introduzir tokens, passwords, cookies ou API keys no chat.

## Próximos passos futuros

- leitura de QR dentro do APK com câmara;
- diagnóstico de ligação mais profundo;
- assinatura release;
- pipeline release APK/AAB;
- ícone e branding final;
- modo kiosk/overlay no futuro, se necessário.
