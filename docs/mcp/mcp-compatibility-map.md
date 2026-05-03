# MCP Compatibility Map

## Objetivo

Preparar o God Mode para expor endpoints internos como tools compatíveis com MCP/agents no futuro, sem ainda adicionar dependência MCP pesada.

## Decisão

Esta fase cria um mapa de compatibilidade, não um servidor MCP real.

## O que entra

- Serviço: `backend/app/services/mcp_compatibility_map_service.py`
- Rota: `backend/app/routes/mcp_compatibility_map.py`
- Home com botão `MCP Tools`
- Manifest exportável via `/api/mcp-compatibility/manifest`

## Endpoints

- `GET/POST /api/mcp-compatibility/status`
- `GET/POST /api/mcp-compatibility/panel`
- `GET/POST /api/mcp-compatibility/rules`
- `GET /api/mcp-compatibility/tools`
- `GET /api/mcp-compatibility/tools/{tool_id}`
- `GET /api/mcp-compatibility/manifest`
- `POST /api/mcp-compatibility/validate-tool`
- `GET/POST /api/mcp-compatibility/package`

## Tools iniciais mapeadas

- `godmode.goal_planner.plan`
- `godmode.agent_roles.assign`
- `godmode.provider_router.route`
- `godmode.security.prepare_ai_handoff`
- `godmode.reusable_code.search`
- `godmode.ecosystem.classify`
- `godmode.andreos.context_panel`
- `godmode.obsidian.prepare_sync`
- `godmode.ruflo.mapping`
- `godmode.home.health`
- `godmode.release.final_readiness`

## Riscos

- `low`: leitura, planeamento, classificação ou análise sem alteração destrutiva.
- `medium`: pode preparar alterações, syncs ou contexto sensível; exige guardrails.
- `high`: pode alterar repo, memória estável, update ou release; exige aprovação clara.
- `critical`: ação destrutiva, credenciais, pagamentos, licenças ou eliminação; bloqueado sem aprovação explícita do Oner.

## Regras

- Tools low podem ser chamadas por IA para leitura/planeamento.
- Tools medium exigem Security Guard quando lidam com contexto sensível.
- Tools high/critical exigem aprovação explícita do Oner.
- Nenhuma tool MCP pode receber ou devolver secrets brutos.
- O manifesto não expõe credenciais internas.

## Próxima evolução

- Criar servidor MCP real opcional.
- Criar autenticação local para tools.
- Criar permissões por role/tool.
- Ligar Tool Manifest ao Provider Router e Agent Roles.
