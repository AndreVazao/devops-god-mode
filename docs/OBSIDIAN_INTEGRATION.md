# Obsidian Integration

## Objetivo

Usar o Obsidian como interface externa de leitura e edição da memória longa do God Mode.

## Vault

O vault chama-se `AndreOS` e fica em:

`memory/vault/AndreOS`

## Organização

- `00_INBOX`: entrada rápida de notas.
- `01_MEMORIA_NUCLEAR`: memória transversal.
- `02_PROJETOS`: memória por projeto.
- `03_CODIGO`: notas técnicas.
- `04_NEGOCIOS`: notas de negócio.
- `05_LOGS_IA`: logs de sessões IA.
- `99_ARQUIVO`: arquivo.

## Abrir notas no Obsidian

O backend gera links `obsidian://`.

Exemplo:

`GET /api/memory-core/obsidian/GOD_MODE/MEMORIA_MESTRE.md`

Retorna `open_uri` e `new_uri`.

## Criar notas

O Memory Core pode preparar URI de criação com `obsidian://new`, mas a gravação principal no repositório é feita por ficheiro Markdown para ser versionada no Git.

## Segurança

Não guardar segredos técnicos no vault. O Obsidian deve receber só memória operacional, decisões, arquitetura, backlog e histórico.

## Sincronização futura

Futuramente pode ser adicionado:

- indexação semântica;
- embeddings locais;
- vector database;
- busca por similaridade;
- sumarização automática de notas antigas.
