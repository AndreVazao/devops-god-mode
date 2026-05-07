# LAN Connection Discovery

## Objetivo

A Phase 209 torna a descoberta do PC em casa mais robusta quando o DHCP muda o IP.

## Regras conhecidas

```txt
PC atual: 192.168.1.81
Telemóvel visto antes: 192.168.1.47
Sweep: 20 abaixo e 20 acima do .81
Range: 192.168.1.61 até 192.168.1.101
Porta: 8000
```

## Endpoint novo

```txt
/api/mobile-pc-pairing/lan-scan-candidates
```

## Manifest

O `connection_manifest` passa a incluir:

- `known_home_pc_ips`;
- `known_home_phone_ips`;
- `lan_sweep_base_ip`;
- `lan_sweep_radius`;
- `lan_sweep_range`;
- `lan_candidates`;
- `mobile_should_try_in_order`.

## Ordem de tentativa

O APK deve tentar:

1. `192.168.1.81` primeiro;
2. alternar perto do 81: 80, 82, 79, 83, etc.;
3. continuar até 61 e 101;
4. se nada responder, tentar endpoint remoto guardado;
5. guardar último endpoint funcional.

## Nota

O IP `192.168.1.47` é hint do telemóvel. Ele ajuda a confirmar a gama da rede, mas não deve ser tratado como backend do PC.

## Próxima camada

O APK deve consumir este manifest automaticamente e fazer auto-switch casa/rua.
