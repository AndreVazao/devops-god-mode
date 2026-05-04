# Launcher/App Default Home Route

## Objetivo

A Phase 174 formaliza `/app/home` como rota canónica do cockpit visual do God Mode para:

- desktop launcher;
- browser;
- APK/WebView;
- manifests de onboarding.

## Rota canónica

```txt
/app/home
```

URL local padrão:

```txt
http://127.0.0.1:8000/app/home
```

## Compatibilidade

As rotas seguintes redirecionam para `/app/home`:

- `/app`
- `/desktop`
- `/mobile`
- `/home`
- `/app/mobile`
- `/app/apk-start`

`/app/apk-start` fica como compatibilidade para metadata antiga de build Android.

## Endpoints

- `GET/POST /api/app-entrypoint/status`
- `GET/POST /api/app-entrypoint/aliases`
- `GET/POST /api/app-entrypoint/manifest`
- `GET/POST /api/app-entrypoint/package`

## Desktop launcher

O desktop launcher deve usar:

```txt
shell_url = http://127.0.0.1:8000/app/home
```

A sequência esperada é:

```txt
start_backend → wait_for_health → open_app_home
```

## APK/WebView

O APK deve usar:

```txt
ENTRY_ROUTE = /app/home
```

Em telemóvel físico, o base URL deve ser o IP LAN do PC:

```txt
http://192.168.x.x:8000/app/home
```

## Segurança

Esta fase apenas define entrypoints e redirects.

Não adiciona ações destrutivas e não contorna gates server-side.
