# Ecossistema AndreVazao — Grupos, Programas e Arquivo Reutilizável

Este documento organiza todos os projetos falados/criados em grupos empresariais mais fortes.

A regra principal é simples:

- O **God Mode** é o orquestrador central.
- Nenhum projeto antigo deve ser apagado sem antes ser arquivado.
- Programas que não avancem continuam úteis como banco de código, ideias, componentes, scripts, automações e experiências.
- O arquivo deve ser preparado para ser lido por IA, Obsidian e pelo próprio God Mode.

---

## 0. Núcleo central — God Mode / Orquestrador

O God Mode é o cérebro operacional do ecossistema.

Ele deve conseguir:

- gerir projetos;
- consultar memória persistente;
- ler documentação em Obsidian/GitHub;
- reaproveitar código arquivado;
- criar novas repos;
- modificar projetos existentes;
- controlar builds;
- controlar licenças;
- coordenar subprogramas;
- decidir que código antigo pode ser reaproveitado noutros produtos.

### Projetos dentro deste grupo

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
- Sistema de arquivo reutilizável de código
- Sistema de leitura de repositórios GitHub
- Sistema de automação de builds
- Sistema de gestão de `.env`
- Sistema de criação automática de repos
- Sistema de dashboard DevOps mobile-first

### Submódulos do God Mode

```txt
GodMode/
├── 00_CORE_ORQUESTRADOR/
├── 01_MEMORIA_OBSIDIAN/
├── 02_GITHUB_AUTOMATION/
├── 03_BUILD_CENTER/
├── 04_AGENTES_IA/
├── 05_ARQUIVO_CODIGO_REUTILIZAVEL/
├── 06_LICENCAS_E_ONER/
├── 07_DASHBOARD_WEB/
├── 08_MOBILE_CONTROL/
└── 09_LOGS_DECISOES_E_AUDITORIA/
```

---

## 1. Grupo Conteúdos — Veributo Studio

Nome de cabeçalho sugerido: **Veributo Studio**.

Este grupo junta tudo o que cria conteúdo, marcas, vídeos, ebooks, vozes, personagens, websites e publicação automática.

### Projetos dentro deste grupo

- Veributo Studio
- Baribudos Studio
- Baribudos Studio Primary
- Baribudos Studio Home Edition
- Baribudos Studio Website
- Website do estúdio
- VerbaForge
- ViralVazao
- Content Creator / Contentoria Heitor
- Persona Voz / Pé Só na Foz / módulo de vozes/personagens
- Translation + Lipsync Lab
- Tradutor de vídeo
- Sistema de dobragem automática
- Sistema de lipsync
- Coqui TTS / XTTS-v2
- Voice cloning
- Sistema de ebooks automáticos
- Sistema de cursos automáticos
- Sistema de vídeos automáticos
- Sistema de posts automáticos
- Sistema de deteção de tendências virais
- Sistema de patrocinadores/anúncios dentro dos conteúdos
- Sistema de publicação YouTube / Instagram / TikTok
- Sistema de aprovação manual para séries grandes
- Sistema autopilot para posts rápidos

### Estrutura sugerida

```txt
VeributoStudio/
├── 00_BRAND_E_WEBSITE/
│   ├── website/
│   └── landing-pages/
├── 01_VERBAFORGE/
│   ├── gerador-ebooks/
│   ├── gerador-videos/
│   ├── gerador-cursos/
│   └── publicador-redes/
├── 02_BARIBUDOS/
│   ├── historias/
│   ├── personagens/
│   ├── vozes/
│   ├── ilustracoes/
│   └── videos/
├── 03_VOZES_E_PERSONAS/
│   ├── voice-cloning/
│   ├── narradores/
│   └── personagens-recorrentes/
├── 04_TRADUCAO_LIPSYNC/
│   ├── tradutor-video/
│   ├── dobragem/
│   ├── legendas/
│   └── lipsync/
├── 05_CONTEUDO_SOCIAL/
│   ├── youtube/
│   ├── instagram/
│   ├── tiktok/
│   └── campanhas/
└── 99_ARQUIVO_CONTEUDOS/
```

