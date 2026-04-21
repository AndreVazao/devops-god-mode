# Conversation to Repo Reconstruction Plan

## Branch
- `feature/conversation-to-repo-reconstruction`

## Objetivo
Preparar o God Mode para conseguir ler conversas antigas em IAs no browser local, extrair código útil e reconstruir uma repo nova de raiz com aprovação contextual.

## Meta funcional
- abrir conversa antiga no browser local
- fazer scroll incremental
- detetar blocos de código
- identificar linguagem e possível destino do ficheiro
- agrupar blocos relacionados
- reconstruir árvore de diretórios
- propor repo nova
- pedir aprovação antes de criar repo/branch/commit

## Pré-condições
- execução no PC local do utilizador
- browser automation local
- sessão autenticada pelo utilizador nas IAs alvo
- approval broker ativo para ações sensíveis

## Blocos desta fase
### 1. Conversation intake
Capturar contexto da conversa:
- origem
- título/conversa alvo
- mensagens relevantes
- blocos de código encontrados

### 2. Code extraction
Extrair e classificar:
- linguagem
- blocos duplicados
- blocos partidos em várias mensagens
- pistas de nomes de ficheiro

### 3. Repo reconstruction
Montar proposta de repo:
- árvore de diretórios
- ficheiros finais
- conflitos e versões alternativas
- ficheiros suspeitos ou incompletos

### 4. Approval checkpoint
Antes de criar repo:
- mostrar resumo
- mostrar riscos
- pedir `OK`, `ALTERA`, `REJEITA`

### 5. Git execution target
Depois da aprovação:
- criar repo nova ou branch nova
- escrever ficheiros
- criar commit inicial

## Critérios de saída
- plano claro
- contrato inicial para reconstrução
- base pronta para browser orchestration local futura
- alinhado com approval broker e cockpit móvel
