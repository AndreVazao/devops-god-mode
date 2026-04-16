# Handsfree Local Tunnel — Next Phase Plan

## Branch
- `feature/handsfree-local-tunnel-next`

## Objetivo
Preparar a próxima evolução do God Mode para uso mais hands-free no telemóvel, com backend local no futuro PC e exposição opcional por túnel privado/free.

## Meta funcional
- menos cliques no mobile shell
- alternância clara entre modo `driving` e `assisted`
- backend local no PC como modo principal futuro
- URL de túnel privado/free como fallback remoto
- configuração simples e persistida no browser

## Blocos desta fase
### 1. Fonte de backend configurável
Adicionar UX para escolher entre:
- `Render`
- `PC local`
- `Túnel privado/free`
- `Manual`

### 2. Presets de endpoint
Valores previstos:
- Render: `https://devops-god-mode-backend.onrender.com`
- PC local: `http://127.0.0.1:8787`
- Shell local: `http://127.0.0.1:4173`
- túnel: valor definido pelo utilizador

### 3. Modo driving reforçado
- esconder campos menos usados por defeito
- destacar apenas 1 ação principal
- headline curta
- cards compactos
- manter botões `OK / ALTERA / REJEITA`

### 4. Modo assisted reforçado
- mostrar repo/path/branch/base branch
- manter visibilidade e lifecycle
- mostrar contexto de repos relacionadas

### 5. Preparação futura de voz
Ainda sem integração final de voz, mas a shell deve ficar pronta para:
- receber input único do utilizador
- executar pipeline
- devolver decisão curta

## Critérios de saída
- shell continua funcional no browser do telemóvel
- backend pode ser trocado entre Render/local/túnel
- driving e assisted continuam claros
- PR curta e limpa
- merge sem squash
