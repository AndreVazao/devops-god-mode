# Ecossistema AndreVazao — Grupos Oficiais, Subprogramas e Reusable Codes

Este documento define a divisão oficial dos projetos do ecossistema AndreVazao.

A regra principal mantém-se:

- O **God Mode** é o orquestrador central.
- Os grupos são famílias de produto/negócio.
- Os projetos antigos que não avançarem não devem ser apagados sem análise.
- Scripts, dashboards, APIs, bases de dados, prompts, automações e instaladores úteis devem ser enviados para **Reusable Codes**.
- O arquivo deve ser legível por humanos, pelo Obsidian e por agentes IA do God Mode.

---

# Mapa oficial dos grupos

```txt
ECOSSISTEMA_ANDREVAZAO/
├── 01_GOD_MODE_E_SUBSISTEMAS/
├── 02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO/
├── 03_MECANICA_ECUPROTUNE_SWAPAI_OUTROS/
├── 04_DESENHO_E_CONVERSOR_CNC/
├── 05_PROVENTIL_VIDEO_PORTEIRO_EXTRATORES_FUMOS/
├── 06_BOT_FACTORY_ENGENHARIA_REVERSA_PCFARM_BOTS_JOGO/
├── 07_BOTS_PROGRAMAS_E_EXCHANGE/
├── 08_MOBILE/
├── 09_ONER_CORE_E_CHAT_BOTS/
├── 10_SHEETPRO_E_PROGRAMAS_PESSOAIS/
├── 11_REUSABLE_CODES/
└── 12_ETC_INCUBADORA_FUTURA/
```

---

# 01 — God Mode e subsistemas

O God Mode é o cérebro e orquestrador de todo o ecossistema.

Ele não deve conter fisicamente todos os projetos dentro dele. Deve conhecer, indexar, controlar, automatizar e reaproveitar tudo.

## Projetos e subsistemas

- God Mode
- DevOps God Mode
- AI DevOps Control Center
- Universal Build Platform
- Build Control Center
- Build Control Panel
- GitHub Auto Builder
- Project Organizer AI
- ENV Editor
- Vortexa Core
- AndreOS Memory
- Obsidian + IA Memory
- Sistema de memória persistente
- Sistema de gestão de repositórios
- Sistema de automação GitHub
- Sistema de builds automáticos
- Sistema de dashboards de estado
- Sistema de agentes IA internos
- Sistema de leitura e catalogação de projetos
- Sistema de integração com Reusable Codes

## Função do grupo

```txt
GodMode/
├── 00_CORE_ORQUESTRADOR/
├── 01_MEMORIA_OBSIDIAN/
├── 02_GITHUB_AUTOMATION/
├── 03_BUILD_CENTER/
├── 04_AGENTES_IA/
├── 05_REUSABLE_CODES_INDEX/
├── 06_DEPLOY_E_PACKAGING/
├── 07_PROJECT_ORGANIZER/
├── 08_MOBILE_CONTROL/
└── 09_AUDITORIA_DECISOES/
```

## Regra

O God Mode deve conseguir perguntar:

```txt
Tenho código antigo útil para resolver isto?
Existe script arquivado semelhante?
Existe dashboard, API, base de dados ou instalador reaproveitável?
Qual repo contém a melhor versão deste módulo?
```

---

# 02 — Baribudos Studio e criadores de conteúdo

Grupo para conteúdo, websites, vídeos, ebooks, cursos, vozes, personagens, lipsync, tradução e publicação automática.

## Projetos e subprogramas

- Baribudos Studio
- Baribudos Studio Primary
- Baribudos Studio Home Edition
- Baribudos Studio Website
- Website Baribudos Studio
- VerbaForge
- ViralVazao
- Criadores de conteúdo
- Content Creator / Contentoria Heitor
- Sistema de personagens/personas
- Sistema de vozes fixas
- Coqui TTS / XTTS-v2
- Voice cloning
- Translation + Lipsync Lab
- Tradutor de vídeo
- Sistema de dobragem automática
- Sistema de legendagem
- Sistema de lipsync
- Gerador de ebooks
- Gerador de vídeos
- Gerador de cursos
- Gerador de posts
- Sistema de tendências virais
- Sistema de autopublicação
- Sistema de patrocinadores/anúncios em conteúdos

