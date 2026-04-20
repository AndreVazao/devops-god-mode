# Project Recovery Real Write Link Plan

## Branch
- `feature/recovery-link`

## Objetivo
Ligar a camada write-ready da recuperação à camada `real_local_write`, para o God Mode conseguir produzir payloads de escrita real a partir dos bundles recuperados.

## Meta funcional
- representar handoff de recovery para escrita real
- representar payloads de escrita por target
- expor pacote compatível com `real_local_write`
- expor próxima ação de handoff
- preparar a fase seguinte de execução de escrita local real

## Blocos desta fase
### 1. Recovery real write handoff contract
Representar:
- handoff_id
- recovery_project_id
- write_ready_bundle_id
- write_run_candidate_count
- handoff_status

### 2. Recovery real write target contract
Representar:
- handoff_target_id
- recovery_project_id
- write_target_path
- preview_payload_mode
- handoff_target_status

### 3. Services and routes
Criar backend para:
- devolver handoffs de recovery para escrita real
- devolver targets do handoff
- devolver pacote compatível com `real_local_write`
- devolver próxima ação de handoff

### 4. Scope
Nesta fase ainda não executa a escrita real no disco.
Fecha a ponte direta entre recuperação write-ready e a camada `real_local_write`.
