# Local First Runtime Enforcement Plan

## Branch
- `feature/localfirst`

## Objetivo
Fechar a transição para modo local-first removendo a camada de transição cloud do runtime principal e deixando o estado do sistema alinhado com PC como cérebro e mobile como cockpit.

## Meta funcional
- retirar a route e os artefactos temporários de transição cloud
- expor estado de sistema sem indicadores de cloud runtime central
- manter apenas sinais úteis para PC local, mobile cockpit e integrações realmente necessárias

## Âmbito desta fase
- remover `cloud_runtime_transition` do runtime principal
- remover docs, contracts, service, route e workflow desta transição temporária
- ajustar `/api/system/config` para modo local-first

## Nota
A cloud deixa de aparecer como camada operacional principal. O fluxo principal passa a assumir PC local e mobile cockpit como arquitetura base.