## Estrutura sugerida

```txt
BaribudosStudioConteudo/
├── 00_BRAND_WEBSITE/
├── 01_BARIBUDOS_UNIVERSE/
│   ├── historias/
│   ├── personagens/
│   ├── vozes/
│   ├── ilustracoes/
│   └── videos/
├── 02_VERBAFORGE/
│   ├── ebooks/
│   ├── cursos/
│   ├── videos/
│   └── publicador-redes/
├── 03_CRIADORES_CONTEUDO/
│   ├── personas/
│   ├── canais/
│   ├── campanhas/
│   └── monetizacao/
├── 04_TRANSLATION_LIPSYNC/
│   ├── tradutor-video/
│   ├── dobragem/
│   ├── legendas/
│   └── lipsync/
├── 05_VOZES_TTS/
│   ├── coqui-xtts/
│   ├── voice-cloning/
│   ├── narradores/
│   └── personagens-recorrentes/
└── 99_ARQUIVO_CONTEUDO/
```

---

# 03 — Mecânica: EcuProTune, SwapAI e outros

Grupo para diagnóstico automóvel, ECU, reprogramação, swaps de motores, engenharia de suportes, peças e futuros sistemas de oficina.

## Projetos e subprogramas

- ECU Pro Tune
- EcuProTune
- Diagnóstico OBD2
- Reprogramação ECU
- Konnwei ELM327 v1.5
- Sistema de backup automático da ECU
- Sistema de presets de performance
- Sistema de limites seguros
- Sistema de relatório de anomalias
- Sistema de assinatura/aceitação do cliente
- SwapAI
- Swap Engine Designer
- Desenho de apoios de motor
- Sistema para trocas de motores
- Sistema de compatibilidade motor/chassis
- Sistema de desenho de adaptadores
- Sistema CAD automóvel
- Sistema de medição por fotos/scans
- Sistema futuro de drone/scanner/fotogrametria
- Outros projetos futuros de mecânica

## Estrutura sugerida

```txt
Mecanica/
├── 00_ECUPROTUNE/
│   ├── diagnostico-obd2/
│   ├── reprogramacao-ecu/
│   ├── backups-originais/
│   ├── presets-performance/
│   ├── limites-seguros/
│   └── relatorios-cliente/
├── 01_SWAPAI/
│   ├── motor-mount-designer/
│   ├── apoios-motor/
│   ├── adaptadores/
│   ├── compatibilidade-motor-chassis/
│   └── calculos-tecnicos/
├── 02_CAD_AUTOMOVEL/
│   ├── pecas/
│   ├── suportes/
│   ├── chapas/
│   └── export-dxf-step-stl/
├── 03_SCAN_DRONE_MEDICOES/
│   ├── fotogrametria/
│   ├── scans-3d/
│   └── referencias-medidas/
└── 99_ARQUIVO_MECANICA/
```

## Regra de segurança

Qualquer sistema ECU ou alteração mecânica deve guardar:

- backup original;
- relatório de alterações;
- limites mínimos e máximos;
- consentimento do cliente;
- separação clara entre diagnóstico e alteração.

---

# 04 — Desenho e conversor CNC

Grupo para desenho técnico, CNC, laser, DXF, GCode e conversores de ficheiros para máquinas.

## Projetos e subprogramas

- GCode Converter
- Conversor SVG para GCode
- Conversor DXF para GCode
- Conversor PNG/JPG/BMP para GCode
- Conversor PDF para GCode
- Conversor TXT para GCode
- Sistema de preview CNC
- Sistema laser/engraver
- Sistema para impressora 2D/3D
- Sistema de escala automática
- Sistema de retração Z entre caracteres
- OpenCV contour detection
- DXF Generator
- Gerador DXF para botoneiras
- Gerador DXF para chapas ProVentil
- Gerador DXF para apoios de motor/SwapAI
- Gerador de ficheiros para corte laser/vinil
- Sistema de camadas CUT_OUTER, CUT_INNER, ENGRAVE, MARK_TEXT, BEND_REF

