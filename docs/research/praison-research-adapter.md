# Praison Research Adapter

## Decisão

Praison é útil para o God Mode, mas deve entrar como fonte de pesquisa/laboratório, não como dependência central imediata.

## Upstream

- Repo: `PraisonLabs/Praison`
- URL: https://github.com/PraisonLabs/Praison
- Licença: MIT
- Stack: Python-first, multi-agent, YAML, memory, RAG, Ollama, 100+ LLMs.

## Valor para o God Mode

Praison traz bons padrões para:

- YAML agent playbooks;
- workflows sequenciais, hierárquicos, paralelos e condicionais;
- agentes com memória curta/longa;
- RAG/custom knowledge;
- code interpreter agents;
- provider/model catalog;
- Ollama integration;
- no-code/auto commands.

## Política

- Não copiar para dentro do God Mode sem análise.
- Não adicionar Praison como dependência central por agora.
- Se for clonar, usar repo privado separado: `AndreVazao/godmode-praison-lab`.
- Extrair padrões primeiro, implementar nativo quando fizer sentido.
- Registar ideias úteis no Reusable Code Registry.

## O que entrou no God Mode

- Serviço: `backend/app/services/praison_research_adapter_service.py`
- Rota: `backend/app/routes/praison_research_adapter.py`

## Endpoints

- `GET/POST /api/praison-research/status`
- `GET/POST /api/praison-research/panel`
- `GET/POST /api/praison-research/rules`
- `GET/POST /api/praison-research/policy`
- `GET/POST /api/praison-research/mapping`
- `GET/POST /api/praison-research/extraction-plan`
- `GET/POST /api/praison-research/package`

## Próximo incremento recomendado

Phase 164 — Orchestration Playbooks v1:

- schema YAML/JSON de playbooks;
- validator;
- converter playbook → Real Orchestration Pipeline;
- templates para projetos reais;
- execução segura por gates.
