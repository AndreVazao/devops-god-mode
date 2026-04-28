# Pro Operator Bridge

## Objetivo

A Phase 101 adiciona o `Operador Pro`: uma camada que recebe uma ordem em linguagem normal, classifica intenção/risco, escolhe a rota segura e decide se pode executar ou se deve devolver plano para revisão.

## Endpoints

- `GET /api/pro-operator/status`
- `GET /api/pro-operator/panel`
- `POST /api/pro-operator/analyze`
- `POST /api/pro-operator/run`
- `GET /api/pro-operator/package`

## Ligação à Home

A Home passa a mostrar:

- `Operador Pro`
- `/api/pro-operator/panel`

## Como funciona

1. Recebe texto curto do operador.
2. Usa IA local opcional para classificação.
3. Usa fallback determinístico se a IA local estiver offline.
4. Escolhe rota:
   - Começar agora;
   - Score profissional;
   - IA local;
   - APK/EXE;
   - instalação;
   - saúde;
   - blockers;
   - resumo;
   - continuar projeto ativo.
5. Calcula risco.
6. Só executa automaticamente quando o risco e o score profissional permitem.

## Regras

- Risco alto não executa direto.
- Ações destrutivas ficam em revisão.
- IA local é opcional.
- O backend continua funcional sem IA local.
- A prioridade continua a vir do operador.

## Exemplos rápidos

- `começar agora`
- `mostra APK e EXE`
- `mostra o score profissional`
- `ver IA local`
- `corrige blockers do God Mode`
- `dá resumo e próximo passo`

## Benefício prático

O operador pode escrever uma frase normal no telemóvel. O God Mode traduz para uma ação segura e usa a arquitetura já existente em vez de inventar caminhos paralelos.