## Estrutura sugerida

```txt
DesenhoCNC/
├── 00_DESENHO_TECNICO/
│   ├── templates/
│   ├── medidas/
│   ├── bibliotecas/
│   └── validadores/
├── 01_GCODE_CONVERTER/
│   ├── svg-to-gcode/
│   ├── dxf-to-gcode/
│   ├── image-to-gcode/
│   ├── pdf-to-gcode/
│   └── txt-to-gcode/
├── 02_DXF_GENERATORS/
│   ├── botoneiras/
│   ├── chapas/
│   ├── apoios-motor/
│   ├── suportes/
│   └── templates/
├── 03_CNC_LASER_PREVIEW/
│   ├── preview-2d/
│   ├── simulador-caminho/
│   └── configuracoes-maquina/
├── 04_EXPORTADORES/
│   ├── gcode/
│   ├── dxf/
│   ├── svg/
│   ├── stl/
│   └── step/
└── 99_ARQUIVO_DESENHO_CNC/
```

## Relações com outros grupos

Este grupo serve diretamente:

- ProVentil, para chapas, botoneiras e peças;
- Mecânica/SwapAI, para apoios de motor e adaptadores;
- Baribudos/Conteúdo, para produtos físicos, brindes, placas e merchandising.

---

# 05 — ProVentil: videoporteiro, extratores de fumos e outros

Grupo do negócio real de instalação, orçamento, manutenção e gestão técnica.

## Projetos e subprogramas

- ProVentil
- proventil.pt
- Sistema videoporteiro
- Sistema Comelit
- Sistema Fermax
- Sistema BTicino
- Sistema de botoneiras
- Sistema de chapas para botoneiras
- Sistema de extração de fumos para restaurantes/hotelaria
- Extratores de fumos
- Motores
- Tubos
- Curvas
- Filtros
- Filtros eletrostáticos
- Carvão ativado
- Juntas flexíveis
- Sistema de propostas por marca
- Sistema de orçamentos automáticos
- Sistema de deslocações por distância
- Sistema de fornecedores
- Sistema ClimaStore
- Sistema de ID por obra/morada
- Histórico técnico por edifício
- Sistema de faltosos/revisitas
- Sistema de stock
- Sistema de comissões técnicas
- Outros futuros serviços ProVentil

## Estrutura sugerida

```txt
ProVentil/
├── 00_CORE_NEGOCIO/
├── 01_CLIENTES_OBRAS_MORADAS/
├── 02_ORCAMENTOS_PROPOSTAS/
├── 03_VIDEO_PORTEIROS/
│   ├── comelit/
│   ├── fermax/
│   ├── bticino/
│   ├── botoneiras/
│   └── chapas/
├── 04_EXTRACAO_FUMOS_RESTAURANTES/
│   ├── motores/
│   ├── tubos/
│   ├── curvas/
│   ├── filtros/
│   ├── eletrostaticos/
│   ├── carvao-ativado/
│   └── fornecedores/
├── 05_DESLOCACOES_TECNICOS/
├── 06_DXF_CHAPAS_BOTONEIRAS/
├── 07_STOCK_FORNECEDORES/
├── 08_COMISSOES/
└── 99_ARQUIVO_PROVENTIL/
```

---

# 06 — Bot Factory, engenharia reversa, PcFarm e bots de jogo

Grupo para criar bots de jogos, estudar comportamento, automatizar jogos e gerir farms.

## Projetos e subprogramas

- Bot Factory
- Engenharia Reversa Framework
- Reverse Engineering Agents
- BOT_<nome_do_jogo>
- PC Farm Lords Mobile
- PcFarm
- Headless Lords Mobile Bot
- Bot Lords Mobile
- Bot Guerra
- Bot Guild
- Bot Rally
- Bot Darknest/DN
- Sistema OCR validate first
- Sistema de aprendizagem entre instâncias
- Sistema de clones do jogo PC
- Sistema de comandos por chat
- Sistema de permissões por castelo
- Sistema de dashboard de instâncias
- Sistema de semáforo por castelo
- Sistema dos 3 bonecos de estado
- Bot APK
- Bots Android para jogos
- Bots PC para jogos

