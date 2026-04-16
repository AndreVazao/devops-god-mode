# Hybrid Local Runtime Plan

## Objetivo
Preparar o God Mode para funcionar em modo híbrido:
- **modo hands-free** quando o utilizador está a conduzir
- **modo assistido por botões** quando o utilizador está parado
- execução principal no **PC local**
- acesso pelo **telemóvel** através de browser/app shell
- possibilidade de exposição por **túnel privado/free** quando necessário

## Arquitetura alvo
### No PC
- backend FastAPI local do God Mode
- shell mobile/web servida localmente
- futuro módulo de voz local
- futuro módulo browser-assisted local

### No telemóvel
- acesso pelo browser/PWA
- cockpit simples com ações rápidas
- comandos por voz/texto
- fallback para botões `OK / ALTERA / REJEITA`

## Perfis de uso
### 1. Driving mode
- interface reduzida
- 1 campo de comando principal
- respostas curtas
- prioridade a ação única recomendada
- mínimo de cliques

### 2. Assisted mode
- cockpit completo
- cards compactos
- botões de aprovação
- detalhe técnico expandível

## Serviços locais previstos
- backend local: `http://127.0.0.1:8787`
- shell local estática: `http://127.0.0.1:4173`

## Estratégia de túnel
### Preferência
Usar um túnel privado/free no futuro PC para expor:
- backend local
- shell local

### Requisito
O túnel deve ser opcional. O sistema deve continuar funcional totalmente em LAN/local.

## Variáveis locais previstas
- `GOD_MODE_PROFILE=hybrid_local`
- `GOD_MODE_BACKEND_HOST=127.0.0.1`
- `GOD_MODE_BACKEND_PORT=8787`
- `GOD_MODE_SHELL_PORT=4173`
- `GOD_MODE_DRIVING_MODE_DEFAULT=true`
- `GOD_MODE_ASSISTED_MODE_AVAILABLE=true`
- `GOD_MODE_TUNNEL_ENABLED=false`
- `GOD_MODE_TUNNEL_BACKEND_URL=`
- `GOD_MODE_TUNNEL_SHELL_URL=`

## Ordem de execução futura no PC
1. arrancar backend local
2. arrancar shell local
3. opcionalmente abrir túnel privado
4. no telemóvel abrir URL local/túnel
5. usar modo driving ou assisted conforme contexto

## Próxima fase recomendada
- preparar scripts Windows locais
- preparar configuração local example
- preparar shell para escolher modo `driving` ou `assisted`
- preparar campo para URL do backend local/túnel
