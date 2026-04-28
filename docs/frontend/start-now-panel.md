# Start Now Panel

## Objetivo

A Phase 99 cria um painel único para começar a usar o God Mode com menos cliques.

A Home passa a expor:

- `Começar agora`
- `/api/start-now/panel`

## Endpoints

- `GET /api/start-now/status`
- `GET /api/start-now/panel`
- `POST /api/start-now/panel`
- `GET /api/start-now/package`

## O que junta

O painel combina quatro blocos que já existem:

1. `Ligar ao PC`
2. `Instalação final`
3. `APK/EXE`
4. `Próxima ordem`

## Cartões

O painel devolve cartões com:

- título;
- endpoint;
- estado;
- resumo curto.

## Botões rápidos

- `Ligar ao PC`
- `Instalação final`
- `APK/EXE`
- `Próxima ordem`
- `Home`

## Critério de aceitação

A validação confirma:

- rotas `/api/start-now/*`;
- Home com ação `Começar agora`;
- painel com quatro cartões;
- botões rápidos;
- documentação;
- Project Tree Autorefresh.