## Estrutura sugerida

```txt
BotFactoryJogos/
├── 00_BOT_FACTORY/
├── 01_ENGENHARIA_REVERSA/
├── 02_FRAMEWORK_BOT_GENERATOR/
├── 03_LORDS_MOBILE_PCFARM/
│   ├── pc-farm/
│   ├── headless-real/
│   ├── emulator-fallback/
│   ├── comandos-chat/
│   ├── rally-dn-war/
│   └── dashboard-instancias/
├── 04_BOTS_ANDROID_JOGOS/
├── 05_BOTS_PC_JOGOS/
├── 06_LICENCAS_BOTS_JOGOS/
└── 99_ARQUIVO_BOTS_JOGOS/
```

---

# 07 — Bots programas e de exchange

Grupo para bots que não são de jogos: bots de programas, automações de trabalho, assistentes, integrações, bots de exchange/trading e futuros bots de operação digital.

## Projetos e subprogramas

- Bots de programas
- Bots de automação de software
- Bots de produtividade
- Bots de scraping legal/permitido
- Bots de monitorização
- Bots de exchange
- Bots de trading por API oficial
- Bots de alertas de preço
- Bots de gestão de carteira
- Bots de arbitragem apenas se for legal e via APIs permitidas
- Bots de relatórios financeiros
- Bots de marketplaces
- Bots de resposta automática
- Bots de atendimento
- Bots futuros não relacionados com jogos

## Estrutura sugerida

```txt
BotsProgramasExchange/
├── 00_BOTS_PROGRAMAS/
│   ├── produtividade/
│   ├── scraping-permitido/
│   ├── monitorizacao/
│   └── automacoes-desktop-web/
├── 01_BOTS_EXCHANGE/
│   ├── api-connectors/
│   ├── price-alerts/
│   ├── portfolio-manager/
│   ├── trading-strategies/
│   └── reports/
├── 02_BOTS_ATENDIMENTO/
├── 03_BOTS_MARKETPLACES/
├── 04_BOTS_FINANCEIROS/
└── 99_ARQUIVO_BOTS_PROGRAMAS_EXCHANGE/
```

## Regra

Bots de exchange/trading devem trabalhar apenas com APIs oficiais, chaves protegidas, logs, limites de risco, modo simulação e confirmação antes de operações reais.

---

# 08 — Mobile

Grupo para apps Android, overlays, controlo pelo telemóvel, automações mobile e sistemas operativos/ambientes móveis.

## Projetos e subprogramas

- Script Reviewer Mobile
- App Android com botões flutuantes
- Overlay sobre outras apps
- Sistema para falar com várias IAs em simultâneo
- Sistema para criar/alterar repos pelo telemóvel
- Sistema Expo/Android com permissões de overlay
- AndreOS
- OS Universal para Telemóveis
- Sistema operativo ultra-leve para jogos
- Instalador PC que prepara telemóvel
- Sistema de deteção automática de hardware
- Sistema de drivers
- Sistema controlado por ADB
- Apps APK futuras dos outros grupos

## Estrutura sugerida

```txt
Mobile/
├── 00_SCRIPT_REVIEWER_MOBILE/
├── 01_FLOATING_OVERLAY_AI/
├── 02_ANDROID_AUTOMATION/
├── 03_ANDREOS/
├── 04_ADB_CONTROL/
├── 05_APKS_PRODUTOS/
└── 99_ARQUIVO_MOBILE/
```

---

# 09 — Oner Core e chat bots

Grupo transversal para administração, licenças, utilizadores, pagamentos, permissões, chatbots e controlo interno.

## Projetos e subprogramas

