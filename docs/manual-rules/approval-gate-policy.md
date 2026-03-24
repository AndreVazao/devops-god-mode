# Approval Gate Policy

## Decisão

O DevOps God Mode deve nascer já com capacidades completas de leitura, análise, planeamento e execução, mas **nenhuma alteração destrutiva ou persistente** pode ser aplicada sem aprovação explícita do owner.

## Política principal

Todas as ações de alteração devem passar por um popup/modal de aprovação com três opções:

- `OK`
- `ALTERA`
- `REJEITA`

## Significado operacional

### OK
- aprova o plano exatamente como apresentado;
- permite executar a ação;
- autoriza persistência da alteração.

### ALTERA
- não executa ainda;
- abre modo de revisão do plano/patch/comando;
- permite editar parâmetros, âmbito, ficheiros, estratégia ou prioridade.

### REJEITA
- cancela a execução;
- regista a rejeição;
- mantém apenas auditoria do plano proposto.

## Ações que DEVEM exigir aprovação

- criar branch;
- modificar ficheiros;
- abrir pull request;
- alterar workflows;
- alterar configs de deploy;
- alterar variáveis ou instruções de infra;
- executar rollback;
- aplicar patches automáticos;
- escrever documentação persistente;
- tocar em regras de ecossistema;
- ações multi-repo.

## Ações que NÃO precisam de aprovação

- leitura;
- inventário;
- auditoria;
- análise de logs;
- classificação de stack;
- deteção de risco;
- geração de plano de correção;
- preview de diff;
- preview de impacto.

## Fluxo padrão

1. scanner lê;
2. engine analisa;
3. engine propõe plano;
4. popup mostra impacto;
5. owner escolhe `OK`, `ALTERA` ou `REJEITA`;
6. só depois há execução.

## Requisitos do popup

O popup de aprovação deve mostrar no mínimo:

- sistema/repo alvo;
- tipo de ação;
- risco estimado;
- ficheiros afetados;
- resumo do diff;
- impacto em repos relacionadas;
- opção de rollback, quando aplicável.

## Modos de risco

### Baixo
- docs;
- refactors localizados;
- melhorias não destrutivas.

### Médio
- config;
- build pipeline;
- contratos entre módulos.

### Alto
- secrets;
- runtime público;
- múltiplas repos;
- produção;
- rollback/force updates.

## Regra absoluta

Mesmo com capacidades FULL, o DevOps God Mode opera em modo:

- `full_capability = true`
- `full_auto_execute = false`
- `owner_confirmation_required = true`

## Objetivo

Dar ao owner controlo total pelo telemóvel, sem limitar o poder do sistema e sem deixar alterações persistentes acontecerem sem consentimento explícito.
