# Mobile Approval Cockpit Plan

## Branch
- `feature/mobile-approval-cockpit`

## Objetivo
Ligar a fundação do approval broker ao cockpit móvel, para que o utilizador consiga ver e responder a aprovações pendentes no telemóvel.

## Meta funcional
- listar approvals pendentes no mobile shell
- mostrar contexto curto e claro
- permitir responder `OK`, `ALTERA`, `REJEITA`
- refletir o estado atualizado sem sair do cockpit
- manter compatibilidade com Render agora e PC local depois

## Blocos desta fase
### 1. Backend read/write already available
A fase anterior já deixou:
- fila local JSON
- endpoints para criar, listar, consultar e responder approvals

### 2. Mobile shell approval view
Adicionar ao cockpit móvel:
- secção de pendentes
- contador de approvals
- cards compactos com resumo, origem e risco

### 3. Quick response actions
Cada card deve permitir:
- `OK`
- `ALTERA`
- `REJEITA`
- nota opcional numa fase seguinte

### 4. Refresh and status
- atualizar lista sem recarregar a página
- mostrar vazio quando não houver pendentes
- mostrar feedback após resposta

## Critérios de saída
- approvals visíveis no telemóvel
- respostas rápidas funcionais
- smoke verde da fase
- branch limpa
