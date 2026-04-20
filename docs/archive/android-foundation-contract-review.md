# Android Foundation Contract Review

## Objetivo
Mapear os contracts Android que ainda existem na repo como foundations históricas e clarificar o seu papel atual.

## Contracts revistos
### `backend/contracts/android_mobile_build_profile.example.json`
Status atual:
- foundation histórica
- representa a fase inicial de APK placeholder
- não deve ser interpretado como pipeline Android final

### `backend/contracts/android_real_build_profile.example.json`
Status atual:
- foundation intermédia
- representa uma tentativa mais realista de APK/WebView packaging
- continua sem fechar o build Android real final

### `backend/contracts/android_runtime_shell_profile.example.json`
Status atual:
- foundation de shell/pairing Android
- ainda útil como referência de payload mobile
- não representa por si só a app Android final

## Regra operacional
Enquanto não existir uma camada Android real consolidada e ligada ao fluxo principal, estes contracts devem ser tratados como:
- referência histórica
- bridge documental para assets mobile
- foundation placeholder

## Próximo passo sugerido
Quando o build Android real existir, decidir um de dois caminhos:
1. migrar estes contracts para arquivo definitivo
2. substituir por contracts novos claramente ligados ao pipeline Android real
