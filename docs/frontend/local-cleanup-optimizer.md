# Local Cleanup Optimizer

## Objetivo

A Phase 127 adiciona limpeza/otimização local segura para PCs antigos ou novos.

O caso principal inicial é limpar modelos Ollama que não funcionam ou estão a ocupar espaço, mantendo modelos úteis como:

- `gemma2:2b`
- `qwen2.5:7b`

Também prepara revisão de ajustes Windows, mas sem desativar nada crítico automaticamente.

## Endpoints

- `GET/POST /api/local-cleanup/status`
- `GET/POST /api/local-cleanup/panel`
- `GET/POST /api/local-cleanup/policy`
- `GET/POST /api/local-cleanup/scan`
- `POST /api/local-cleanup/plan`
- `POST /api/local-cleanup/script`
- `POST /api/local-cleanup/apply-safe`
- `GET/POST /api/local-cleanup/latest`
- `GET/POST /api/local-cleanup/package`

## Ollama

O scan usa:

`ollama list`

O plano separa modelos em:

- manter;
- remover se estiverem marcados como quebrados;
- rever se não estiverem na lista de manter.

A remoção usa alvo exato:

`ollama rm <modelo>`

Sem wildcards.

## Windows

A fase pode sugerir revisão de:

- apps de arranque;
- overlays não usados;
- indexação excessiva;
- sincronizações pesadas.

Mas nunca desativa automaticamente:

- Windows Update;
- Defender/Security Center;
- Firewall;
- rede;
- drivers;
- instalador Windows;
- autenticação/perfis;
- backup/restore.

## Aprovação

Aplicar limpeza segura exige frase:

`OPTIMIZE LOCAL PC`

## Segurança

- não remove modelos sem alvo exato;
- não usa wildcards;
- não desativa serviços críticos;
- alterações Windows ficam como revisão/script;
- caches locais ficam em allowlist;
- tudo fica registado em `data/local_cleanup_optimizer.json`.

## Uso recomendado

1. `scan`
2. `plan` com lista de modelos a manter e modelos quebrados
3. `script` para rever comandos
4. `apply-safe` apenas se for para remover modelos marcados como quebrados
