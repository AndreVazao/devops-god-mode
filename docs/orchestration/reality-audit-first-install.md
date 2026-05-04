# Reality Audit + First Real Install Mission

## Objetivo

A Phase 179 impede o God Mode de parecer mais poderoso do que é.

Ela separa cada capacidade em:

- `real`: implementada e validada por backend/CI;
- `partial`: contrato/módulo existe, mas precisa runtime real no PC;
- `planned`: política/roadmap existe, execução real ainda não;
- `blocked`: não funciona até instalar/configurar dependência.

## Endpoints

- `GET/POST /api/god-mode-reality-audit/status`
- `GET/POST /api/god-mode-reality-audit/audit`
- `GET/POST /api/god-mode-reality-audit/capabilities`
- `GET/POST /api/god-mode-reality-audit/first-install-mission`
- `GET/POST /api/god-mode-reality-audit/project-tree-and-inventory-mission`
- `GET/POST /api/god-mode-reality-audit/package`

## Veredito honesto atual

Real:

- backend;
- Windows/Android builds;
- cockpit `/app/home`;
- logs/histórico de botões;
- tree oficial;
- registry de módulos;
- inventário manual/staged de conversas.

Parcial/bloqueado até PC real:

- listagem/leitura automática de conversas em providers externos;
- browser worker real;
- sessão/login reutilizável;
- execução completa em projeto real.

Planeado:

- vault local cifrado completo;
- self-update staged com rollback completo.

## Primeira missão no PC

1. Instalar/abrir Windows EXE.
2. Confirmar `/health` e `/app/home`.
3. Abrir o cockpit no telemóvel via IP LAN do PC.
4. Validar `/api/module-registry-snapshot/summary`.
5. Validar `docs/project-tree/GOD_MODE_TREE.md`.
6. Adicionar/stage primeiras conversas IA manualmente.
7. Instalar/validar Playwright se for usar browser real.
8. Fazer login manual em providers escolhidos.
9. Tentar ler snapshot visível de conversa.
10. Executar uma ação low-risk aprovada com prova/rollback.

## Regra dura

Nenhuma capacidade de browser/provider pode ser considerada 100% real enquanto não passar no PC real com sessão/login controlado pelo operador.
