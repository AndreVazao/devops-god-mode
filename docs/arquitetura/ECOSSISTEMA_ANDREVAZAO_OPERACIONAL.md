# Ecossistema AndreVazao — Camada Operacional do God Mode

Status: OFICIAL
Dono: André Vazão / God Mode
Fonte base: `docs/arquitetura/ECOSSISTEMA_ANDREVAZAO_GRUPOS_E_ARQUIVO.md`
Usado por: Project Organizer, Reusable Code Registry, Obsidian Sync, GitHub Memory, agentes IA, Build Center e Oner Core.

## Objetivo

Transformar o mapa dos 12 grupos oficiais numa regra operacional executável pelo God Mode.

O documento original define a visão humana e estratégica. Esta camada define como o God Mode deve agir.

## Regra-mãe

O God Mode não contém fisicamente todos os projetos. O God Mode conhece, indexa, classifica, controla, automatiza, audita e reaproveita os projetos.

## Tipos oficiais de execução

Todo projeto deve ser classificado como um destes tipos:

- `LOCAL`: corre principalmente no PC/local.
- `CLOUD`: corre principalmente online/cloud.
- `HIBRIDO`: tem parte local e parte cloud.
- `MOBILE`: APK/app móvel ou controlo por telemóvel.
- `ARQUIVO`: congelado, substituído, histórico ou ainda não validado.

## Tipos oficiais de licenciamento

Todo projeto/produto deve receber uma sugestão de licenciamento:

- `interno_apenas`
- `gratuito`
- `pessoal`
- `profissional`
- `por_cliente`
- `por_conta`
- `por_castelo`
- `por_modulo`
- `por_utilizador`
- `por_obra`
- `cloud_saas`
- `a_definir`

## Política de memória

### GitHub memory

Usar para:

- programação;
- arquitetura;
- decisões técnicas;
- PRs;
- builds;
- releases;
- reusable codes;
- estado técnico estável.

### Obsidian local

Usar para:

- operação real;
- evolução local;
- notas de uso;
- observações de teste;
- prioridades;
- oficina técnica apenas do God Mode.

### Regra especial

Programas cloud não dependem de Obsidian local para funcionar. Devem usar DB/storage/cloud memory própria.

## 12 grupos oficiais

1. `01_GOD_MODE_E_SUBSISTEMAS`
2. `02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO`
3. `03_MECANICA_ECUPROTUNE_SWAPAI_OUTROS`
4. `04_DESENHO_E_CONVERSOR_CNC`
5. `05_PROVENTIL_VIDEO_PORTEIRO_EXTRATORES_FUMOS`
6. `06_BOT_FACTORY_ENGENHARIA_REVERSA_PCFARM_BOTS_JOGO`
7. `07_BOTS_PROGRAMAS_E_EXCHANGE`
8. `08_MOBILE`
9. `09_ONER_CORE_E_CHAT_BOTS`
10. `10_SHEETPRO_E_PROGRAMAS_PESSOAIS`
11. `11_REUSABLE_CODES`
12. `12_ETC_INCUBADORA_FUTURA`

## Regras de decisão

### Projetos novos

Quando surgir uma ideia/projeto novo:

1. Classificar por grupo.
2. Classificar tipo de execução.
3. Classificar licenciamento provável.
4. Verificar se já existe repo.
5. Verificar se já existe código reutilizável.
6. Criar nota Obsidian se ainda estiver em evolução.
7. Criar memória GitHub se virar decisão técnica estável.

### Projetos antigos

Nenhum projeto antigo é apagado diretamente.

Fluxo obrigatório:

1. Analisar repo/conteúdo.
2. Separar código útil.
3. Registar em Reusable Code Registry.
4. Criar `.meta.md` quando for uma peça reutilizável.
5. Marcar como `ARQUIVADO`, `SUBSTITUIDO`, `NAO_VALIDADO` ou `REUTILIZAVEL`.
6. Só depois sugerir congelar, manter ou eliminar.

### Reusable Codes

Antes de pedir código novo a qualquer IA, o God Mode deve pesquisar primeiro:

- `/api/reusable-code-registry/search`
- `/api/ecosystem-map/reusable-decision`

Se existir componente compatível, deve adaptar/reutilizar antes de pedir código novo.

## Metadata obrigatória para peça reutilizável

```txt
Nome:
Projeto original:
Grupo original:
Grupo destino possível:
Linguagem:
Framework:
Estado:
Serve para:
Pode ser reutilizado em:
Riscos:
Dependências:
Como testar:
Última revisão:
Tipo execução:
Licenciamento provável:
```

## Integração esperada no God Mode

O God Mode deve expor:

- painel do ecossistema;
- lista dos grupos;
- classificação automática de projeto/repo;
- decisão de execução/licenciamento;
- decisão de reusable code;
- mapa de repos conhecidos;
- regras de arquivo;
- pacote para agentes IA.

## Estado desta camada

Esta camada foi operacionalizada na Phase 155 através dos endpoints `/api/ecosystem-map/*`.
