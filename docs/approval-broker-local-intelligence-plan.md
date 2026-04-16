# Approval Broker + Local Intelligence Plan

## Branch
- `feature/local-runtime-tunnel-dashboard`

## Objetivo
Preparar a fase em que o God Mode passa a usar o PC local como cérebro principal, com aprovações contextuais no telemóvel e base para inteligência evolutiva local.

## Princípio operacional
### Agora
- Render continua a servir para teste e uso remoto inicial
- telemóvel continua a ser o cockpit principal

### Depois
- PC local executa o trabalho pesado
- telemóvel aprova, comanda e acompanha remotamente
- túnel privado/free liga o telemóvel ao PC quando necessário

## Bloco 1 — Approval Broker
Criar uma camada que centraliza pedidos de aprovação.

### Cada pedido deve incluir
- `request_id`
- `source`
- `action_type`
- `risk_level`
- `summary`
- `details`
- `requires_manual_confirmation`
- `suggested_response`

### Respostas suportadas
- `OK`
- `ALTERA`
- `REJEITA`

### Comportamento esperado
- baixo risco: aprovação rápida
- médio risco: popup contextual curto
- alto risco: confirmação manual explícita

## Bloco 2 — Popup contextual remoto
Quando surgir ação sensível:
- o PC gera pedido de aprovação
- o telemóvel recebe card/popup com contexto
- o utilizador responde
- o PC executa só depois da aprovação

## Bloco 3 — Inteligência local incremental
No PC local, preparar base para:
- reconhecimento de erros recorrentes
- classificação de stacks e linguagens
- histórico de correções aprovadas
- sugestão de reconciliação entre repos
- apoio a merges complexos por etapas

## Bloco 4 — Browser orchestration local
No PC local:
- abrir browser controlado
- falar com IAs web quando necessário
- recolher resposta
- devolver resultado ao cockpit móvel
- sempre com regras de risco e aprovação

## Bloco 5 — Persistência local
Preparar armazenamento local para:
- fila de aprovações
- histórico de decisões
- padrões de erro
- contexto de sessões
- cache de prompts e respostas úteis

## Resultado esperado
- menos toques repetitivos
- aprovação sensível com contexto
- PC local como motor principal
- telemóvel como comando remoto
- base real para inteligência evolutiva sem dependência obrigatória de APIs pagas
