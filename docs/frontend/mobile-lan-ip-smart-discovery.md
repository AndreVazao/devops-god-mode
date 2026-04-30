# Mobile LAN IP Smart Discovery

## Problema encontrado no teste real

O operador escreveu `http://182.168.1.81:8000`, mas o IP correto do PC era `http://192.168.1.81:8000`.

O APK aceitou o endereço errado e mostrou o fallback offline.

## Objetivo

Melhorar a experiência mobile para redes locais:

- corrigir automaticamente `182.168.x.x` para `192.168.x.x`;
- testar primeiro o IP manual escrito pelo operador;
- pesquisar melhor os hosts próximos do IP do telemóvel;
- incluir hosts comuns como `.80`, `.81`, `.82`;
- explicar no fallback para confirmar `192.168.x.x`.

## Exemplo real

- PC: `192.168.1.81`
- Telemóvel: `192.168.1.67`
- Gateway: `192.168.1.254`

O Auto agora pesquisa também:

- `192.168.1.81`
- vizinhos de `192.168.1.67`
- gateway e hosts comuns da rede

## Segurança

- Não guarda credenciais.
- Não envia dados sensíveis.
- Só testa `/health` no backend local.
- Mantém fallback visual se não encontrar o PC.

## Resultado esperado

O operador pode escrever `192.168.1.81:8000` ou carregar em `Auto` e o APK tem mais hipóteses de encontrar o PC sem configuração manual perfeita.
