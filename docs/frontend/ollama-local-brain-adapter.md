# Ollama Local Brain Adapter

## Objetivo

Integrar o Ollama instalado no PC como cérebro local auxiliar do God Mode.

O Ollama passa a servir para tarefas privadas, rápidas e offline, sem substituir o ChatGPT ou outros providers externos quando for preciso mais capacidade.

## Endpoints

- `GET/POST /api/ollama-local-brain/status`
- `GET/POST /api/ollama-local-brain/panel`
- `GET/POST /api/ollama-local-brain/policy`
- `GET/POST /api/ollama-local-brain/use-cases`
- `GET /api/ollama-local-brain/health`
- `GET /api/ollama-local-brain/models`
- `POST /api/ollama-local-brain/benchmark-light`
- `POST /api/ollama-local-brain/auto-select`
- `GET /api/ollama-local-brain/route-decision`
- `POST /api/ollama-local-brain/generate`
- `GET/POST /api/ollama-local-brain/package`

## Home / Modo Fácil

Foi adicionado o botão:

- `IA Local` → `/api/ollama-local-brain/panel`

Foi adicionado o comando rápido:

- `open_ollama_local_brain`

## Funções

- Detetar se Ollama está acessível em `http://127.0.0.1:11434`.
- Listar modelos instalados.
- Identificar modelos leves, de código e provavelmente pesados.
- Fazer benchmark leve.
- Selecionar automaticamente o melhor modelo que funciona.
- Guardar o modelo selecionado em `data/ollama_local_brain_adapter.json`.
- Decidir quando usar Ollama ou providers externos.

## Uso recomendado

Ollama deve ser usado para:

- resumir conversas antigas localmente;
- limpar contexto antes de enviar para providers externos;
- criar primeiras versões de prompts;
- preparar `MEMORY_DELTA`;
- sugerir próximos passos offline;
- revisão leve de código;
- fallback quando não houver internet.

## Uso não recomendado

Não usar Ollama como fonte final para:

- decisões críticas sem validação;
- código final complexo sem testes;
- ações destrutivas;
- substituir providers externos quando for preciso alta qualidade.

## Política de PC velho vs PC novo

No PC velho, o God Mode deve preferir modelos leves como `gemma2:2b`.

No PC novo, o God Mode deve voltar a correr `auto-select` e promover modelos maiores se passarem no benchmark.

## Segurança

- Não enviar credenciais para modelos locais.
- Não guardar tokens nem passwords.
- Tratar respostas do Ollama como rascunho/recomendação.
- Validar tudo pelo God Mode antes de executar.