### Regra de arquivo

Tudo o que for criado para conteúdo, mesmo que não avance, deve ir para:

```txt
VeributoStudio/99_ARQUIVO_CONTEUDOS/
```

---

## 2. Grupo Mecânica — ECU, Swap e Engenharia Automóvel

Este grupo junta ferramentas para carros, diagnóstico, reprogramação, peças, desenhos técnicos e futuros sistemas de oficina/engenharia.

### Projetos dentro deste grupo

- ECU Pro Tune
- Diagnóstico OBD2
- Reprogramação ECU
- Konnwei ELM327 v1.5
- Sistema de backup automático da ECU
- Sistema de presets de performance
- Sistema de limites seguros
- Sistema de relatório de anomalias
- Sistema de PDF com assinatura do cliente
- Sistema por matrícula/veículo
- SwapAI / Swap Engine Designer
- Desenho de apoios de motor
- Sistema para trocas de motor
- Sistema para medir e desenhar suportes/adaptadores
- Sistema CAD para peças automóveis
- Sistema de compatibilidade motor/chassis
- Sistema futuro para oficina/mecânica
- Sistema futuro com drones/scanner/fotogrametria para captar medidas

### Estrutura sugerida

```txt
Mecanica/
├── 00_ECU_PRO_TUNE/
│   ├── diagnostico-obd2/
│   ├── reprogramacao-ecu/
│   ├── backups-ecu/
│   ├── presets-performance/
│   └── relatorios-cliente/
├── 01_SWAP_AI/
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

### Nota de segurança

Projetos de ECU e alterações mecânicas devem guardar sempre:

- backup original;
- limites seguros;
- relatório de alterações;
- consentimento do cliente;
- separação entre modo diagnóstico e modo alteração.

---

## 3. Grupo Maquinário — CNC, Laser, DXF, Produção

Este grupo junta tudo o que transforma desenhos, imagens, texto ou medidas em ficheiros para máquinas.

### Projetos dentro deste grupo

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
- Gerador de ficheiros para corte laser/vinil
- Sistema de camadas CUT_OUTER, CUT_INNER, ENGRAVE, MARK_TEXT, BEND_REF

### Estrutura sugerida

```txt
Maquinario/
├── 00_GCODE_CONVERTER/
│   ├── svg-to-gcode/
│   ├── dxf-to-gcode/
│   ├── image-to-gcode/
│   ├── pdf-to-gcode/
│   └── txt-to-gcode/
├── 01_DXF_GENERATORS/
│   ├── botoneiras/
│   ├── chapas/
│   ├── suportes/
│   └── templates/
├── 02_CNC_LASER_PREVIEW/
│   ├── preview-2d/
│   ├── simulador-caminho/
│   └── configuracoes-maquina/
├── 03_EXPORTADORES/
│   ├── gcode/
│   ├── dxf/
│   ├── svg/
│   ├── stl/
│   └── step/
└── 99_ARQUIVO_MAQUINARIO/
```

### Relação com outros grupos

Este grupo serve também:

- ProVentil, para chapas e botoneiras;
- Mecânica, para apoios de motor e peças;
- Conteúdos, para produtos físicos, placas, brindes e merchandising.

---

## 4. Grupo ProVentil — Negócio Real / Obras / Orçamentos

Este grupo fica separado porque é negócio operacional real.

### Projetos dentro deste grupo

- ProVentil
- proventil.pt
- Sistema de extração de fumos
- Sistema de ventilação hotelaria
- Sistema de videoporteiros
- Sistema Comelit
- Sistema Fermax
- Sistema BTicino
- Sistema de propostas por marca
- Sistema de orçamentos automáticos
- Sistema de deslocações por distância
- Sistema de materiais e fornecedores
- Sistema ClimaStore
- Sistema de ID por obra/morada
- Sistema de histórico técnico por edifício
- Sistema de faltosos
- Sistema de revisitas
- Sistema de comissões técnicas
- Sistema de stock
- Sistema de PDFs/orçamentos/propostas
- Sistema de chapas e botoneiras com DXF

### Estrutura sugerida

```txt
ProVentil/
├── 00_CORE_NEGOCIO/
├── 01_CLIENTES_OBRAS_MORADAS/
├── 02_ORCAMENTOS_PROPOSTAS/
├── 03_VIDEO_PORTEIROS/
│   ├── comelit/
│   ├── fermax/
│   └── bticino/
├── 04_EXTRACAO_FUMOS/
│   ├── motores/
│   ├── tubos/
│   ├── curvas/
│   ├── filtros/
│   └── fornecedores/
├── 05_DESLOCACOES_E_TECNICOS/
├── 06_DXF_CHAPAS_BOTONEIRAS/
├── 07_COMISSOES/
└── 99_ARQUIVO_PROVENTIL/
```

---

## 5. Grupo Bots / Jogos / Automação

Este grupo fica separado do God Mode.

O God Mode orquestra, mas os bots vivem aqui como produtos próprios.

### Projetos dentro deste grupo

- Bot Factory
- Engenharia Reversa Framework
- BOT_<nome do jogo>
- PC Farm Lords Mobile
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
- Bots Android
- Bots PC

### Estrutura sugerida

```txt
BotsJogos/
├── 00_BOT_FACTORY/
├── 01_REVERSE_ENGINEERING/
├── 02_LORDS_MOBILE/
│   ├── pc-farm/
│   ├── headless-real/
│   ├── emulator-fallback/
│   ├── comandos-chat/
│   ├── rally-dn-war/
│   └── dashboard-instancias/
├── 03_BOTS_ANDROID/
├── 04_BOTS_PC/
├── 05_LICENCAS_BOTS/
└── 99_ARQUIVO_BOTS_JOGOS/
```

---

## 6. Grupo Mobile / Android / Overlay / OS

Este grupo junta apps móveis, overlays e ideias de sistema operativo leve.

### Projetos dentro deste grupo

- Script Reviewer Mobile
- App Android com botões flutuantes
- Overlay sobre outras apps
- Sistema para falar com várias IAs em simultâneo
- Sistema para criar/alterar repos pelo telemóvel
- Sistema Expo/Android com permissões de overlay
- AndreOS
- OS Universal para Telemóveis
- Sistema operativo ultra-leve para jogos
- Instalador PC que prepara o telemóvel
- Sistema de deteção automática de hardware
- Sistema de drivers
- Sistema controlado por ADB

### Estrutura sugerida

```txt
MobileAndroid/
├── 00_SCRIPT_REVIEWER_MOBILE/
├── 01_FLOATING_OVERLAY_AI/
├── 02_ANDROID_AUTOMATION/
├── 03_ANDREOS/
├── 04_ADB_CONTROL/
└── 99_ARQUIVO_MOBILE/
```

---

## 7. Grupo Dados / Licenças / Oner

Este grupo é transversal. Não é produto final único; é infraestrutura de monetização e controlo.

### Projetos dentro deste grupo

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
- Sistema de aprovação de alterações por botão aceitar

### Estrutura sugerida

```txt
OnerCore/
├── 00_AUTH_USERS/
├── 01_LICENCAS/
├── 02_PAGAMENTOS/
├── 03_PLANOS_E_PRECOS/
├── 04_PERMISSOES_CHECKBOXES/
├── 05_ADMIN_EMPREGADOS/
├── 06_COMISSOES_BONUS/
├── 07_AUDITORIA/
└── 99_ARQUIVO_ONER/
```

---

## 8. Grupo SheetPro / Escalas / PDFs

Este grupo fica dedicado a análise de PDFs, escalas, chapas e serviços.

### Projetos dentro deste grupo

- SheetProPrivate
- Programa para verificar escalas
- Sistema de análise de chapas
- Sistema de análise de PDFs de serviços
- Sistema de base de dados de rotas
- Sistema de atualização de chapas
- Sistema horário verão/inverno
- Sistema horário escolar/não escolar
- Sistema de deteção de novas rotas
- Sistema de comparação de alterações

### Estrutura sugerida

```txt
SheetPro/
├── 00_IMPORTADOR_PDFS/
├── 01_ANALISADOR_CHAPAS/
├── 02_BASE_ROTAS_SERVICOS/
├── 03_COMPARADOR_ALTERACOES/
├── 04_VALIDADOR_ESCALAS/
└── 99_ARQUIVO_SHEETPRO/
```

---

# Arquivo geral reutilizável

Este é o ponto crítico.

Tudo o que nasceu antes e pode não avançar deve ser preservado num arquivo de reaproveitamento.

O objetivo não é manter projetos mortos. O objetivo é guardar peças úteis.

## Estrutura geral recomendada

```txt
ArquivoCodigoReutilizavel/
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
└── 99_CEMITERIO_CONTROLADO/
    ├── projetos-parados/
    ├── ideias-congeladas/
    ├── experiencias/
    └── codigo-nao-validado/
