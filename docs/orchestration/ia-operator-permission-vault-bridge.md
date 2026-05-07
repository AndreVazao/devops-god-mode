# IA Operator Permission/Vault Bridge + First Autonomous Work Loop

## Objetivo

A Phase 206 liga diretamente o operador IA ao Permission Relay e ao Vault local.

O objetivo é arrancar o primeiro loop autónomo seguro:

```txt
Self Diagnosis
→ IA Work Packets
→ Vault reference binding
→ Mobile permission se faltar acesso
→ espera/offline resend se necessário
→ importação de nota/resposta
→ conversão em tarefas de revisão
```

## Endpoint principal

```txt
/api/ia-operator-bridge/package
```

## Página visual

```txt
/app/ia-operator-bridge
/app/first-autonomous-work-loop
```

## Endpoints

- `/api/ia-operator-bridge/status`
- `/api/ia-operator-bridge/policy`
- `/api/ia-operator-bridge/start-loop`
- `/api/ia-operator-bridge/bind-packet`
- `/api/ia-operator-bridge/continue-with-note`
- `/api/ia-operator-bridge/dashboard`
- `/api/ia-operator-bridge/package`

## O que faz

- Cria primeiro loop autónomo seguro.
- Executa self-diagnosis.
- Cria work session IA.
- Cria IA work packets a partir das lacunas.
- Procura referências no Vault local por provider/projeto.
- Se houver referência compatível, vincula o packet ao Vault.
- Se faltar acesso, cria permission request no Mobile Permission Relay.
- Deixa o PC em espera quando precisa de autorização/preenchimento.
- Importa nota/resposta capturada.
- Converte nota/resposta em tarefas de revisão.

## Segurança

- Não faz login privado automático.
- Não guarda material sensível fora do Vault local.
- Não faz chamadas pagas sem gate.
- Não aplica patches sem PR.
- Não faz merge/release/deploy sem aprovação do Oner.

## Estado real

Esta fase é a primeira ponte para o God Mode trabalhar enquanto o Oner está na rua.

O Oner pode abrir:

```txt
/app/ia-operator-bridge
```

E clicar em `Start first autonomous work loop`.

O PC cria packets e, se faltar acesso, envia popup para o telemóvel via:

```txt
/app/mobile-permission-relay
```

## Próximo passo

Depois desta fase, o próximo passo é criar a página/install flow final para o primeiro arranque real no PC:

```txt
Install → Open GodModeDesktop.exe → First Loop → Permissions/Vault → Work continues
```

## Workflow hygiene

Ao avançar para esta fase, o smoke antigo da Phase 205 deve ser apagado. Fica só:

- `.github/workflows/phase206-ia-operator-permission-vault-bridge-smoke.yml`

Além dos workflows globais/builds.
