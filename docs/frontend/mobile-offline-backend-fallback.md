# Mobile Offline Backend Fallback

## Objetivo

Quando o APK abre sem o backend/EXE do PC ativo, não deve mostrar o erro nativo do Android WebView.

A shell mobile passa a mostrar uma página própria do God Mode com:

- estado `APK OK`;
- aviso de que o cérebro corre no PC;
- instrução para abrir `GodModeDesktop.exe`;
- botão `Auto` para redescobrir o backend;
- campo para introduzir `http://IP_DO_PC:8000`;
- explicação de que `127.0.0.1` no telemóvel aponta para o próprio telemóvel.

## Comportamento esperado

1. APK abre.
2. Tenta descobrir o backend em `/health`.
3. Se encontrar, abre `/app/home`.
4. Se não encontrar, mostra fallback offline.
5. O operador pode tentar `Auto`, preencher IP manualmente ou aguardar até instalar/abrir o EXE no PC.

## Segurança

- Não guarda credenciais.
- Não tenta instalar nada.
- Não envia comandos offline.
- Só guarda a base URL do backend local.

## Resultado

O APK deixa de parecer quebrado antes do PC estar instalado e passa a guiar o operador até ao pairing real.
