# Home Visual Shell

## Objetivo

A Phase 173 liga a Home/App Control Surface a uma interface visual real servida pelo backend.

Entrada principal:

```txt
/app/home
```

Entrada alternativa:

```txt
/api/home-visual-shell/page
```

A página carrega:

```txt
/api/home-control-surface/package
```

E renderiza:

- cards por módulo;
- semáforo por módulo;
- estado global;
- botões reais por endpoint;
- editor de payload para ações POST;
- confirmação quando `requires_confirmation=true`;
- layout responsivo para PC/APK/WebView.

## Endpoints

- `GET /app/home`
- `GET /api/home-visual-shell/page`
- `GET/POST /api/home-visual-shell/status`
- `GET/POST /api/home-visual-shell/package`

## Segurança

A página não inventa ações.

Ela renderiza apenas botões vindos do backend em `/api/home-control-surface/package`.

Ações de maior risco continuam dependentes dos gates próprios:

- confirmação visual;
- payload explícito;
- frase/gate do módulo original quando aplicável;
- validação server-side no endpoint real.

## Uso no desktop/APK

- Desktop launcher pode abrir `/app/home`.
- APK/WebView pode abrir `/app/home` quando conectado ao backend local/remoto.
- Browser normal também pode abrir a mesma página.

## Próxima evolução

- Persistir preferências visuais do Oner.
- Adicionar polling automático por módulo.
- Adicionar logs por botão.
- Ligar aos atalhos reais do launcher/APK se existirem no repo.
