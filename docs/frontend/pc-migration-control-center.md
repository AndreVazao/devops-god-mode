# PC Migration Control Center

## Objetivo

A Phase 121 junta num painel único o primeiro arranque, instalação/configuração automática, backup portátil e restore.

A regra é simples: o God Mode deve configurar tudo sozinho sempre que for seguro inferir caminhos e defaults. Só deve parar quando a ação puder instalar software, sobrescrever ficheiros, pedir login manual ou mexer em dados sensíveis.

## Endpoints

- `GET/POST /api/pc-migration-control/status`
- `GET/POST /api/pc-migration-control/panel`
- `POST /api/pc-migration-control/auto-setup`
- `GET/POST /api/pc-migration-control/auto-mode`
- `GET/POST /api/pc-migration-control/latest`
- `GET/POST /api/pc-migration-control/package`

## Auto setup

Endpoint principal:

`POST /api/pc-migration-control/auto-setup`

O auto setup executa passos seguros automaticamente:

1. Check-up do PC.
2. Plano de ferramentas em falta.
3. Geração de script PowerShell de instalação/configuração.
4. Preparação da memória AndreOS/Obsidian.
5. Backup portátil.
6. Painel de próxima ação.

## O que é automático

- Detetar ferramentas instaladas.
- Identificar ferramentas em falta.
- Escolher modo PC fraco ou PC novo quando possível.
- Gerar script de instalação/configuração.
- Preparar memórias dos projetos.
- Criar backup portátil.
- Gerar próxima ação.

## Onde para para OK

O God Mode deve pedir aprovação quando for preciso:

- executar script que instala ferramentas;
- fazer login manual;
- restaurar backup;
- sobrescrever ficheiros;
- fazer rollback;
- mexer em dados sensíveis.

## Fluxo PC antigo

1. Executar auto setup.
2. Criar backup.
3. Copiar ZIP para pen/disco.
4. Levar para PC novo.

## Fluxo PC novo

1. Instalar God Mode.
2. Executar auto setup.
3. Rever/rodar script de ferramentas, se aprovado.
4. Fazer preview do backup.
5. Restaurar com frase de aprovação.
6. Fazer novo auto setup para validar ambiente.

## Modo PC fraco

- Instalar apenas ferramentas leves.
- Evitar insistir em Android Studio quebrado.
- Preferir GitHub Actions para builds pesados.
- Usar Obsidian/Markdown para memória.

## Modo PC novo

- Preparar ferramentas mais completas.
- Permitir Android SDK/ADB local se possível.
- Permitir IA local opcional se o PC aguentar.
- Continuar com gates para ações reais.
