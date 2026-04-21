# Local Runtime Dominance Phase Plan

## Branch
- `feature/local-runtime-dominance`

## Objetivo
Adicionar uma camada de dominância do runtime local para o God Mode conseguir declarar o PC como runtime principal efetivo, deixar o APK como cockpit remoto e rebaixar Vercel, Render e Supabase a suporte opcional sem partir compatibilidade.

## Meta funcional
- representar runtime surfaces dominantes
- representar ações de dominância local por área
- expor pacote compacto pronto para cockpit mobile
- expor próxima ação prioritária de dominância local
- preparar a fase seguinte de runtime local real e canal remoto estável

## Blocos desta fase
### 1. Local runtime dominance contract
Representar:
- local_runtime_dominance_id
- dominant_runtime
- remote_client_mode
- support_cloud_mode
- dominance_status

### 2. Local runtime action contract
Representar:
- local_runtime_action_id
- runtime_area
- action_type
- action_label
- execution_path
- action_status

### 3. Services and routes
Criar backend para:
- devolver runtime surfaces dominantes
- devolver ações de runtime local
- devolver pacote compacto pronto para cockpit
- devolver próxima ação prioritária

### 4. UX note
O utilizador deve sentir que o APK só fala com o PC. A cloud não desaparece, mas deixa de parecer o centro do sistema.

### 5. Workflow de fase
Criar workflow temporário desta fase.
Na fase seguinte, este workflow deverá ser apagado conforme a policy da repo.
