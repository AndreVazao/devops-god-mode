# PC Phone Offline Autonomy Model

## Objetivo
Definir o comportamento operacional do sistema quando:
- o telefone fica offline mas o PC continua online
- o PC fica offline mas o telefone continua a receber ordens
- a ligação regressa e os dois lados precisam de reconciliar estado

## Regra principal
O PC é o executor principal.
O telefone é o cockpit principal.

Isto significa:
- se o PC estiver online, ele deve continuar o trabalho até terminar ou até surgir um bloqueio real
- se o telefone cair, o PC não deve parar por causa disso
- se o PC cair, o telefone deve guardar os pedidos em buffer até conseguir voltar a enviá-los ao PC
- quando a ligação regressar, o sistema deve reconciliar estado e continuar sem perder contexto

## Regras de continuidade
### 1. PC online, telefone offline
- o PC continua a trabalhar
- o PC só pergunta alguma coisa se faltar direção real
- o trabalho não deve voltar ao início
- o contexto ativo deve manter-se até conclusão ou bloqueio

### 2. Telefone online, PC offline
- o telefone continua a receber ordens do utilizador
- cada pedido fica guardado em buffer local
- os pedidos não se perdem
- quando o PC regressa, os pedidos passam para fila pronta para o PC executar

### 3. Ligação restaurada
- o sistema compara o estado do buffer do telefone com o estado ativo do PC
- pedidos pendentes passam a prontos para execução no PC
- o histórico recente fica preservado para evitar duplicações
- o fluxo continua a partir do ponto mais avançado possível

## Regra de autonomia
Depois de receber uma ordem clara, o PC deve:
- continuar o trabalho sozinho
- seguir as diretrizes já existentes na conversa alvo
- montar, adaptar, reaproveitar e consolidar o que for preciso
- só interromper para perguntar quando houver falta real de direção, conflito de decisão ou informação impossível de inferir com segurança

## Regra de perguntas
O sistema não deve fazer perguntas só por rotina.
Só deve perguntar quando acontecer uma destas situações:
- faltam credenciais ou acessos indispensáveis
- existem duas direções materialmente diferentes e o sistema não consegue inferir a correta
- há risco de destruir trabalho importante sem confirmação
- o objetivo final depende de uma escolha do utilizador que não está nas diretrizes já dadas

## Componentes do backend ligados a este modelo
- `offline_command_buffering`
- `remote_session_persistence`
- `continuous_remote_execution`
- `runtime_supervisor_guidance`
- `mobile_cockpit_command_surface`

## Estado pretendido
O estado pretendido da repo é:
- PC local-first como cérebro operacional real
- telefone como cockpit fino e resiliente
- continuidade de tarefas mesmo com falhas temporárias de ligação
- perguntas mínimas e apenas quando são realmente necessárias
