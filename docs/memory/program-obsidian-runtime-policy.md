# Program Obsidian Runtime Policy

## Decisão

O Obsidian local não tem o mesmo papel para todos os programas.

## Regra principal

- **God Mode** pode usar Obsidian como oficina técnica de desenvolvimento, orquestração, prompts, arquitetura, planeamento e memória operacional local.
- **Outros programas locais** podem usar Obsidian apenas para trabalho real, operação diária, observações, histórico legível por humanos e evolução de uso.
- **Programas cloud** não dependem de Obsidian local. Devem usar base de dados, storage ou cloud memory própria.

## God Mode

Pode usar Obsidian para:

- desenvolvimento local;
- prompts técnicos;
- preparação de sync para GitHub memory;
- arquitetura;
- planeamento;
- priorização;
- observações reais;
- orquestração dos outros sistemas.

## Programas locais

Exemplos: ProVentil local, VerbaForge local, Bot Lords Mobile local, ECU Repro local.

Podem usar Obsidian para:

- notas operacionais;
- histórico humano;
- observações de uso;
- evolução do comportamento;
- relatórios locais;
- contexto do utilizador.

Não devem usar Obsidian como:

- base de dados principal;
- fonte de licenças;
- fonte de pagamentos;
- armazenamento de dados críticos;
- ambiente de desenvolvimento próprio.

Dados críticos ficam na DB/pasta própria do programa.

## Programas cloud

Exemplos: Build Control Center cloud, dashboards web, serviços online.

Devem usar:

- PostgreSQL/SQLite/cloud DB;
- object storage;
- cloud logs;
- GitHub memory para programação;
- storage próprio do serviço.

Obsidian pode receber apenas resumos exportados pelo God Mode, se o operador quiser.

## Regra de promoção técnica

Se um programa local gerar informação útil para desenvolvimento, bug, feature, arquitetura ou código reutilizável:

1. a informação fica primeiro como nota operacional/local;
2. o God Mode filtra;
3. o God Mode decide se promove para GitHub memory;
4. se for código reutilizável, entra também no Reusable Code Registry.

## Segurança

- Não guardar credenciais no Obsidian.
- Não guardar dados críticos apenas em Markdown.
- Não deixar programas cloud dependerem de ficheiros locais.
- Não misturar memória de operação com memória técnica estável sem curadoria do God Mode.