- Oner Core
- Painel Oner
- Back-end unificado
- Base de dados unificada
- Sistema de utilizadores
- Sistema de pagamentos
- Sistema de licenças por programa
- Sistema de permissões por checkbox
- Sistema de pacotes/preços
- Sistema de upsell por IA
- Sistema de admins/empregados
- Sistema de comissões
- Sistema de bónus
- Sistema de auditoria
- Chatbot privado do Oner
- Chatbots de cliente
- Chatbots de suporte
- Chatbots internos por projeto
- Sistema de aprovação por botão aceitar

## Estrutura sugerida

```txt
OnerCoreChatBots/
├── 00_CORE_ADMIN/
├── 01_AUTH_USERS/
├── 02_LICENCAS/
├── 03_PAGAMENTOS/
├── 04_PLANOS_PRECOS/
├── 05_PERMISSOES_CHECKBOXES/
├── 06_ADMIN_EMPREGADOS/
├── 07_COMISSOES_BONUS/
├── 08_CHATBOTS/
│   ├── oner-private-ai/
│   ├── suporte-clientes/
│   ├── chatbots-projetos/
│   └── agentes-internos/
├── 09_AUDITORIA_APROVACOES/
└── 99_ARQUIVO_ONER_CORE/
```

---

# 10 — SheetPro e outros programas pessoais

Grupo para ferramentas pessoais, análise de PDFs, escalas, chapas, organização, utilitários e programas que servem a vida diária/trabalho interno.

## Projetos e subprogramas

- SheetProPrivate
- SheetPro
- Programa para verificar escalas
- Sistema de análise de chapas
- Sistema de análise de PDFs de serviços
- Sistema de base de dados de rotas
- Sistema de atualização de chapas
- Sistema horário verão/inverno
- Sistema horário escolar/não escolar
- Sistema de deteção de novas rotas
- Sistema de comparação de alterações
- Programas pessoais futuros
- Utilitários locais
- Ferramentas internas pequenas

## Estrutura sugerida

```txt
SheetProProgramasPessoais/
├── 00_SHEETPRO/
│   ├── importador-pdfs/
│   ├── analisador-chapas/
│   ├── base-rotas-servicos/
│   ├── comparador-alteracoes/
│   └── validador-escalas/
├── 01_UTILITARIOS_PESSOAIS/
├── 02_AUTOMACOES_LOCAIS/
├── 03_ORGANIZADORES/
└── 99_ARQUIVO_PESSOAL/
```

---

# 11 — Reusable Codes

Grupo especial para guardar código reaproveitável de todos os projetos.

Este grupo não é cemitério morto. É uma biblioteca de peças úteis.

## O que entra aqui

- scripts completos;
- funções úteis;
- componentes UI;
- dashboards;
- instaladores;
- GitHub Actions;
- configs;
- esquemas de base de dados;
- migrações;
- prompts;
- agentes;
- integrações;
- conversores;
- módulos mobile;
- lógica de licenças;
- código abandonado mas útil;
- experiências que podem ser adaptadas.

## Estrutura oficial

```txt
ReusableCodes/
├── 00_INDEX/
│   ├── catalogo-geral.md
│   ├── mapa-repos.md
│   ├── tags.md
│   └── decisoes.md
├── 01_COMPONENTES_UI/
│   ├── dashboards/
│   ├── botoes/
│   ├── tabelas/
│   ├── overlays/
│   └── temas-dark/
├── 02_BACKEND/
│   ├── fastapi/
│   ├── flask/
│   ├── workers/
│   ├── schedulers/
│   └── auth/
├── 03_DATABASE/
│   ├── sqlite/
│   ├── postgresql/
│   ├── migrations/
│   └── schemas/
├── 04_AUTOMACOES/
│   ├── github/
│   ├── android/
│   ├── adb/
│   ├── windows/
│   └── builds/
├── 05_AI_AGENTS/
│   ├── prompts/
│   ├── ferramentas/
│   ├── memoria/
│   └── decisores/
├── 06_CONVERSORES/
│   ├── gcode/
│   ├── dxf/
│   ├── pdf/
│   ├── imagem/
│   └── audio-video/
├── 07_MOBILE/
│   ├── android/
│   ├── expo/
│   ├── kotlin/
│   └── overlays/
├── 08_PACKAGING/
│   ├── pyinstaller/
│   ├── installers/
│   ├── github-actions/
│   └── releases/
├── 09_NEGOCIO/
│   ├── licencas/
│   ├── pagamentos/
│   ├── comissoes/
│   └── propostas/
├── 10_MECANICA_CNC/
│   ├── ecu/
│   ├── swapai/
│   ├── dxf/
│   └── gcode/
└── 99_CEMITERIO_CONTROLADO/
    ├── projetos-parados/
    ├── ideias-congeladas/
    ├── experiencias/
    └── codigo-nao-validado/
```

