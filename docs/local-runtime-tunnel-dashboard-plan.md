# Local Runtime + Tunnel + Dashboard Plan

## Branch
- `feature/local-runtime-tunnel-dashboard`

## Objetivo
Preparar a próxima fase do God Mode para funcionar em dois modos sem mudar de arquitetura:
- agora: Render + telemóvel
- depois: PC local + dashboard local + telemóvel remoto

## Meta operacional
### Hoje
- cockpit principal no telemóvel
- backend principal em Render
- trabalho remoto a partir da rua

### Amanhã
- backend pesado no PC de casa
- dashboard local no PC para uso direto
- telemóvel continua a operar remotamente
- túnel privado/free para ligação externa quando necessário

## Blocos desta fase
### 1. Runtime local do backend
- preparar arranque local simples do backend no PC
- manter porta prevista `127.0.0.1:8787`
- documentar fluxo de arranque e healthcheck local

### 2. Dashboard local do PC
- manter shell mobile para controlo remoto
- preparar modo dashboard para uso direto no PC
- permitir a mesma API base com experiência diferente consoante o dispositivo

### 3. Presets e comutação
- Render
- PC local
- túnel privado/free
- manual

### 4. Acesso remoto do telemóvel
- telemóvel continua a ser cockpit remoto
- PC passa a fazer o trabalho pesado
- túnel fica como ponte quando o utilizador está fora

### 5. Integração futura com automação e IAs
- ambiente local deve ser a base para browser automation
- ambiente local deve facilitar comunicação com várias IAs e ferramentas auxiliares
- a arquitetura não deve depender permanentemente de Render

## Critérios de saída
- branch limpa
- docs claras
- base pronta para implementação local no futuro PC
- sem partir o modo Render atual