```

## Regras do arquivo

Cada script guardado deve ter um ficheiro `.meta.md` com:

```txt
Nome:
Projeto original:
Grupo:
Linguagem:
Framework:
Estado:
Serve para:
Pode ser reutilizado em:
Riscos:
Dependências:
Última revisão:
```

## Estados possíveis

```txt
ATIVO
ARQUIVADO_UTIL
EXPERIENCIA
SUBSTITUIDO
NAO_VALIDADO
PERIGOSO_NAO_USAR_SEM_REVISAO
```

---

# Mapa final dos grupos

```txt
ECOSSISTEMA_ANDREVAZAO/
├── 00_GOD_MODE_ORQUESTRADOR/
├── 01_VERIBUTO_STUDIO_CONTEUDOS/
├── 02_MECANICA_ECU_SWAP_AUTO/
├── 03_MAQUINARIO_CNC_DXF_GCODE/
├── 04_PROVENTIL_NEGOCIO_REAL/
├── 05_BOTS_JOGOS_AUTOMACAO/
├── 06_MOBILE_ANDROID_OVERLAY_OS/
├── 07_ONER_CORE_LICENCAS_DADOS/
├── 08_SHEETPRO_ESCALAS_PDFS/
└── 99_ARQUIVO_CODIGO_REUTILIZAVEL/
```

---

# Prioridade estratégica

## Prioridade 1

- God Mode
- AndreOS Memory / Obsidian Memory
- Arquivo Código Reutilizável
- GitHub Auto Builder / Build Center

## Prioridade 2

- Veributo Studio
- VerbaForge
- Baribudos Studio
- Translation + Lipsync Lab

## Prioridade 3

- ProVentil
- Maquinário/CNC/DXF
- Mecânica/ECU/SwapAI

## Prioridade 4

- Bots/Jogos
- Mobile Overlay
- SheetPro

---

# Decisão arquitetural

O God Mode não deve conter todos os projetos fisicamente dentro dele.

O God Mode deve conter:

- índice dos projetos;
- ponte para cada repo;
- memória Obsidian;
- arquivo de código reutilizável;
- automações de leitura/build/deploy;
- agentes que entendem o que cada projeto faz.

Os projetos devem continuar separados por produto/grupo, mas ligados por índice central.

---

# Próximo passo recomendado

Criar os seguintes ficheiros/pastas:

```txt
docs/arquitetura/ECOSSISTEMA_ANDREVAZAO_GRUPOS_E_ARQUIVO.md
docs/arquivo-codigo/README.md
docs/arquivo-codigo/catalogo-geral.md
docs/arquivo-codigo/template-meta-script.md
docs/obsidian/estrutura-vault-andrevazao.md
```
