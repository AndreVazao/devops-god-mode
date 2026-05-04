# First Install Download Center + PC Proof Checklist UI

## Objetivo

A Phase 181 cria um centro único para a primeira instalação real do God Mode no PC.

A página operacional é:

```txt
/api/first-install-pc-proof-center/app
```

O package JSON é:

```txt
/api/first-install-pc-proof-center/package
```

## O que agrega

- artifacts Windows/APK;
- checklist de primeira instalação;
- comandos provider proof;
- estado de Playwright/proofs;
- estado de tree oficial;
- module registry;
- reality audit;
- download/install center.

## Fluxo amanhã no PC

1. Abrir GitHub Actions.
2. Descarregar artifact Windows `godmode-windows-exe`.
3. Executar o EXE no PC.
4. Abrir `/app/home`.
5. Abrir `/api/first-install-pc-proof-center/app`.
6. Descarregar/instalar APK se necessário.
7. Confirmar tree e module registry.
8. Instalar Playwright se necessário.
9. Executar provider proof para ChatGPT/Gemini/Claude/Perplexity.
10. Fazer login manual.
11. Importar proof JSON para inventário.
12. Só depois executar primeira ação low-risk aprovada.

## Endpoints

- `/api/first-install-pc-proof-center/status`
- `/api/first-install-pc-proof-center/artifacts`
- `/api/first-install-pc-proof-center/commands`
- `/api/first-install-pc-proof-center/checklist`
- `/api/first-install-pc-proof-center/cards`
- `/api/first-install-pc-proof-center/package`
- `/api/first-install-pc-proof-center/app`

## Segurança

- Não guarda credenciais.
- Não executa envio/deleção/cleanup de conversas.
- Provider proof exige login manual.
- O painel apenas organiza comandos, checklist e links.
- Ações de risco continuam dependentes dos gates próprios.