## Metadata obrigatória por peça guardada

Cada ficheiro reaproveitável deve ter um `.meta.md` ao lado:

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
```

## Estados possíveis

```txt
ATIVO
REUTILIZAVEL
ARQUIVADO_UTIL
EXPERIENCIA
SUBSTITUIDO
NAO_VALIDADO
PERIGOSO_NAO_USAR_SEM_REVISAO
```

---

# 12 — ETC / Incubadora futura

Grupo para ideias novas que ainda não têm família clara.

Nada deve ficar perdido em conversas soltas. Quando surgir uma ideia nova, entra primeiro aqui. Depois o God Mode decide se vira projeto próprio, subprograma ou peça para Reusable Codes.

## Estrutura sugerida

```txt
EtcIncubadora/
├── 00_IDEIAS_NOVAS/
├── 01_TESTES_RAPIDOS/
├── 02_PROMPTS_SOLTOS/
├── 03_PROVAS_CONCEITO/
├── 04_PROJETOS_SEM_GRUPO/
└── 99_ARQUIVO_INCUBADORA/
```

## Regra

A incubadora não é para guardar código final. Código útil sai daqui e vai para:

```txt
ReusableCodes/
```

Projetos que ganham força saem daqui e vão para um dos grupos oficiais.

---

# Repositórios GitHub conhecidos e grupo sugerido

```txt
AndreVazao/devops-god-mode                 -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/ai-devops-control-center        -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/universal-build-platform        -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/build-control-center            -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/build-control-panel             -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/GitHub-auto-builder             -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/Project-Organizer-AI            -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/ENV-editor                      -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/Vortexa-core                    -> 01_GOD_MODE_E_SUBSISTEMAS
AndreVazao/andreos-memory                  -> 01_GOD_MODE_E_SUBSISTEMAS

AndreVazao/baribudos-studio                -> 02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO
AndreVazao/baribudos-studio-primary        -> 02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO
AndreVazao/baribudos-studio-home-edition   -> 02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO
AndreVazao/baribudos-studio-website        -> 02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO

AndreVazao/ecu-pro-tune                    -> 03_MECANICA_ECUPROTUNE_SWAPAI_OUTROS

AndreVazao/proventil                       -> 05_PROVENTIL_VIDEO_PORTEIRO_EXTRATORES_FUMOS

AndreVazao/Bot_Factory                     -> 06_BOT_FACTORY_ENGENHARIA_REVERSA_PCFARM_BOTS_JOGO

AndreVazao/script-reviewer-mobile          -> 08_MOBILE

AndreVazao/SheetProPrivate                 -> 10_SHEETPRO_E_PROGRAMAS_PESSOAIS
```

---

# Política de eliminação e aproveitamento

Nenhum projeto antigo deve ser apagado diretamente.

Fluxo correto:

```txt
1. Identificar projeto antigo.
2. Analisar scripts, configs, prompts, DBs e UI.
3. Separar o que é útil.
4. Guardar em ReusableCodes com metadata.
5. Marcar projeto como ARQUIVADO, SUBSTITUIDO ou NAO_VALIDADO.
6. Só depois decidir se o repo pode ser congelado, mantido ou eliminado.
```

---

# Decisão estratégica

Os 12 grupos oficiais passam a ser a base de organização.

O God Mode deve usar este documento como mapa principal para:

- organizar repos;
- criar novos projetos;
- decidir onde guardar ideias;
- reaproveitar código antigo;
- montar documentação Obsidian;
- alimentar agentes IA;
- preparar builds;
- ligar produtos ao Oner Core.
