# First Real Run Checklist

## Objetivo

A Phase 142 cria a checklist prática para a primeira execução real do God Mode depois de instalar EXE e APK.

Esta camada responde:

> Já posso começar a usar o God Mode no dia a dia?

## Endpoints

- `GET/POST /api/first-real-run/status`
- `GET/POST /api/first-real-run/panel`
- `POST /api/first-real-run/start`
- `POST /api/first-real-run/step`
- `POST /api/first-real-run/progress`
- `POST /api/first-real-run/complete`
- `GET/POST /api/first-real-run/latest`
- `GET/POST /api/first-real-run/package`

## Checklist

1. Confirmar gate final verde.
2. Baixar EXE e APK.
3. Executar GodModeDesktop.exe no PC.
4. Instalar/abrir APK no telemóvel.
5. Emparelhar APK ao PC.
6. Abrir Home / Modo Fácil.
7. Rodar smoke local de primeira execução.
8. Testar envio/receção de ficheiro pequeno.
9. Criar primeiro job real controlado.
10. Dar primeiro comando real curto.
11. Confirmar pronto para uso diário.

## Resultado

O serviço calcula:

- passos obrigatórios concluídos;
- percentagem;
- blockers;
- próximo passo;
- `ready_for_daily_use`.

## Segurança

- Não mexe em projetos reais sozinho.
- Apenas guia e regista evidência leve.
- Redige chaves sensíveis em evidências.
- Permite override do operador, mas só fica marcado como override.
