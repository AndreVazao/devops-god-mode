# Autonomous Install Research Code

## Objetivo

A Phase 122 reforça o God Mode para trabalhar com mais autonomia até ao produto funcional.

Esta fase junta três capacidades:

1. Instalar/configurar ferramentas automaticamente quando o PC for adequado.
2. Preparar pesquisa pública/Web/Google e guardar notas úteis por projeto.
3. Criar contratos de código por linguagem para o God Mode saber gerar, validar e entregar ficheiros funcionais.

## Endpoints

- `GET/POST /api/autonomous-delivery/status`
- `GET/POST /api/autonomous-delivery/panel`
- `GET/POST /api/autonomous-delivery/policy`
- `POST /api/autonomous-delivery/auto-install-decision`
- `POST /api/autonomous-delivery/research-plan`
- `POST /api/autonomous-delivery/research-note`
- `POST /api/autonomous-delivery/code-contract`
- `POST /api/autonomous-delivery/run`
- `POST /api/autonomous-delivery/provider-score`
- `GET/POST /api/autonomous-delivery/latest`
- `GET/POST /api/autonomous-delivery/package`

## Auto-instalação

O God Mode pode decidir instalar/configurar ferramentas necessárias quando:

- a ferramenta é conhecida;
- existe pacote confiável no plano;
- o PC tem perfil adequado;
- a ferramenta é útil para o projeto;
- não há bloqueio de sistema, login, licença ou risco de sobrescrever dados.

Em PC fraco:

- instala apenas ferramentas leves;
- evita insistir em ferramentas pesadas;
- prefere GitHub Actions para builds pesados.

Em PC novo/forte:

- prepara toolchain mais completa;
- pode usar Android SDK/ADB local;
- pode usar IA local opcional se o PC aguentar.

## Logins

O operador faz login quando necessário.

Depois disso, o God Mode deve preferir reutilizar sessão existente do browser ou armazenamento seguro do sistema.

A memória não deve guardar dados sensíveis de acesso.

## Pesquisa Web/Google

O God Mode passa a conseguir preparar pesquisas por projeto para descobrir:

- documentação oficial;
- alterações de ferramentas/APIs;
- guias úteis;
- issues e exemplos no GitHub;
- informação pública de comunidades;
- novidades que gerem backlog ou upgrades.

Exemplo: se um jogo, framework ou serviço mudar, o God Mode pode criar plano de pesquisa, recolher notas úteis e transformar isso em backlog técnico.

## Providers

Providers previstos:

- ChatGPT: provider principal diário.
- DeepSeek: apoio forte em código.
- Claude: revisão de contexto grande.
- Gemini: multimodal/pesquisa.
- Google/Web: pesquisa pública.
- Local AI: rascunhos/offline quando disponível.

O endpoint `provider-score` permite o God Mode aprender quais providers concluem melhor cada tipo de trabalho.

## Contratos de código

O endpoint `code-contract` cria um contrato técnico por projeto e linguagem.

Inclui:

- objetivo;
- linguagem/stack;
- ficheiros alvo;
- comandos de validação;
- sequência de providers;
- definição de pronto.

Linguagens previstas:

- Python
- JavaScript
- TypeScript
- Kotlin
- Java
- PowerShell
- HTML/CSS
- SQL

## Delivery run

O endpoint `/api/autonomous-delivery/run` junta:

1. decisão de instalação;
2. plano de pesquisa;
3. contrato de código;
4. plano de continuação por provider;
5. próxima ação.

## Regra final

O God Mode deve ser automático no trabalho seguro:

- pesquisar;
- resumir;
- preparar código;
- gerar contratos;
- preparar ficheiros;
- guardar memória;
- preparar PR/build.

Só deve parar quando houver login, bloqueio real do sistema, risco de dados sensíveis ou ação destrutiva.