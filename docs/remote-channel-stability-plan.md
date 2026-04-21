# Remote Channel Stability Phase Plan

## Branch
- `feature/remote-channel-stability`

## Objetivo
Adicionar uma camada de estabilidade do canal remoto para o God Mode conseguir manter ligação fiável entre APK e PC, suportar pedidos curtos, estados compactos e confirmações rápidas mesmo quando a rede oscila.

## Meta funcional
- representar canais remotos estáveis
- representar ações de robustez do canal
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de estabilidade
- preparar a fase seguinte de sessão remota persistente

## Blocos desta fase
### 1. Remote channel stability contract
Representar:
- remote_channel_id
- channel_mode
- transport_role
- resilience_profile
- channel_status

### 2. Remote channel action contract
Representar:
- remote_channel_action_id
- channel_area
- action_type
- action_label
- fallback_mode
- action_status

### 3. Services and routes
Criar backend para:
- devolver canais remotos estáveis
- devolver ações de robustez
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador não deve sentir ruído técnico. O APK envia, recebe e confirma. O canal entre APK e PC deve parecer simples e sólido.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
