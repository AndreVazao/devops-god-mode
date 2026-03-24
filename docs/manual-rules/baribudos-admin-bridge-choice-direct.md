# Baribudos Admin Bridge Choice — Direct Studio to Website

## Decisão

Foi escolhida a opção **1 — ponte direta Studio -> Website**.

## Justificação

- O **DevOps God Mode** é um ecossistema de reparação, alinhamento e governação de sistemas.
- O **Baribudos Studio** é um ecossistema independente.
- O **Baribudos Studio** é quem manda no **Baribudos Website**.
- Portanto, o Website deve ser controlado diretamente pelo Studio, e não através do God Mode.

## Papel do God Mode neste caso

O God Mode deve:
- observar;
- diagnosticar;
- alinhar;
- reparar;
- monitorizar;
- sugerir melhorias;
- validar contratos e impactos.

O God Mode **não é** o command bus primário do ecossistema Baribudos.

## Papel do Studio neste caso

O Studio é o command plane principal do Baribudos Ecosystem.

O Studio deve falar diretamente com o Website para:
- publicar;
- despublicar;
- atualizar catálogo;
- gerir visibilidade;
- gerir preços;
- gerir admins;
- pedir resumos comerciais;
- disparar sync;
- reprocessar publicações.

## Arquitetura resultante

### Control Plane
- `baribudos-studio`

### Public Execution Plane
- `baribudos-studio-website`

### Support / Oversight Plane
- `devops-god-mode`

## Regras

- `studio_is_primary_control_plane = true`
- `website_is_public_execution_plane = true`
- `god_mode_is_observer_and_repair_orchestrator = true`
- `admin_bridge_direction = STUDIO_TO_WEBSITE_DIRECT`
- `god_mode_is_not_primary_command_bus_for_baribudos = true`
